# Accessibility Fixes for Templates

## Issues Found and Fixes Needed

### base.html

1. **Line 76** - backdrop-filter vendor prefix
```css
/* Add vendor prefix before backdrop-filter */
-webkit-backdrop-filter: blur(12px);
backdrop-filter: blur(12px);
```

2. **Line 229** - Mobile menu button needs text
```html
<button id="mobile-menu-button" 
        class="text-gray-700 hover:text-purple-600 focus-ring p-2 rounded-lg transition-colors"
        aria-label="Toggle mobile menu"
        title="Toggle mobile menu">
    <!-- SVG icon here -->
</button>
```

3. **Line 306** - Alert close button needs text
```html
<button onclick="this.parentElement.parentElement.remove()" 
        class="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
        aria-label="Close alert"
        title="Close alert">
    <!-- Close icon -->
</button>
```

4. **Lines 342, 345, 348** - Social media links need text
```html
<a href="#" class="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
   aria-label="Follow us on Twitter"
   title="Follow us on Twitter">
    <!-- Twitter icon -->
</a>

<a href="#" class="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
   aria-label="Follow us on GitHub"
   title="Follow us on GitHub">
    <!-- GitHub icon -->
</a>

<a href="#" class="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center transition-all duration-300 hover:scale-110"
   aria-label="Join our Discord"
   title="Join our Discord">
    <!-- Discord icon -->
</a>
```

### admin/dashboard.html

1. **Line 165** - Remove inline styles
```html
<!-- Instead of inline style -->
<div class="bg-purple-600 h-2 rounded-full" style="width: {{ percentage }}%"></div>

<!-- Use CSS class -->
<div class="bg-purple-600 h-2 rounded-full progress-bar-fill" 
     data-width="{{ percentage }}"></div>

<!-- Add JavaScript to set width -->
<script>
document.querySelectorAll('.progress-bar-fill').forEach(el => {
    el.style.width = el.dataset.width + '%';
});
</script>
```

2. **Line 60** - Fix UL structure
```html
<!-- Before -->
<ul class="text-red-700 mt-1 text-sm">
    Text directly here
</ul>

<!-- After -->
<div class="text-red-700 mt-1 text-sm">
    Text content here
</div>

<!-- OR wrap in LI -->
<ul class="text-red-700 mt-1 text-sm list-none">
    <li>Error message here</li>
</ul>
```

### admin/users.html

1. **Line 74** - Clear filters link needs text
```html
<a href="{{ url_for('admin.users') }}" 
   class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition"
   aria-label="Clear all filters"
   title="Clear all filters">
    <svg><!-- Icon --></svg>
    <span class="ml-2">Clear</span>
</a>
```

2. **Lines 56, 64** - Select elements need labels
```html
<!-- Email Verified Filter -->
<label for="verified-filter" class="block text-sm font-medium text-gray-700 mb-2">
    Email Verified
</label>
<select name="verified" 
        id="verified-filter"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        aria-label="Filter by email verification status">
    <option value="">All</option>
    <option value="1">Verified</option>
    <option value="0">Not Verified</option>
</select>

<!-- Admin Status Filter -->
<label for="admin-filter" class="block text-sm font-medium text-gray-700 mb-2">
    Admin Status
</label>
<select name="admin" 
        id="admin-filter"
        class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        aria-label="Filter by admin status">
    <option value="">All</option>
    <option value="1">Admin</option>
    <option value="0">Regular User</option>
</select>
```

## Automated Fix Script

Run this to fix common accessibility issues:

```python
# fix_accessibility.py
import re

def fix_buttons_without_labels(html):
    """Add aria-label to buttons without text."""
    # Pattern for buttons without aria-label
    pattern = r'(<button[^>]*?)(?!.*aria-label)(?!.*title)(>)'
    
    # Add aria-label based on context
    def add_label(match):
        button_tag = match.group(1)
        if 'mobile-menu' in button_tag:
            return button_tag + ' aria-label="Toggle menu" title="Toggle menu">'
        elif 'close' in button_tag.lower() or '×' in button_tag:
            return button_tag + ' aria-label="Close" title="Close">'
        else:
            return button_tag + ' aria-label="Button" title="Button">'
    
    return re.sub(pattern, add_label, html)

def fix_links_without_text(html):
    """Add aria-label to links without text."""
    # Similar pattern for links
    pass

def fix_select_without_label(html):
    """Add labels to select elements."""
    pass

# Usage
with open('template.html', 'r') as f:
    html = f.read()

html = fix_buttons_without_labels(html)
# ... other fixes

with open('template.html', 'w') as f:
    f.write(html)
```

## Accessibility Testing Checklist

- [ ] All images have alt text
- [ ] All buttons have discernible text or aria-label
- [ ] All links have discernible text or aria-label
- [ ] All form inputs have associated labels
- [ ] Color contrast meets WCAG AA standards
- [ ] Keyboard navigation works
- [ ] Focus indicators are visible
- [ ] ARIA roles and states are properly used
- [ ] Heading hierarchy is correct (h1, h2, h3...)
- [ ] Lists only contain li elements
- [ ] No inline styles (or minimal)
- [ ] Vendor prefixes for CSS properties

## Tools for Accessibility Testing

1. **Browser Extensions**
   - axe DevTools
   - WAVE
   - Lighthouse (Chrome DevTools)

2. **Command Line**
   - pa11y
   - axe-core

3. **Automated Testing**
```javascript
// Add to test suite
describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
        const results = await axe.run();
        expect(results.violations).toHaveLength(0);
    });
});
```

## Quick Fixes Script

```bash
# Run accessibility linter
npm install -g pa11y
pa11y http://localhost:5000

# Fix common issues
grep -r "backdrop-filter" app/templates/ --include="*.html"
grep -r "<button" app/templates/ --include="*.html" | grep -v "aria-label"
grep -r "<a href" app/templates/ --include="*.html" | grep -v "aria-label"
grep -r "<select" app/templates/ --include="*.html" | grep -v "aria-label"
```
