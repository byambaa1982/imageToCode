# Test AI Service Demo Code Generation

from app.converter.ai_service import AIService

# Test the AI service directly
ai_service = AIService()

# Test React demo generation
print("Testing React demo generation...")
result = ai_service.convert_screenshot_to_code(
    image_path="/tmp/test.png",  # dummy path
    framework="react",
    css_framework="tailwind"
)

print("Success:", result.get('success'))
print("HTML length:", len(result.get('html', '')))
print("CSS length:", len(result.get('css', '')))  
print("JS length:", len(result.get('js', '')))

print("\nHTML contains key elements:")
html_content = result.get('html', '')
print("- DOCTYPE:", 'DOCTYPE' in html_content)
print("- React CDN:", 'unpkg.com/react' in html_content)
print("- Babel:", 'babel' in html_content)
print("- Root div:", 'id="root"' in html_content)

print("\nHTML Preview (first 300 chars):")
print(html_content[:300] + "..." if len(html_content) > 300 else html_content)
