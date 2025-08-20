import re
from typing import List, Tuple
from core.config import settings
from utils.validators import validate_formula


def parse_formula(formula: str) -> List[Tuple[str, int]]:
    """
    Parse a chemical formula into its constituent elements and counts.
    
    Args:
        formula (str): Chemical formula to parse
        
    Returns:
        List[Tuple[str, int]]: List of (element, count) tuples
        
    Raises:
        ValueError: If formula format is invalid
    """
    try:
        tokens = re.findall(r'[A-Z][a-z]?|\d+|\(|\)', formula)
        if not tokens:
            raise ValueError(f"Invalid formula format: {formula}")
        
        stack = [[]]
        i = 0

        while i < len(tokens):
            token = tokens[i]
            i += 1  # Always increment i after accessing tokens[i]

            if token == '(':
                stack.append([])
            elif token == ')':
                if len(stack) <= 1:
                    raise ValueError(f"Unbalanced parentheses in formula: {formula}")
                    
                group = stack.pop()
                
                # Check for a multiplier after the closing parenthesis
                if i < len(tokens) and tokens[i].isdigit():
                    multiplier = int(tokens[i])
                    i += 1
                else:
                    multiplier = 1
                    
                # Apply the multiplier to all elements in the group
                for elem, count in group:
                    stack[-1].append((elem, count * multiplier))
            elif re.match(r'[A-Z][a-z]?', token):
                element = token
                
                # Check for a count after the element
                if i < len(tokens) and tokens[i].isdigit():
                    count = int(tokens[i])
                    i += 1
                else:
                    count = 1
                    
                stack[-1].append((element, count))
            elif token.isdigit():
                # This handles cases where we have a digit without a preceding element
                raise ValueError(f"Unexpected number in formula: {formula} at position {i-1}")
            else:
                # This should not happen with our regex pattern
                raise ValueError(f"Invalid token in formula: {token}")

        # Check for unbalanced parentheses
        if len(stack) != 1:
            raise ValueError(f"Unbalanced parentheses in formula: {formula}")
            
        return stack[0]  # Returns a list of (element, count) pairs from the top-level group
    except Exception as e:
        # Catch any other unexpected errors and provide a clear message
        print(f"Error parsing formula '{formula}': {str(e)}")
        raise ValueError(f"Error parsing formula: {str(e)}")

## ========================================================================================

def calculate_molar_mass(formula: str) -> float:
    """
    Calculate the molar mass of a chemical formula.
    
    Args:
        formula (str): Chemical formula
        
    Returns:
        float: Calculated molar mass in g/mol
        
    Raises:
        ValueError: If formula contains unknown elements
    """
    # Validate formula first
    validate_formula(formula)
    
    parsed = parse_formula(formula)
    total_mass = 0
    
    for element, count in parsed:
        if element not in settings.atomic_masses:
            raise ValueError(f"Unknown element: {element}")
        total_mass += settings.atomic_masses[element] * count
    
    return total_mass