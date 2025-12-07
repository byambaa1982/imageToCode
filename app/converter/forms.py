# app/converter/forms.py
"""Converter forms."""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional
from config import Config


class UploadForm(FlaskForm):
    """Form for uploading screenshots."""
    
    screenshot = FileField(
        'Screenshot',
        validators=[
            FileRequired(message='Please select a screenshot to upload'),
            FileAllowed(
                Config.ALLOWED_EXTENSIONS,
                message=f'Only image files are allowed: {", ".join(Config.ALLOWED_EXTENSIONS)}'
            )
        ]
    )
    
    framework = SelectField(
        'Target Framework',
        choices=[
            ('html', 'HTML/CSS/JS'),
            ('react', 'React'),
            ('vue', 'Vue.js'),
            ('svelte', 'Svelte')
        ],
        default='react',
        validators=[DataRequired()]
    )
    
    css_framework = SelectField(
        'CSS Framework',
        choices=[
            ('tailwind', 'Tailwind CSS'),
            ('bootstrap', 'Bootstrap 5'),
            ('css', 'Custom CSS'),
            ('material', 'Material Design')
        ],
        default='tailwind',
        validators=[DataRequired()]
    )
    
    additional_instructions = TextAreaField(
        'Additional Instructions',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Any specific requirements or modifications? (optional)',
            'rows': 3
        }
    )
    
    responsive_design = BooleanField(
        'Generate Responsive Design',
        default=True
    )
    
    include_animations = BooleanField(
        'Include Hover Effects & Animations',
        default=True
    )
    
    accessibility_focus = BooleanField(
        'Focus on Accessibility (ARIA labels, semantic HTML)',
        default=True
    )


class FeedbackForm(FlaskForm):
    """Form for conversion feedback."""
    
    rating = SelectField(
        'How would you rate this conversion?',
        choices=[
            ('5', '⭐⭐⭐⭐⭐ Excellent'),
            ('4', '⭐⭐⭐⭐ Good'),
            ('3', '⭐⭐⭐ Fair'),
            ('2', '⭐⭐ Poor'),
            ('1', '⭐ Very Poor')
        ],
        validators=[DataRequired()]
    )
    
    feedback_text = TextAreaField(
        'Comments (optional)',
        validators=[Optional()],
        render_kw={
            'placeholder': 'Any suggestions for improvement?',
            'rows': 4
        }
    )
    
    issues = SelectField(
        'Any specific issues?',
        choices=[
            ('', 'No issues'),
            ('layout', 'Layout issues'),
            ('colors', 'Colors not matching'),
            ('responsiveness', 'Not responsive'),
            ('code_quality', 'Code quality issues'),
            ('missing_elements', 'Missing elements'),
            ('other', 'Other')
        ],
        validators=[Optional()]
    )
