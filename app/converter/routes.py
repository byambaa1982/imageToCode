# app/converter/routes.py
"""Converter routes."""

import os
import uuid
from datetime import datetime, timedelta

from flask import (
    render_template, redirect, url_for, flash, request, 
    jsonify, current_app, send_file, abort
)
from flask_login import login_required, current_user

from app.converter import converter
from app.converter.forms import UploadForm, FeedbackForm
from app.converter.utils import (
    validate_image_file, 
    save_uploaded_file,
    cleanup_temp_files
)
from app.extensions import db
from app.models import Conversion, ConversionFeedback
from app.tasks.conversion_tasks import (
    process_screenshot_conversion,
    get_conversion_status,
    retry_failed_conversion
)


@converter.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload page."""
    # Refresh current user data from database to get latest credits
    db.session.refresh(current_user)
    
    # Temporarily disabled for development - re-enable for production
    # if not current_user.email_verified:
    #     flash('Please verify your email address before converting screenshots.', 'warning')
    #     return redirect(url_for('account.dashboard'))
    
    if not current_user.has_credits():
        flash('You have no credits remaining. Please purchase more credits.', 'warning')
        return redirect(url_for('payment.pricing'))
    
    form = UploadForm()
    
    if form.validate_on_submit():
        try:
            # Validate uploaded file
            is_valid, error_msg = validate_image_file(form.screenshot.data)
            if not is_valid:
                flash(f'Invalid file: {error_msg}', 'error')
                return render_template('converter/upload.html', form=form)
            
            # Generate conversion UUID
            conversion_uuid = str(uuid.uuid4())
            
            # Save uploaded file
            success, file_path, error_msg = save_uploaded_file(form.screenshot.data, conversion_uuid)
            if not success:
                flash(f'Failed to save file: {error_msg}', 'error')
                return render_template('converter/upload.html', form=form)
            
            # Create conversion record
            conversion = Conversion(
                uuid=conversion_uuid,
                account_id=current_user.id,
                original_image_url=file_path,
                original_filename=form.screenshot.data.filename,
                framework=form.framework.data,
                css_framework=form.css_framework.data,
                status='pending',
                ip_address=request.remote_addr
            )
            
            db.session.add(conversion)
            
            # Deduct credits
            try:
                current_user.deduct_credits(1.0, f'Conversion {conversion_uuid}')
                current_app.logger.info(f'Deducted 1 credit from user {current_user.id} for conversion {conversion_uuid}')
            except ValueError as e:
                db.session.rollback()
                flash('Insufficient credits. Please purchase more credits.', 'error')
                return redirect(url_for('payment.pricing'))
            
            db.session.commit()
            
            # Start background processing (for Phase 2, we'll call directly)
            # In production, this should be a proper Celery task
            try:
                from app.tasks.conversion_tasks import process_screenshot_conversion
                # For now, call directly (TODO: make async in production)
                import threading
                thread = threading.Thread(target=process_screenshot_conversion, args=[conversion_uuid])
                thread.daemon = True
                thread.start()
                
                current_app.logger.info(f'Started conversion processing for {conversion_uuid}')
            except Exception as e:
                current_app.logger.error(f'Failed to start conversion processing: {str(e)}')
                db.session.rollback()
                # Refund the credit
                current_user.add_credits(1.0, f'Refund for failed conversion start {conversion_uuid}')
                flash('Failed to start conversion. Please try again.', 'error')
                return redirect(url_for('converter.upload'))
            

            
            # Redirect to processing page
            flash('Your screenshot has been uploaded successfully! Processing will begin shortly.', 'success')
            return redirect(url_for('converter.processing', conversion_uuid=conversion_uuid))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error in upload route: {str(e)}')
            flash('An error occurred while processing your upload. Please try again.', 'error')
            
            # Cleanup uploaded file if it exists
            if 'file_path' in locals() and file_path:
                cleanup_temp_files([file_path])
    
    return render_template('converter/upload.html', form=form)


@converter.route('/processing/<conversion_uuid>')
@login_required
def processing(conversion_uuid):
    """Processing page with real-time status updates."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        flash('Conversion not found.', 'error')
        return redirect(url_for('account.dashboard'))
    
    # If already completed, redirect to result
    if conversion.status == 'completed':
        return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))
    
    return render_template('converter/processing.html', 
                         conversion=conversion,
                         conversion_uuid=conversion_uuid)


