# app/converter/prompts.py
"""Optimized AI prompts for code generation."""

# Base system prompt for all conversions
BASE_SYSTEM_PROMPT = """You are an expert frontend developer specializing in converting UI screenshots to production-ready code.

Your task is to analyze the provided screenshot and generate clean, modern, accessible, and responsive code.

Key requirements:
1. **Accurate Recreation**: Match the layout, colors, typography, and spacing as closely as possible
2. **Semantic HTML**: Use proper HTML5 semantic elements
3. **Accessibility**: Include ARIA labels, alt text, and keyboard navigation support
4. **Responsive Design**: Make the layout work on mobile, tablet, and desktop
5. **Modern Practices**: Use current best practices for the chosen framework
6. **Clean Code**: Write readable, well-organized, and commented code
7. **Performance**: Optimize for fast loading and rendering

Output format:
- Return ONLY the code, no explanations
- Use code blocks with proper language tags
- Include HTML, CSS, and JavaScript separately
"""


# Framework-specific prompts
FRAMEWORK_PROMPTS = {
    'react': """
Generate a React component using modern React patterns:

- Use functional components with hooks
- Implement proper prop types or TypeScript interfaces
- Use React best practices (useState, useEffect, etc.)
- Include comments for complex logic
- Export the component as default

Structure:
```jsx
// Component code here
import React, { useState, useEffect } from 'react';

const ComponentName = () => {
  // Component logic
  
  return (
    // JSX here
  );
};

export default ComponentName;
```

Additional CSS:
```css
/* Component styles */
```

Additional JavaScript (if needed):
```javascript
/* Helper functions or utilities */
```
""",
    
    'vue': """
Generate a Vue 3 component using Composition API:

- Use <script setup> syntax
- Implement reactive data with ref() and reactive()
- Use Vue 3 best practices
- Include proper template structure
- Add scoped styles

Structure:
```vue
<template>
  <!-- Template code here -->
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

// Component logic
</script>

<style scoped>
/* Component styles */
</style>
```
""",
    
    'html': """
Generate clean HTML, CSS, and JavaScript:

- Use semantic HTML5 elements
- Create external CSS in a <style> block
- Add vanilla JavaScript for interactivity
- Ensure cross-browser compatibility
- Include responsive meta tags

Structure:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Component</title>
    <style>
        /* CSS here */
    </style>
</head>
<body>
    <!-- HTML here -->
    
    <script>
        // JavaScript here
    </script>
</body>
</html>
```
""",
    
    'svelte': """
Generate a Svelte 4 component:

- Use Svelte's reactive declarations ($:)
- Implement proper event handling
- Use Svelte stores if needed
- Include scoped styles
- Follow Svelte best practices

Structure:
```svelte
<script>
  // Component logic
  import { writable } from 'svelte/store';
</script>

<!-- HTML template -->

<style>
  /* Scoped styles */
</style>
```
""",
    
    'angular': """
Generate an Angular 17+ component:

- Use standalone components
- Implement proper TypeScript types
- Use Angular signals for reactivity
- Follow Angular style guide
- Include template and styles

Structure:
```typescript
// component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-component',
  standalone: true,
  imports: [CommonModule],
  template: `
    <!-- Template here -->
  `,
  styles: [`
    /* Styles here */
  `]
})
export class ComponentName {
  // Component logic
}
```
"""
}


# CSS Framework-specific additions
CSS_FRAMEWORK_PROMPTS = {
    'tailwind': """
Use Tailwind CSS utility classes:

- Use Tailwind's responsive modifiers (sm:, md:, lg:, xl:, 2xl:)
- Implement hover, focus, and active states
- Use Tailwind's color palette
- Apply proper spacing with Tailwind utilities
- Use flexbox and grid utilities
- Include dark mode support where appropriate

Example:
```html
<div class="container mx-auto px-4 py-8">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Content -->
    </div>
</div>
```

Do NOT write custom CSS unless absolutely necessary. Use Tailwind utilities.
""",
    
    'bootstrap': """
Use Bootstrap 5 classes:

- Use Bootstrap's grid system (container, row, col-*)
- Implement Bootstrap components (card, btn, navbar, etc.)
- Use Bootstrap utilities (m-*, p-*, text-*, bg-*, etc.)
- Include responsive breakpoints (col-sm-*, col-md-*, etc.)
- Apply Bootstrap color classes

Example:
```html
<div class="container">
    <div class="row g-4">
        <div class="col-12 col-md-6 col-lg-4">
            <!-- Content -->
        </div>
    </div>
</div>
```

Prefer Bootstrap classes over custom CSS.
""",
    
    'css': """
Write custom CSS from scratch:

- Use CSS Grid and Flexbox for layout
- Implement CSS custom properties (variables)
- Use modern CSS features (clamp(), min(), max())
- Include media queries for responsiveness
- Follow BEM naming convention
- Add smooth transitions and animations

Example:
```css
:root {
    --primary-color: #3b82f6;
    --spacing-unit: 1rem;
}

.component {
    display: grid;
    gap: var(--spacing-unit);
}

@media (min-width: 768px) {
    .component {
        grid-template-columns: repeat(2, 1fr);
    }
}
```
"""
}


