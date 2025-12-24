# app/converter/ai_service.py
"""AI service for converting screenshots to code."""

import base64
import io
import json
import logging
import time
from typing import Dict, Optional, Tuple

from openai import OpenAI
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
            try:
                self.openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        
        # Initialize Anthropic client (only if valid key)
        if Config.ANTHROPIC_API_KEY and not Config.ANTHROPIC_API_KEY.startswith('sk-ant-your-'):
            try:
                self.anthropic_client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
                logger.info("Anthropic client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {str(e)}")
    
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
                model = Config.AI_MODEL or 'gpt-4o'
            
            # Make AI request
            start_time = time.time()
            
            # Check if we have any AI service available
            has_ai_service = (
                (model.startswith('gpt-') and self.openai_client) or
                (model.startswith('claude-') and self.anthropic_client) or
                self.openai_client  # fallback to OpenAI
            )
            
            if not has_ai_service:
                logger.warning("No AI service configured - generating demo code based on image properties")
                # Still process the image to extract properties for better demo
                image_properties = self._analyze_image_properties(image_path)
                demo_code = self._generate_demo_code(framework, css_framework, image_properties)
                result = {
                    'content': f"Demo mode - {framework.title()} component generated (AI service not configured)",
                    'tokens_used': 0,
                    'is_demo': True
                }
                parsed_code = demo_code
            else:
                try:
                    if model.startswith('gpt-') and self.openai_client:
                        result = self._call_openai(prompt, processed_image, model)
                    elif model.startswith('claude-') and self.anthropic_client:
                        result = self._call_anthropic(prompt, processed_image, model)
                    else:
                        # Fallback to OpenAI if available
                        if self.openai_client:
                            result = self._call_openai(prompt, processed_image, 'gpt-4o')
                        else:
                            raise Exception("No AI service available")
                    
                    if 'error' in result:
                        raise Exception(f"AI service error: {result['error']}")
                        
                    # Parse AI response if successful
                    parsed_code = self._parse_ai_response(result['content'], framework)
                    result['is_demo'] = False
                        
                except Exception as e:
                    logger.info(f"AI service failed ({str(e)}), falling back to demo mode")
                    # Generate demo code as fallback, but still use image properties
                    image_properties = self._analyze_image_properties(image_path)
                    demo_code = self._generate_demo_code(framework, css_framework, image_properties)
                    result = {
                        'content': f"Demo mode - {framework.title()} component generated (AI service failed: {str(e)})",
                        'tokens_used': 0,
                        'is_demo': True
                    }
                    parsed_code = demo_code
            
            processing_time = time.time() - start_time
            
            return {
                'html': parsed_code.get('html', ''),
                'css': parsed_code.get('css', ''),
                'js': parsed_code.get('js', ''),
                'framework': framework,
                'css_framework': css_framework,
                'processing_time': processing_time,
                'tokens_used': result.get('tokens_used', 0),
                'model_used': model,
                'is_demo': result.get('is_demo', False),
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
    
    def _analyze_image_properties(self, image_path: str) -> Dict[str, any]:
        """
        Analyze image properties to create better demo code.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing image properties
        """
        properties = {
            'width': 800,
            'height': 600,
            'aspect_ratio': 'landscape',
            'dominant_colors': ['blue', 'white'],
            'is_mobile': False,
            'layout_type': 'landing'
        }
        
        try:
            with Image.open(image_path) as img:
                # Basic dimensions
                properties['width'] = img.size[0]
                properties['height'] = img.size[1]
                
                # Aspect ratio
                if img.size[0] > img.size[1]:
                    properties['aspect_ratio'] = 'landscape'
                elif img.size[0] < img.size[1]:
                    properties['aspect_ratio'] = 'portrait'
                else:
                    properties['aspect_ratio'] = 'square'
                
                # Mobile detection (rough heuristic)
                properties['is_mobile'] = img.size[0] < 500 and img.size[1] > img.size[0]
                
                # Try to extract dominant colors (simplified)
                try:
                    # Convert to RGB if necessary
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Sample colors from different parts of the image
                    colors = []
                    for y in [img.size[1]//4, img.size[1]//2, 3*img.size[1]//4]:
                        for x in [img.size[0]//4, img.size[0]//2, 3*img.size[0]//4]:
                            if x < img.size[0] and y < img.size[1]:
                                pixel = img.getpixel((x, y))
                                colors.append(pixel)
                    
                    # Simplified color analysis - just categorize as warm/cool
                    warm_count = 0
                    cool_count = 0
                    for r, g, b in colors:
                        if r > b and r > g:
                            warm_count += 1
                        elif b > r and b > g:
                            cool_count += 1
                    
                    if warm_count > cool_count:
                        properties['dominant_colors'] = ['red', 'orange', 'yellow']
                    else:
                        properties['dominant_colors'] = ['blue', 'green', 'purple']
                        
                except Exception:
                    # Keep defaults
                    pass
                
                logger.info(f"Image analysis for {image_path}: {properties}")
                
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {str(e)}")
        
        return properties
    
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
            response = self.openai_client.chat.completions.create(
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
    
    def _generate_demo_code(self, framework: str, css_framework: str, image_properties: Dict[str, any] = None) -> Dict[str, str]:
        """
        Generate realistic demo code when AI service is unavailable.
        
        Args:
            framework: Target framework
            css_framework: CSS framework
            image_properties: Properties extracted from the uploaded image
            
        Returns:
            Dict containing demo HTML, CSS, and JS code
        """
        
        # Use image properties to customize the demo
        if not image_properties:
            image_properties = {
                'aspect_ratio': 'landscape',
                'is_mobile': False,
                'dominant_colors': ['blue', 'white']
            }
        
        # Determine if this should be a mobile-first design
        is_mobile_design = image_properties.get('is_mobile', False)
        colors = image_properties.get('dominant_colors', ['blue', 'white'])
        primary_color = colors[0] if colors else 'blue'
        
        demo_templates = {
            'react': {
                'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>React Landing Page</title>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        function LandingPage() {
          return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
              {/* Header */}
              <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                  <div className="flex justify-between items-center py-6">
                    <div className="flex items-center">
                      <h1 className="text-2xl font-bold text-gray-900">
                        Your App
                      </h1>
                    </div>
                    <nav className="hidden md:flex space-x-8">
                      <a href="#" className="text-gray-600 hover:text-gray-900">Home</a>
                      <a href="#" className="text-gray-600 hover:text-gray-900">About</a>
                      <a href="#" className="text-gray-600 hover:text-gray-900">Services</a>
                      <a href="#" className="text-gray-600 hover:text-gray-900">Contact</a>
                    </nav>
                    <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 btn-primary">
                      Get Started
                    </button>
                  </div>
                </div>
              </header>

              {/* Hero Section */}
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                <div className="text-center">
                  <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                    Build Amazing
                    <span className="text-blue-600 block">Digital Experiences</span>
                  </h2>
                  <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                    Transform your ideas into stunning websites and applications with our 
                    powerful tools and expert guidance.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold btn-primary">
                      Start Building
                    </button>
                    <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-50 text-lg font-semibold">
                      Learn More
                    </button>
                  </div>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8 mt-16">
                  <div className="text-center p-6 feature-card">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Fast & Efficient</h3>
                    <p className="text-gray-600">Lightning-fast performance that scales with your needs.</p>
                  </div>
                  
                  <div className="text-center p-6 feature-card">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">Reliable</h3>
                    <p className="text-gray-600">Built with industry best practices for maximum reliability.</p>
                  </div>
                  
                  <div className="text-center p-6 feature-card">
                    <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold mb-2">User-Friendly</h3>
                    <p className="text-gray-600">Intuitive design that puts user experience first.</p>
                  </div>
                </div>
              </main>
            </div>
          );
        }

        // Render the component
        ReactDOM.render(<LandingPage />, document.getElementById('root'));
    </script>
</body>
</html>''',
                'css': '''/* Additional custom styles for React component */
.hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  transition: all 0.2s ease-in-out;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }
}''',
                'js': '''// Interactive functionality for React component
import { useState, useEffect } from 'react';

export function useScrollEffect() {
  const [scrollY, setScrollY] = useState(0);
  
  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);
  
  return scrollY;
}

// Animation utilities
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6 }
};