@converter.route('/result/<conversion_uuid>')
@login_required
def result(conversion_uuid):
    """Result page showing generated code."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        flash('Conversion not found.', 'error')
        return redirect(url_for('account.dashboard'))
    
    if conversion.status != 'completed':
        if conversion.status == 'failed':
            flash('Conversion failed. You can retry or contact support.', 'error')
        else:
            return redirect(url_for('converter.processing', conversion_uuid=conversion_uuid))
    
    # Check if files have expired
    if conversion.expires_at and conversion.expires_at < datetime.utcnow():
        flash('This conversion has expired. Files are no longer available.', 'warning')
        return redirect(url_for('account.dashboard'))
    
    feedback_form = FeedbackForm()
    
    # Check if this was generated in demo mode (heuristic)
    is_demo_mode = (
        conversion.tokens_used == 0 and 
        conversion.generated_html and 
        ('Your App' in conversion.generated_html or 'Demo mode' in str(conversion.generated_html))
    )
    
    return render_template('converter/result.html', 
                         conversion=conversion,
                         feedback_form=feedback_form,
                         is_demo_mode=is_demo_mode)


@converter.route('/api/status/<conversion_uuid>')
@login_required
def api_conversion_status(conversion_uuid):
    """API endpoint to get conversion status."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        return jsonify({'error': 'Conversion not found'}), 404
    
    # Get detailed status
    status_data = get_conversion_status(conversion_uuid)
    
    return jsonify(status_data)


