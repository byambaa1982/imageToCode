# app/converter/ai_service.py
"""AI service for converting screenshots to code."""

import base64
import io
import json
import logging
import time
from typing import Dict, Optional, Tuple

import openai
from anthropic import Anthropic
from PIL import Image

from config import Config

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered code generation from screenshots."""
    
    def __init__(self):
        """Initialize AI service with API clients."""
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI client
        if Config.OPENAI_API_KEY:
            openai.api_key = Config.OPENAI_API_KEY
            self.openai_client = openai
        
        # Initialize Anthropic client
        if Config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    def convert_screenshot_to_code(
        self,
        image_path: str,
        framework: str = 'react',
        css_framework: str = 'tailwind',
        model: str = None
    ) -> Dict[str, any]:
        """
        Convert a screenshot to code using AI.
        
        Args:
            image_path: Path to the image file
            framework: Target framework (react, vue, html, etc.)
            css_framework: CSS framework (tailwind, bootstrap, css, etc.)
            model: AI model to use (optional)
            
        Returns:
            Dict containing generated code and metadata
        """
        try:
            # Process image
            processed_image = self._process_image(image_path)
            if not processed_image:
                return {'error': 'Failed to process image'}
            
            # Generate prompt
            prompt = self._generate_prompt(framework, css_framework)
            
            # Choose model
            if not model:
                model = Config.AI_MODEL or 'gpt-4-vision-preview'
            
            # Make AI request
            start_time = time.time()
            
            if model.startswith('gpt-') and self.openai_client:
                result = self._call_openai(prompt, processed_image, model)
            elif model.startswith('claude-') and self.anthropic_client:
                result = self._call_anthropic(prompt, processed_image, model)
            else:
                # Fallback to OpenAI if available
                if self.openai_client:
                    result = self._call_openai(prompt, processed_image, 'gpt-4-vision-preview')
                else:
                    return {'error': 'No AI service available'}
            
            processing_time = time.time() - start_time
            
            if 'error' in result:
                return result
            
            # Parse response and extract code
            parsed_code = self._parse_ai_response(result['content'], framework)
            
            return {
                'html': parsed_code.get('html', ''),
                'css': parsed_code.get('css', ''),
                'js': parsed_code.get('js', ''),
                'framework': framework,
                'css_framework': css_framework,
                'processing_time': processing_time,
                'tokens_used': result.get('tokens_used', 0),
                'model_used': model,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error in AI conversion: {str(e)}")
            return {'error': f'AI conversion failed: {str(e)}', 'success': False}
    
    def _process_image(self, image_path: str) -> Optional[str]:
        """
        Process image for AI consumption.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string or None if failed
        """
        try:
            # Open and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for most AI models)
                max_size = (1024, 1024)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                return image_base64
                
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return None
    
    def _generate_prompt(self, framework: str, css_framework: str) -> str:
        """
        Generate AI prompt based on framework and CSS framework.
        
        Args:
            framework: Target framework
            css_framework: CSS framework
            
        Returns:
            Formatted prompt string
        """
        base_prompt = """You are an expert frontend developer. Please convert this UI screenshot into clean, production-ready code.

REQUIREMENTS:
1. Generate semantic, accessible HTML with proper structure
2. Use modern, responsive CSS that works on all devices
3. Include hover effects and interactive states where appropriate
4. Write clean, commented code following best practices
5. Ensure the design is pixel-perfect to the screenshot
6. Use proper semantic HTML tags (header, nav, main, section, etc.)
7. Include alt text for images and proper ARIA labels

"""
        
        framework_prompts = {
            'react': """TARGET: React component using JSX
- Create a functional React component
- Use modern React hooks if needed
- Include PropTypes or TypeScript interfaces
- Use className instead of class
- Follow React best practices
- Export as default component

""",
            'vue': """TARGET: Vue.js component
- Create a Vue 3 component using Composition API
- Use proper Vue template syntax
- Include script setup if applicable
- Follow Vue best practices
- Use proper v-bind and v-on directives

""",
            'html': """TARGET: Static HTML/CSS/JavaScript
- Create clean HTML5 document structure
- Include proper DOCTYPE and meta tags
- Use semantic HTML elements
- Add vanilla JavaScript for interactivity if needed

""",
            'svelte': """TARGET: Svelte component
- Create a Svelte component file
- Use Svelte's reactive syntax
- Include proper script and style blocks
- Follow Svelte best practices

"""
        }
        
        css_framework_prompts = {
            'tailwind': """CSS FRAMEWORK: Tailwind CSS
- Use Tailwind utility classes exclusively
- Implement responsive design with Tailwind breakpoints (sm:, md:, lg:, xl:)
- Use Tailwind's color palette and spacing system
- Include hover: and focus: states
- Use flexbox and grid utilities for layout
- Avoid custom CSS unless absolutely necessary

