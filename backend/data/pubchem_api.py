import requests
from typing import Dict, Optional
import time


def get_chemical_properties(formula: str) -> Dict[str, Optional[str]]:
    # Initialize empty properties dict
    properties = {
        "boiling_point": None,
        "melting_point": None,
        "density": None,
        "state_at_room_temp": None,
        "iupac_name": None,
        "hazard_classification": None,
        "structure_image_url": None,
        "structure_image_svg_url": None,
        "compound_url": None
    }
    
    try:
        # First, get the compound ID from the formula
        search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/formula/{formula}/cids/JSON"
        
        response = requests.get(search_url, timeout=10)
        if response.status_code != 200:
            print(f"PubChem search failed for formula {formula}: {response.status_code}")
            return properties
        
        search_data = response.json()
        if 'IdentifierList' not in search_data or 'CID' not in search_data['IdentifierList']:
            print(f"No compound found for formula {formula}")
            return properties
        
        # Get the first CID (compound ID)
        cid = search_data['IdentifierList']['CID'][0]
        
        # Add a small delay to be respectful to the API
        time.sleep(0.1)
        
        # Get detailed compound information
        compound_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
        
        response = requests.get(compound_url, timeout=10)
        if response.status_code == 200:
            compound_data = response.json()
            if 'PropertyTable' in compound_data and 'Properties' in compound_data['PropertyTable']:
                prop = compound_data['PropertyTable']['Properties'][0]
                properties['iupac_name'] = prop.get('IUPACName')
        
        # Add structure image URLs
        properties['structure_image_url'] = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        properties['structure_image_svg_url'] = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SVG"
        properties['compound_url'] = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
        
        # Try to get additional properties like melting point, boiling point, etc.
        time.sleep(0.1)  # Be respectful to the API
        
        experimental_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{cid}/JSON"
        
        response = requests.get(experimental_url, timeout=15)
        if response.status_code == 200:
            try:
                exp_data = response.json()
                
                # Navigate through the complex JSON structure to find experimental properties
                if 'Record' in exp_data:
                    record = exp_data['Record']
                    if 'Section' in record:
                        for section in record['Section']:
                            _extract_properties_from_section(section, properties)
                            
            except Exception as e:
                print(f"Error parsing experimental data for {formula}: {str(e)}")
        
        print(f"Successfully fetched properties for {formula} (CID: {cid})")
        
    except requests.exceptions.Timeout:
        print(f"PubChem API timeout for formula {formula}")
    except requests.exceptions.RequestException as e:
        print(f"PubChem API request failed for formula {formula}: {str(e)}")
    except Exception as e:
        print(f"Unexpected error fetching properties for {formula}: {str(e)}")
    
    return properties


def _extract_properties_from_section(section: Dict, properties: Dict[str, Optional[str]]) -> None:
    # Check section title for relevant properties
    if 'TOCHeading' in section:
        heading = section['TOCHeading'].lower()
        
        # Look for physical and chemical properties
        if any(keyword in heading for keyword in ['physical', 'chemical', 'experimental']):
            if 'Section' in section:
                for subsection in section['Section']:
                    _extract_properties_from_section(subsection, properties)
            
            # Extract information from this section
            if 'Information' in section:
                for info in section['Information']:
                    if 'Name' in info and 'Value' in info:
                        name = info['Name'].lower()
                        
                        # Extract string values from the Value structure
                        value = _extract_value_string(info['Value'])
                        
                        if value:
                            if 'boiling point' in name:
                                properties['boiling_point'] = value
                            elif 'melting point' in name:
                                properties['melting_point'] = value
                            elif 'density' in name:
                                properties['density'] = value
                            elif 'physical state' in name or 'state' in name:
                                properties['state_at_room_temp'] = value
                            elif 'hazard' in name or 'safety' in name or 'toxicity' in name:
                                properties['hazard_classification'] = value


def _extract_value_string(value_data) -> Optional[str]:
    if isinstance(value_data, dict):
        if 'StringWithMarkup' in value_data:
            for item in value_data['StringWithMarkup']:
                if 'String' in item:
                    return item['String']
        elif 'Number' in value_data:
            return str(value_data['Number'][0]) if isinstance(value_data['Number'], list) else str(value_data['Number'])
    elif isinstance(value_data, list):
        for item in value_data:
            result = _extract_value_string(item)
            if result:
                return result
    
    return None