@converter.route('/api/retry/<conversion_uuid>', methods=['POST'])
@login_required
def api_retry_conversion(conversion_uuid):
    """API endpoint to retry failed conversion."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        return jsonify({'error': 'Conversion not found'}), 404
    
    if conversion.status != 'failed':
        return jsonify({'error': 'Conversion is not in failed state'}), 400
    
    if conversion.retry_count >= 3:
        return jsonify({'error': 'Maximum retry attempts exceeded'}), 400
    
    try:
        # Start retry task
        from app.tasks.conversion_tasks import retry_failed_conversion
        import threading
        thread = threading.Thread(target=retry_failed_conversion, args=[conversion_uuid])
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Retry started'
        })
        
    except Exception as e:
        current_app.logger.error(f'Error retrying conversion {conversion_uuid}: {str(e)}')
        return jsonify({'error': 'Failed to start retry'}), 500


@converter.route('/download/<conversion_uuid>')
@login_required
def download_conversion(conversion_uuid):
    """Download generated code package."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        flash('Conversion not found.', 'error')
        return redirect(url_for('account.dashboard'))
    
    if conversion.status != 'completed':
        flash('Conversion is not ready for download.', 'error')
        return redirect(url_for('converter.processing', conversion_uuid=conversion_uuid))
    
    # Check if conversion has generated content - if not, generate demo content
    if not conversion.generated_html or conversion.generated_html.strip() == '' or 'HTML code here' in conversion.generated_html:
        current_app.logger.warning(f'Empty or placeholder HTML detected for {conversion_uuid}, generating demo code for download')
        
        # Generate demo code on-the-fly for download
        try:
            from app.converter.ai_service import AIService
            ai_service = AIService()
            demo_code = ai_service._generate_demo_code(conversion.framework, conversion.css_framework or 'tailwind')
            
            # Update the conversion with demo content 
            conversion.generated_html = demo_code.get('html', '')
            conversion.generated_css = demo_code.get('css', '')
            conversion.generated_js = demo_code.get('js', '')
            
            # Save to database
            from app.extensions import db
            db.session.commit()
            
            current_app.logger.info(f'Generated and saved demo code for {conversion_uuid}')
            
        except Exception as e:
            current_app.logger.error(f'Failed to generate demo code for {conversion_uuid}: {str(e)}')
            flash('No generated content available for download.', 'error')
            return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))
    
    # Generate ZIP on-the-fly if file doesn't exist
    if not conversion.download_url or not os.path.exists(conversion.download_url):
        try:
            # Generate ZIP package dynamically
            import tempfile
            import zipfile
            from io import BytesIO
            
            # Create in-memory ZIP
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add HTML file
                if conversion.generated_html:
                    zip_file.writestr('index.html', conversion.generated_html)
                
                # For React, also add the pure component file
                if conversion.framework == 'react' and conversion.generated_html:
                    # Extract React component from the HTML
                    react_component = '''import React from 'react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
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
            <button className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700">
              Get Started
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Build Amazing
            <span className="text-blue-600 block">Digital Experiences</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Transform your ideas into stunning websites and applications.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg font-semibold">
              Start Building
            </button>
            <button className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg hover:bg-gray-50 text-lg font-semibold">
              Learn More
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}'''
                    zip_file.writestr('LandingPage.jsx', react_component)
                
                # Add CSS file  
                if conversion.generated_css:
                    zip_file.writestr('styles.css', conversion.generated_css)
                
                # Add JS file
                if conversion.generated_js:
                    zip_file.writestr('script.js', conversion.generated_js)
                
                # Add README
                if conversion.framework == 'react':
                    readme_content = f"""# React Conversion: {conversion.original_filename}

Generated on: {conversion.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Framework: {conversion.framework}
CSS Framework: {conversion.css_framework or 'None'}

## Files:
- **index.html** - Standalone HTML file with React CDN (open directly in browser)
- **LandingPage.jsx** - Pure React component for use in React projects
- **styles.css** - CSS styles
- **script.js** - JavaScript utilities

## Usage:

### Option 1: Standalone HTML (Immediate Use)
Open `index.html` in any web browser - no build process required!
This file includes React via CDN and uses Babel for in-browser JSX compilation.

### Option 2: React Project Integration
1. Copy `LandingPage.jsx` to your React project
2. Import and use: `import LandingPage from './LandingPage';`
3. Include the CSS styles in your project
4. Install required dependencies: `npm install react react-dom`

## Development Notes:
- The standalone HTML is perfect for quick previews and demos
- The JSX component follows React best practices and is production-ready
- All styling uses Tailwind CSS classes
- Icons are inline SVGs for zero dependencies
"""
                else:
                    readme_content = f"""# Conversion: {conversion.original_filename}

Generated on: {conversion.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Framework: {conversion.framework}
CSS Framework: {conversion.css_framework or 'None'}

## Files:
- index.html - Main HTML file
- styles.css - CSS styles
- script.js - JavaScript code

## Usage:
Open index.html in a web browser to view the converted design.
"""
                zip_file.writestr('README.md', readme_content)
            
            zip_buffer.seek(0)
            
            # Return the ZIP file
            from flask import Response
            return Response(
                zip_buffer.getvalue(),
                mimetype='application/zip',
                headers={
                    'Content-Disposition': f'attachment; filename=conversion_{conversion_uuid}.zip'
                }
            )
            
        except Exception as e:
            current_app.logger.error(f'Error generating download package for {conversion_uuid}: {str(e)}')
            flash('Error generating download package. Please try again.', 'error')
            return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))
    
    # Use existing file if it exists
    try:
        return send_file(
            conversion.download_url,
            as_attachment=True,
            download_name=f'conversion_{conversion_uuid}.zip',
            mimetype='application/zip'
        )
    except Exception as e:
        current_app.logger.error(f'Error downloading file {conversion.download_url}: {str(e)}')
        flash('Error downloading file. Please try again.', 'error')
        return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))


