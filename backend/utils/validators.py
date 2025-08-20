import re

def validate_formula(formula: str) -> str:
    """
    Validate chemical formula format.
    
    Args:
        formula (str): Chemical formula to validate
        
    Returns:
        str: Validated formula
        
    Raises:
        ValueError: If formula format is invalid
    """
    # Basic validation to catch obvious errors
    if not formula or not re.match(r'^[A-Za-z0-9\(\)]+$', formula):
        raise ValueError(f"Invalid formula format: {formula}")
    

    # Check for balanced parentheses
    stack = []
    for char in formula:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                raise ValueError(f"Unbalanced parentheses in formula: {formula}")
            stack.pop()
    
    if stack:
        raise ValueError(f"Unbalanced parentheses in formula: {formula}")
    
    return formula

# Example usage:
# print(validate_formula("H2O"))        # OK
# print(validate_formula("C6H12O6"))    # OK
# print(validate_formula("Na(Cl)2"))    # OK
# print(validate_formula("H2(O"))       # Fehler: Unbalanced parentheses
# print(validate_formula("NaCl!"))      # Fehler: Invalid formula format
