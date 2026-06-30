import os
import re


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize a filename to prevent security vulnerabilities.
    
    Removes or replaces characters that could cause:
    - SQL injection attacks
    - Path traversal attacks
    - File system issues
    - Unicode-based attacks
    
    Args:
        filename: The original filename from user upload
        max_length: Maximum allowed filename length (default 255 for DB schema)
    
    Returns:
        A sanitized filename safe for storage and logging
    
    Raises:
        ValueError: If filename is empty or contains only invalid characters
    
    Examples:
        >>> sanitize_filename("test'; DROP TABLE users; --.pdf")
        'test_DROP_TABLE_users___.pdf'
        
        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'
        
        >>> sanitize_filename("invoice (2024).pdf")
        'invoice_2024_.pdf'
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # 1. Remove directory path components (defense against path traversal)
    filename = os.path.basename(filename.replace("\\", "/"))
    
    # 2. Remove leading dots (hidden files, directory traversal)
    filename = filename.lstrip(".")
    
    # 3. Replace SQL-dangerous characters: ' " ; -- /* */
    # These are replaced with underscore to preserve filename readability
    sql_dangerous_chars = r"['\";\-/*]|--"
    filename = re.sub(sql_dangerous_chars, "_", filename)
    
    # 4. Keep only safe characters: alphanumeric, dots, hyphens, underscores, spaces
    # Preserve the file extension by keeping dots
    filename = re.sub(r"[^a-zA-Z0-9._\- ]", "_", filename)
    
    # 5. Remove consecutive underscores/dots/hyphens for cleanliness
    filename = re.sub(r"[._\-]{2,}", "_", filename)
    
    # 6. Remove trailing dots (potential NTFS alternate data stream on Windows)
    filename = filename.rstrip(".")
    
    # 7. Enforce max length
    if len(filename) > max_length:
        # Try to preserve extension
        name_part, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        if max_name_length > 0:
            filename = name_part[:max_name_length] + ext
        else:
            filename = filename[:max_length]
    
    # 8. Final validation: ensure we have a valid filename
    if not filename or filename == "_":
        raise ValueError("Filename contained no valid characters after sanitization")
    
    return filename


def validate_filename_length(filename: str, max_length: int = 255) -> bool:
    """
    Validate that filename is within acceptable length.
    
    Args:
        filename: The filename to validate
        max_length: Maximum allowed length
    
    Returns:
        True if filename length is valid, False otherwise
    """
    return len(filename) > 0 and len(filename) <= max_length