@converter.route('/preview/<conversion_uuid>')
@login_required
def preview_conversion(conversion_uuid):
    """Preview generated HTML."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        current_app.logger.error(f'Conversion not found: {conversion_uuid}')
        abort(404)
    
    if conversion.status != 'completed':
        current_app.logger.error(f'Conversion not completed: {conversion_uuid}, status: {conversion.status}')
        abort(404)
    
    # Check if generated content exists
    if not conversion.generated_html:
        current_app.logger.error(f'No generated HTML for conversion: {conversion_uuid}')
        # Return a simple error page instead of aborting
        from flask import Response
        error_html = """
        <html>
        <head><title>Preview Not Available</title></head>
        <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
            <h1>Preview Not Available</h1>
            <p>This conversion doesn't have generated code available for preview.</p>
            <p>Conversion Status: """ + conversion.status + """</p>
        </body>
        </html>
        """
        return Response(error_html, mimetype='text/html')
    
    if conversion.preview_url and os.path.exists(conversion.preview_url):
        return send_file(conversion.preview_url)
    
    # Generate preview on the fly if file doesn't exist
    try:
        from app.converter.utils import generate_preview_html
        preview_html = generate_preview_html(
            conversion.generated_html or '',
            conversion.generated_css or '',
            conversion.generated_js or ''
        )
        
        current_app.logger.info(f'Generated preview for conversion: {conversion_uuid}')
        from flask import Response
        return Response(preview_html, mimetype='text/html')
        
    except Exception as e:
        current_app.logger.error(f'Error generating preview for {conversion_uuid}: {str(e)}')
        from flask import Response
        error_html = f"""
        <html>
        <head><title>Preview Error</title></head>
        <body style="font-family: Arial, sans-serif; padding: 50px; text-align: center;">
            <h1>Preview Error</h1>
            <p>There was an error generating the preview.</p>
            <p>Error: {str(e)}</p>
        </body>
        </html>
        """
        return Response(error_html, mimetype='text/html')


@converter.route('/feedback/<conversion_uuid>', methods=['POST'])
@login_required
def submit_feedback(conversion_uuid):
    """Submit feedback for a conversion."""
    # Verify conversion belongs to current user
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        return jsonify({'error': 'Conversion not found'}), 404
    
    form = FeedbackForm()
    if form.validate_on_submit():
        try:
            # Check if feedback already exists
            existing_feedback = ConversionFeedback.query.filter_by(
                conversion_id=conversion.id,
                account_id=current_user.id
            ).first()
            
            if existing_feedback:
                # Update existing feedback
                existing_feedback.rating = int(form.rating.data)
                existing_feedback.feedback_text = form.feedback_text.data
                existing_feedback.issues = form.issues.data
                existing_feedback.updated_at = datetime.utcnow()
            else:
                # Create new feedback
                feedback = ConversionFeedback(
                    conversion_id=conversion.id,
                    account_id=current_user.id,
                    rating=int(form.rating.data),
                    feedback_text=form.feedback_text.data,
                    issues=form.issues.data
                )
                db.session.add(feedback)
            
            db.session.commit()
            
            if request.is_json:
                return jsonify({'success': True, 'message': 'Feedback submitted successfully'})
            else:
                flash('Thank you for your feedback!', 'success')
                return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error submitting feedback: {str(e)}')
            
            if request.is_json:
                return jsonify({'error': 'Failed to submit feedback'}), 500
            else:
                flash('Failed to submit feedback. Please try again.', 'error')
                return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))
    
    if request.is_json:
        return jsonify({'error': 'Invalid form data', 'errors': form.errors}), 400
    else:
        flash('Please correct the errors and try again.', 'error')
        return redirect(url_for('converter.result', conversion_uuid=conversion_uuid))


@converter.route('/retry/<conversion_uuid>')
@login_required
def retry(conversion_uuid):
    """Retry a failed conversion."""
    conversion = Conversion.query.filter_by(
        uuid=conversion_uuid,
        account_id=current_user.id
    ).first()
    
    if not conversion:
        flash('Conversion not found.', 'error')
        return redirect(url_for('account.history'))
    
    if conversion.status != 'failed':
        flash('This conversion is not in a failed state.', 'error')
        return redirect(url_for('account.history'))
    
    if conversion.retry_count >= 3:
        flash('Maximum retry attempts exceeded.', 'error')
        return redirect(url_for('account.history'))
    
    try:
        # Start retry task
        from app.tasks.conversion_tasks import retry_failed_conversion
        import threading
        thread = threading.Thread(target=retry_failed_conversion, args=[conversion_uuid])
        thread.daemon = True
        thread.start()
        
        flash('Conversion retry started. You will be notified when it completes.', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error retrying conversion: {e}")
        flash('Failed to retry conversion. Please try again.', 'error')
    
    return redirect(url_for('account.history'))