// Form validation
export function validateEmail(email) {
  const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return re.test(String(email).toLowerCase());
}'''
            },
            'vue': {
                'html': '''<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center py-6">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">
              Your App
            </h1>
          </div>
          <nav class="hidden md:flex space-x-8">
            <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">Services</a>
            <a href="#" class="text-gray-600 hover:text-gray-900">Contact</a>
          </nav>
          <button 
            class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            @click="getStarted"
          >
            Get Started
          </button>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div class="text-center">
        <h2 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Build Amazing
          <span class="text-blue-600 block">Digital Experiences</span>
        </h2>
        <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Transform your ideas into stunning websites and applications with our 
          powerful tools and expert guidance.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <button 
            class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold"
            @click="startBuilding"
          >
            Start Building
          </button>
          <button 
            class="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-50 text-lg font-semibold"
            @click="learnMore"
          >
            Learn More
          </button>
        </div>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-3 gap-8 mt-16">
        <div 
          v-for="feature in features" 
          :key="feature.id"
          class="text-center p-6 card-hover"
        >
          <div :class="'w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ' + feature.bgColor">
            <component :is="feature.icon" :class="'w-8 h-8 ' + feature.iconColor" />
          </div>
          <h3 class="text-xl font-semibold mb-2">{{ feature.title }}</h3>
          <p class="text-gray-600">{{ feature.description }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LandingPage',
  setup() {
    const features = ref([
      {
        id: 1,
        title: 'Fast & Efficient',
        description: 'Lightning-fast performance that scales with your needs.',
        bgColor: 'bg-blue-100',
        iconColor: 'text-blue-600',
        icon: 'IconBolt'
      },
      {
        id: 2,
        title: 'Reliable',
        description: 'Built with industry best practices for maximum reliability.',
        bgColor: 'bg-green-100',
        iconColor: 'text-green-600',
        icon: 'IconCheck'
      },
      {
        id: 3,
        title: 'User-Friendly',
        description: 'Intuitive design that puts user experience first.',
        bgColor: 'bg-purple-100',
        iconColor: 'text-purple-600',
        icon: 'IconHeart'
      }
    ])

    const getStarted = () => {
      console.log('Get started clicked')
    }

    const startBuilding = () => {
      console.log('Start building clicked')
    }

    const learnMore = () => {
      console.log('Learn more clicked')
    }

    return {
      features,
      getStarted,
      startBuilding,
      learnMore
    }
  }
}
</script>''',
                'css': '''<style scoped>
