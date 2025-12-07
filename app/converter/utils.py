# app/converter/utils.py
"""Converter utility functions."""

import os
import uuid
from typing import Optional, Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from PIL import Image
import logging

from config import Config

logger = logging.getLogger(__name__)


def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the file
        
    Returns:
        True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def validate_image_file(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if not file.filename:
        return False, "No filename provided"
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Supported formats: {', '.join(Config.ALLOWED_EXTENSIONS)}"
    
    # Check file size (Flask already handles MAX_CONTENT_LENGTH)
    try:
        # Read file to validate it's a real image
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        if len(file_content) == 0:
            return False, "File is empty"
        
        # Try to open with PIL to validate image format
        try:
            image = Image.open(file)
            image.verify()  # Verify it's a valid image
            file.seek(0)  # Reset file pointer after verification
            
            # Check image dimensions (minimum and maximum)
            width, height = image.size
            if width < 100 or height < 100:
                return False, "Image too small. Minimum size is 100x100 pixels"
            
            if width > 4096 or height > 4096:
                return False, "Image too large. Maximum size is 4096x4096 pixels"
                
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"
    
    return True, None


def save_uploaded_file(file: FileStorage, conversion_uuid: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Save uploaded file to storage.
    
    Args:
        file: Uploaded file object
        conversion_uuid: UUID for the conversion
        
    Returns:
        Tuple of (success, file_path, error_message)
    """
    try:
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        new_filename = f"{conversion_uuid}.{file_extension}"
        
        # Create upload directory if it doesn't exist
        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # Validate saved file
        if not os.path.exists(file_path):
            return False, None, "Failed to save file"
        
        return True, file_path, None
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        return False, None, f"Error saving file: {str(e)}"


def process_image_for_ai(image_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Process image for AI consumption.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (success, processed_path, error_message)
    """
    try:
        # Open and process image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
                # Save processed image
                processed_path = image_path.replace('.', '_processed.')
                img.save(processed_path, 'PNG', quality=95)
                return True, processed_path, None
            else:
                # Image is already in RGB format
                return True, image_path, None
                
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {str(e)}")
        return False, None, f"Error processing image: {str(e)}"


def cleanup_temp_files(file_paths: list) -> None:
    """
    Clean up temporary files.
    
    Args:
        file_paths: List of file paths to delete
    """
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up file {file_path}: {str(e)}")


def generate_preview_html(html_code: str, css_code: str, js_code: str) -> str:
    """
    Generate complete HTML preview with embedded CSS and JS.
    
    Args:
        html_code: HTML code
        css_code: CSS code
        js_code: JavaScript code
        
    Returns:
        Complete HTML document string
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview</title>
    <style>
        /* Reset styles */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
        }}
        
        /* Generated CSS */
        {css_code}
    </style>
</head>
<body>
    {html_code}
    
    <script>
        {js_code}
    </script>
</body>
</html>"""


def extract_framework_specific_code(code: str, framework: str) -> str:
    """
    Extract framework-specific code from generated content.
    
    Args:
        code: Generated code
        framework: Target framework
        
    Returns:
        Cleaned framework-specific code
    """
    if framework == 'react':
        # Ensure React component is properly formatted
        if 'export default' not in code and 'function' in code:
            # Wrap in proper component structure
            component_name = 'GeneratedComponent'
            if 'function' in code:
                return code
            else:
                return f"""export default function {component_name}() {{
    return (
        {code}
    );
}}"""
    
    elif framework == 'vue':
        # Ensure Vue component structure
        if '<template>' not in code:
            return f"""<template>
    {code}
</template>

<script setup>
// Add your Vue component logic here
</script>

<style scoped>
/* Add your component styles here */
</style>"""
    
    return code


def validate_generated_code(html_code: str, css_code: str, js_code: str) -> Tuple[bool, Optional[str]]:
    """
    Basic validation of generated code.
    
    Args:
        html_code: HTML code to validate
        css_code: CSS code to validate
        js_code: JavaScript code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Basic HTML validation
        if html_code:
            # Check for balanced tags (basic check)
            open_tags = html_code.count('<')
            close_tags = html_code.count('>')
            if open_tags != close_tags:
                return False, "HTML appears to have unbalanced tags"
        
        # Basic CSS validation
        if css_code:
            # Check for balanced braces
            open_braces = css_code.count('{')
            close_braces = css_code.count('}')
            if open_braces != close_braces:
                return False, "CSS appears to have unbalanced braces"
        
        # Basic JS validation (very basic)
        if js_code:
            # Check for balanced parentheses and braces
            open_parens = js_code.count('(')
            close_parens = js_code.count(')')
            open_braces = js_code.count('{')
            close_braces = js_code.count('}')
            
            if open_parens != close_parens:
                return False, "JavaScript appears to have unbalanced parentheses"
            if open_braces != close_braces:
                return False, "JavaScript appears to have unbalanced braces"
        
        return True, None
        
    except Exception as e:
        return False, f"Code validation error: {str(e)}"


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in MB.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)
    except Exception:
        return 0.0


def create_download_package(html_code: str, css_code: str, js_code: str, conversion_uuid: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Create a downloadable package with all generated files.
    
    Args:
        html_code: Generated HTML
        css_code: Generated CSS
        js_code: Generated JavaScript
        conversion_uuid: UUID for the conversion
        
    Returns:
        Tuple of (success, zip_path, error_message)
    """
    import zipfile
    import tempfile
    
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Write files
        files_created = []
        
        if html_code:
            html_path = os.path.join(temp_dir, 'index.html')
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_code)
            files_created.append(('index.html', html_path))
        
        if css_code:
            css_path = os.path.join(temp_dir, 'styles.css')
            with open(css_path, 'w', encoding='utf-8') as f:
                f.write(css_code)
            files_created.append(('styles.css', css_path))
        
        if js_code:
            js_path = os.path.join(temp_dir, 'script.js')
            with open(js_path, 'w', encoding='utf-8') as f:
                f.write(js_code)
            files_created.append(('script.js', js_path))
        
        # Create ZIP file
        zip_path = os.path.join(Config.UPLOAD_FOLDER, f"{conversion_uuid}_code.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, filepath in files_created:
                zipf.write(filepath, filename)
        
        # Cleanup temp files
        for _, filepath in files_created:
            try:
                os.remove(filepath)
            except:
                pass
        
        try:
            os.rmdir(temp_dir)
        except:
            pass
        
        return True, zip_path, None
        
    except Exception as e:
        logger.error(f"Error creating download package: {str(e)}")
        return False, None, f"Error creating download package: {str(e)}"
