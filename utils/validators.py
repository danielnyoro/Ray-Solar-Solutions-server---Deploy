import re
from email_validator import validate_email as email_validator, EmailNotValidError

def validate_email(email):
    """Validate email format"""
    try:
        # Use check_deliverability=False to allow test domains
        email_validator(email, check_deliverability=False)
        return True
    except EmailNotValidError:
        return False

def validate_password(password):
    """Validate password meets requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    return True, None

def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True, None
    
    # Remove spaces, dashes, and parentheses
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits, optional + at start)
    if re.match(r'^\+?\d{10,15}$', clean_phone):
        return True, None
    
    return False, "Invalid phone number format"

def validate_role(role):
    """Validate user role"""
    allowed_roles = ['customer', 'provider', 'admin']
    if role.lower() in allowed_roles:
        return True, None
    return False, f"Role must be one of: {', '.join(allowed_roles)}"