.card-hover {
  transition: all 0.3s ease;
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.hero-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

button {
  transition: all 0.2s ease-in-out;
}

button:hover {
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  h2 {
    font-size: 2.5rem;
  }
}
</style>''',
                'js': '''// Vue 3 Composition API utilities
import { ref, onMounted, onUnmounted } from 'vue'

export function useScrollPosition() {
  const y = ref(0)
  
  const updateScrollPosition = () => {
    y.value = window.scrollY
  }
  
  onMounted(() => {
    window.addEventListener('scroll', updateScrollPosition)
  })
  
  onUnmounted(() => {
    window.removeEventListener('scroll', updateScrollPosition)
  })
  
  return { y }
}

// Form validation composable
export function useFormValidation() {
  const errors = ref({})
  
  const validateEmail = (email) => {
    const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return re.test(String(email).toLowerCase())
  }
  
  const validateRequired = (value) => {
    return value && value.toString().trim().length > 0
  }
  
  return {
    errors,
    validateEmail,
    validateRequired
  }
}'''
            },
            'html': {
                'html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Landing Page</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles.css">
</head>
<body class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-6">
                <div class="flex items-center">
                    <h1 class="text-2xl font-bold text-gray-900">
                        Your App
                    </h1>
                </div>
                <nav class="hidden md:flex space-x-8">
                    <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
                    <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
                    <a href="#" class="text-gray-600 hover:text-gray-900">Services</a>
                    <a href="#" class="text-gray-600 hover:text-gray-900">Contact</a>
                </nav>
                <button class="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 btn-primary">
                    Get Started
                </button>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div class="text-center">
            <h2 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
                Build Amazing
                <span class="text-blue-600 block">Digital Experiences</span>
            </h2>
            <p class="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Transform your ideas into stunning websites and applications with our 
                powerful tools and expert guidance.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold btn-primary">
                    Start Building
                </button>
                <button class="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-50 text-lg font-semibold">
                    Learn More
                </button>
            </div>
        </div>

        <!-- Features Grid -->
        <div class="grid md:grid-cols-3 gap-8 mt-16">
            <div class="text-center p-6 feature-card">
                <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold mb-2">Fast & Efficient</h3>
                <p class="text-gray-600">Lightning-fast performance that scales with your needs.</p>
            </div>
            
            <div class="text-center p-6 feature-card">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold mb-2">Reliable</h3>
                <p class="text-gray-600">Built with industry best practices for maximum reliability.</p>
            </div>
            
            <div class="text-center p-6 feature-card">
                <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                </div>
                <h3 class="text-xl font-semibold mb-2">User-Friendly</h3>
                <p class="text-gray-600">Intuitive design that puts user experience first.</p>
            </div>
        </div>
    </main>

    <script src="script.js"></script>
</body>
</html>''',
                'css': '''/* Custom styles for landing page */
.hero-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-primary {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    transition: all 0.2s ease-in-out;
}

.btn-primary:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 130, 246, 0.4);
}

.feature-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.feature-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .feature-card {
        margin-bottom: 1rem;
    }
}

/* Loading animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Fade in animation */
.fade-in {
    opacity: 0;
    transform: translateY(20px);
    animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}''',
                'js': '''// Interactive functionality for landing page
document.addEventListener('DOMContentLoaded', function() {
    console.log('Landing page loaded successfully!');
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Button click handlers
    const getStartedBtn = document.querySelector('header button');
    const startBuildingBtn = document.querySelector('main button:first-of-type');
    const learnMoreBtn = document.querySelector('main button:last-of-type');
    
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function() {
            alert('Get Started clicked! This would redirect to sign up.');
            console.log('Get started button clicked');
        });
    }
    
    if (startBuildingBtn) {
        startBuildingBtn.addEventListener('click', function() {
            alert('Start Building clicked! This would show the builder interface.');
            console.log('Start building button clicked');
        });
    }
    
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', function() {
            alert('Learn More clicked! This would show additional information.');
            console.log('Learn more button clicked');
        });
    }
    
    // Feature cards hover effect enhancement
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.background = 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.background = '';
        });
    });
    
    // Scroll animations
    function animateOnScroll() {
        const elements = document.querySelectorAll('.feature-card');
        elements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight * 0.8) {
                element.classList.add('fade-in');
            }
        });
    }
    
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Run on page load
    
    // Form validation function
    function validateEmail(email) {
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    }
    
    // Expose utility functions to global scope
    window.utils = {
        validateEmail,
        showLoading: function(element) {
            element.innerHTML = '<span class="loading"></span> Loading...';
        },
        hideLoading: function(element, originalText) {
            element.innerHTML = originalText;
        }
    };
});'''
            }
        }
        
        # Default to HTML if framework not found
        if framework not in demo_templates:
            framework = 'html'
        
        template = demo_templates[framework]
        
        # Adjust CSS based on css_framework
        css_adjustments = {
            'bootstrap': '''
/* Bootstrap-specific overrides */
.hero-section {
    background: linear-gradient(135deg, #007bff 0%, #6610f2 100%);
}

.btn-custom {
    border-radius: 25px;
    padding: 12px 24px;
}

.card-custom {
    border: none;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
''',
            'tailwind': template['css'],  # Use default CSS for Tailwind
            'css': template['css'].replace('Tailwind', 'CSS')  # Generic CSS version
        }
        
        return {
            'html': template['html'],
            'css': css_adjustments.get(css_framework, template['css']),
            'js': template['js']
        }