""",
            'bootstrap': """CSS FRAMEWORK: Bootstrap 5
- Use Bootstrap 5 classes and components
- Implement responsive design with Bootstrap grid
- Use Bootstrap utilities for spacing, colors, etc.
- Include Bootstrap component classes where appropriate
- Use Bootstrap's responsive breakpoints

""",
            'css': """CSS FRAMEWORK: Custom CSS
- Write clean, modern CSS from scratch
- Use CSS Grid and Flexbox for layout
- Implement responsive design with media queries
- Use CSS custom properties (variables)
- Follow BEM methodology for class naming
- Include smooth transitions and animations

""",
            'material': """CSS FRAMEWORK: Material Design
- Use Material Design principles and components
- Implement Material elevation and shadows
- Use Material color system
- Include Material typography scale
- Add Material ripple effects and animations

"""
        }
        
        output_format = """OUTPUT FORMAT:
Please provide the code in the following format:

```html
<!-- HTML code here -->
```

```css
/* CSS code here */
```

```javascript
// JavaScript code here (if needed)
```

Make sure to:
- Match the visual design exactly
- Use proper indentation and formatting
- Include comments explaining complex sections
- Ensure code is production-ready
- Test that the code would work in a real application

"""
        
        return (
            base_prompt +
            framework_prompts.get(framework, framework_prompts['html']) +
            css_framework_prompts.get(css_framework, css_framework_prompts['css']) +
            output_format
        )
    
    def _call_openai(self, prompt: str, image_base64: str, model: str) -> Dict[str, any]:
        """
        Call OpenAI API for code generation.
        
        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image
            model: Model name
            
        Returns:
            API response with content and metadata
        """
        try:
            response = self.openai_client.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return {
                'content': response.choices[0].message.content,
                'tokens_used': response.usage.total_tokens,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return {'error': f'OpenAI API error: {str(e)}'}
    
    def _call_anthropic(self, prompt: str, image_base64: str, model: str) -> Dict[str, any]:
        """
        Call Anthropic API for code generation.
        
        Args:
            prompt: Text prompt
            image_base64: Base64 encoded image
            model: Model name
            
        Returns:
            API response with content and metadata
        """
        try:
            message = self.anthropic_client.messages.create(
                model=model or "claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": image_base64
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }
                ]
            )
            
            return {
                'content': message.content[0].text,
                'tokens_used': message.usage.input_tokens + message.usage.output_tokens,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return {'error': f'Anthropic API error: {str(e)}'}
    
    def _parse_ai_response(self, content: str, framework: str) -> Dict[str, str]:
        """
        Parse AI response to extract code blocks.
        
        Args:
            content: Raw AI response content
            framework: Target framework
            
        Returns:
            Dict with html, css, js code blocks
        """
        result = {'html': '', 'css': '', 'js': ''}
        
        try:
            # Extract code blocks using simple parsing
            lines = content.split('\n')
            current_block = None
            current_code = []
            
            for line in lines:
                # Check for code block start
                if line.strip().startswith('```'):
                    if current_block:
                        # End of current block
                        result[current_block] = '\n'.join(current_code)
                        current_block = None
                        current_code = []
                    else:
                        # Start of new block
                        if 'html' in line.lower() or 'jsx' in line.lower():
                            current_block = 'html'
                        elif 'css' in line.lower():
                            current_block = 'css'
                        elif 'javascript' in line.lower() or 'js' in line.lower():
                            current_block = 'js'
                        else:
                            # Default to HTML for unmarked blocks
                            current_block = 'html'
                        current_code = []
                elif current_block:
                    current_code.append(line)
            
            # Handle case where last block doesn't have closing ```
            if current_block and current_code:
                result[current_block] = '\n'.join(current_code)
            
            # If no code blocks found, try to extract from content directly
            if not any(result.values()):
                result['html'] = content.strip()
            
            # Clean up and validate code
            for key in result:
                result[key] = self._clean_code(result[key], key, framework)
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            result['html'] = content.strip()
        
        return result
    
    def _clean_code(self, code: str, code_type: str, framework: str) -> str:
        """
        Clean and validate generated code.
        
        Args:
            code: Raw code string
            code_type: Type of code (html, css, js)
            framework: Target framework
            
        Returns:
            Cleaned code string
        """
        if not code.strip():
            return ''
        
        # Remove common AI artifacts
        code = code.strip()
        
        # Remove markdown artifacts
        code = code.replace('```html', '').replace('```css', '').replace('```javascript', '').replace('```', '')
        
        # Basic validation and cleanup based on type
        if code_type == 'html':
            # Ensure proper HTML structure
            if framework == 'react' and not code.strip().startswith('<'):
                # Wrap React components properly
                if 'function' not in code.lower() and 'const' not in code.lower():
                    code = f"export default function Component() {{\n  return (\n{code}\n  );\n}}"
        
        return code.strip()