# Quality enhancement prompts
QUALITY_PROMPTS = {
    'accessibility': """
Ensure maximum accessibility:

1. Add proper ARIA labels and roles
2. Include alt text for all images
3. Ensure keyboard navigation works
4. Use semantic HTML elements
5. Provide sufficient color contrast
6. Include focus indicators
7. Support screen readers

Example:
```html
<button aria-label="Close menu" class="menu-close">
    <span aria-hidden="true">×</span>
</button>

<img src="..." alt="Descriptive alt text">

<nav role="navigation" aria-label="Main navigation">
    <!-- Nav items -->
</nav>
```
""",
    
    'responsive': """
Make the design fully responsive:

1. Mobile-first approach
2. Flexible layouts (grid, flexbox)
3. Responsive typography (clamp, rem)
4. Responsive images (srcset, picture)
5. Touch-friendly interactions (44px minimum)
6. Breakpoints: 640px, 768px, 1024px, 1280px, 1536px

Example:
```css
.container {
    width: 100%;
    max-width: 1280px;
    padding: 1rem;
}

@media (min-width: 768px) {
    .container {
        padding: 2rem;
    }
}

.text {
    font-size: clamp(1rem, 2.5vw, 1.5rem);
}
```
""",
    
    'performance': """
Optimize for performance:

1. Minimize DOM manipulations
2. Use CSS transforms for animations
3. Lazy load images
4. Debounce event handlers
5. Use efficient selectors
6. Avoid layout thrashing
7. Optimize critical rendering path

Example:
```javascript
// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func(...args), wait);
    };
}

// Lazy loading
<img loading="lazy" src="..." alt="...">
```
"""
}


def get_prompt(framework='react', css_framework='tailwind', include_quality=True):
    """
    Generate complete prompt for AI code generation.
    
    Args:
        framework: Target framework (react, vue, html, svelte, angular)
        css_framework: CSS framework (tailwind, bootstrap, css)
        include_quality: Whether to include quality enhancement prompts
        
    Returns:
        Complete prompt string
    """
    prompt_parts = [BASE_SYSTEM_PROMPT]
    
    # Add framework-specific prompt
    if framework in FRAMEWORK_PROMPTS:
        prompt_parts.append(FRAMEWORK_PROMPTS[framework])
    
    # Add CSS framework prompt
    if css_framework in CSS_FRAMEWORK_PROMPTS:
        prompt_parts.append(CSS_FRAMEWORK_PROMPTS[css_framework])
    
    # Add quality prompts
    if include_quality:
        prompt_parts.extend([
            QUALITY_PROMPTS['accessibility'],
            QUALITY_PROMPTS['responsive'],
            QUALITY_PROMPTS['performance']
        ])
    
    return '\n\n'.join(prompt_parts)


def get_user_prompt(additional_instructions=''):
    """
    Generate user prompt with screenshot analysis request.
    
    Args:
        additional_instructions: Any additional user instructions
        
    Returns:
        User prompt string
    """
    prompt = """Analyze the provided screenshot carefully and generate the code to recreate this UI.

Pay attention to:
- Layout and structure
- Colors and gradients
- Typography (fonts, sizes, weights)
- Spacing and alignment
- Shadows and borders
- Interactive elements (buttons, forms, etc.)
- Icons and images

Generate complete, production-ready code that matches the screenshot as closely as possible."""
    
    if additional_instructions:
        prompt += f"\n\nAdditional instructions:\n{additional_instructions}"
    
    return prompt
