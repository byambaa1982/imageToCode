# app/tasks/conversion_tasks.py
"""Conversion background tasks."""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import current_task
from app.extensions import db
from app.models import Conversion, Account
from app.converter.ai_service import AIService
from app.converter.utils import (
    process_image_for_ai, 
    cleanup_temp_files, 
    generate_preview_html,
    validate_generated_code,
    create_download_package
)

logger = logging.getLogger(__name__)

def process_screenshot_conversion(conversion_uuid: str) -> Dict[str, Any]:
    """
    Background task to process screenshot conversion.
    
    Args:
        conversion_uuid: UUID of the conversion to process
        
    Returns:
        Dict with conversion results
    """
    # Import app here to avoid circular imports
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            # Update task status (placeholder for future Celery integration)
            logger.info(f'Starting conversion for {conversion_uuid}')
            
            # Get conversion from database
            conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            if not conversion:
                raise Exception(f"Conversion {conversion_uuid} not found")
            
            # Update conversion status
            conversion.status = 'processing'
            db.session.commit()
            
            # Update task status (placeholder for future Celery integration)
            logger.info(f'Processing image for {conversion_uuid}')
            
            # Process image for AI
            success, processed_path, error = process_image_for_ai(conversion.original_image_url)
            if not success:
                raise Exception(f"Image processing failed: {error}")
            
            # Update task status (placeholder for future Celery integration)
            logger.info(f'Calling AI service for {conversion_uuid}')
            
            # Initialize AI service
            ai_service = AIService()
            
            # Call AI service
            ai_result = ai_service.convert_screenshot_to_code(
                image_path=processed_path or conversion.original_image_url,
                framework=conversion.framework,
                css_framework=conversion.css_framework
            )
            
            if not ai_result.get('success', False):
                raise Exception(f"AI conversion failed: {ai_result.get('error', 'Unknown error')}")
            
            # Update task status (placeholder for future Celery integration)  
            logger.info(f'Validating generated code for {conversion_uuid}')
            
            # Validate generated code
            html_code = ai_result.get('html', '')
            css_code = ai_result.get('css', '')
            js_code = ai_result.get('js', '')
            
            is_valid, validation_error = validate_generated_code(html_code, css_code, js_code)
            if not is_valid:
                logger.warning(f"Code validation warning for {conversion_uuid}: {validation_error}")
            
            # Update task status (placeholder for future Celery integration)
            logger.info(f'Creating preview and download package for {conversion_uuid}')
            
            # Generate preview HTML
            preview_html = generate_preview_html(html_code, css_code, js_code)
            
            # Create download package
            package_success, zip_path, package_error = create_download_package(
                html_code, css_code, js_code, conversion_uuid
            )
            
            if not package_success:
                logger.error(f"Failed to create download package for {conversion_uuid}: {package_error}")
            
            # Update conversion in database
            conversion.generated_html = html_code
            conversion.generated_css = css_code
            conversion.generated_js = js_code
            conversion.processing_time = ai_result.get('processing_time', 0)
            conversion.tokens_used = ai_result.get('tokens_used', 0)
            conversion.status = 'completed'
            conversion.download_url = zip_path if package_success else None
            conversion.expires_at = datetime.utcnow() + timedelta(days=30)  # Files expire in 30 days
            
            # Create preview file
            try:
                preview_filename = f"{conversion_uuid}_preview.html"
                preview_path = os.path.join(os.path.dirname(conversion.original_image_url), preview_filename)
                with open(preview_path, 'w', encoding='utf-8') as f:
                    f.write(preview_html)
                conversion.preview_url = preview_path
            except Exception as e:
                logger.error(f"Failed to save preview for {conversion_uuid}: {str(e)}")
            
            db.session.commit()
            
            # Cleanup temporary files
            cleanup_files = [processed_path] if processed_path != conversion.original_image_url else []
            cleanup_temp_files(cleanup_files)
            
            # Update task status (placeholder for future Celery integration)
            logger.info(f'Conversion completed successfully for {conversion_uuid}')
            
            logger.info(f"Conversion {conversion_uuid} completed successfully")
            
            return {
                'success': True,
                'conversion_uuid': conversion_uuid,
                'status': 'completed',
                'html': html_code,
                'css': css_code,
                'js': js_code,
                'processing_time': conversion.processing_time,
                'tokens_used': conversion.tokens_used
            }
            
        except Exception as e:
            logger.error(f"Error processing conversion {conversion_uuid}: {str(e)}")
            
            try:
                # Update conversion status to failed
                conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
                if conversion:
                    conversion.status = 'failed'
                    conversion.error_message = str(e)
                    conversion.retry_count = (conversion.retry_count or 0) + 1
                    db.session.commit()
                    
                    # Refund credits if this is the first attempt
                    if conversion.retry_count == 1:
                        account = Account.query.get(conversion.account_id)
                        if account:
                            try:
                                account.add_credits(1.0, f"Refund for failed conversion {conversion_uuid}")
                                logger.info(f"Refunded 1 credit to account {account.id} for failed conversion {conversion_uuid}")
                            except Exception as refund_error:
                                logger.error(f"Failed to refund credits for {conversion_uuid}: {str(refund_error)}")
            except Exception as db_error:
                logger.error(f"Failed to update database for failed conversion {conversion_uuid}: {str(db_error)}")
            
            # Update task status (placeholder for future Celery integration)
            logger.error(f'Conversion failed for {conversion_uuid}: {str(e)}')
            
            return {
                'success': False,
                'error': str(e),
                'conversion_uuid': conversion_uuid
            }


def retry_failed_conversion(conversion_uuid: str) -> Dict[str, Any]:
    """
    Retry a failed conversion.
    
    Args:
        conversion_uuid: UUID of the conversion to retry
        
    Returns:
        Dict with retry results
    """
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            if not conversion:
                return {'success': False, 'error': 'Conversion not found'}
            
            if conversion.status != 'failed':
                return {'success': False, 'error': 'Conversion is not in failed state'}
            
            if conversion.retry_count >= 3:
                return {'success': False, 'error': 'Maximum retry attempts exceeded'}
            
            # Reset conversion status
            conversion.status = 'pending'
            conversion.error_message = None
            db.session.commit()
            
            # Process the conversion
            return process_screenshot_conversion(conversion_uuid)
            
        except Exception as e:
            logger.error(f"Error retrying conversion {conversion_uuid}: {str(e)}")
            return {'success': False, 'error': str(e)}


def cleanup_expired_conversions():
    """Clean up expired conversions and files."""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            # Find expired conversions
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            expired_conversions = Conversion.query.filter(
                Conversion.expires_at < datetime.utcnow()
            ).all()
            
            cleanup_count = 0
            for conversion in expired_conversions:
                try:
                    # Delete associated files
                    files_to_delete = [
                        conversion.original_image_url,
                        conversion.preview_url,
                        conversion.download_url
                    ]
                    
                    for file_path in files_to_delete:
                        if file_path and os.path.exists(file_path):
                            os.remove(file_path)
                    
                    # Delete conversion record
                    db.session.delete(conversion)
                    cleanup_count += 1
                    
                except Exception as e:
                    logger.error(f"Error cleaning up conversion {conversion.uuid}: {str(e)}")
            
            db.session.commit()
            logger.info(f"Cleaned up {cleanup_count} expired conversions")
            
            return {'success': True, 'cleaned_count': cleanup_count}
            
        except Exception as e:
            logger.error(f"Error in cleanup_expired_conversions: {str(e)}")
            return {'success': False, 'error': str(e)}


def get_conversion_status(conversion_uuid: str) -> Dict[str, Any]:
    """
    Get the current status of a conversion.
    
    Args:
        conversion_uuid: UUID of the conversion
        
    Returns:
        Dict with conversion status
    """
    from app import create_app
    
    app = create_app()
    with app.app_context():
        try:
            conversion = Conversion.query.filter_by(uuid=conversion_uuid).first()
            if not conversion:
                return {'success': False, 'error': 'Conversion not found'}
            
            return {
                'success': True,
                'uuid': conversion.uuid,
                'status': conversion.status,
                'error_message': conversion.error_message,
                'processing_time': float(conversion.processing_time) if conversion.processing_time else None,
                'tokens_used': conversion.tokens_used,
                'created_at': conversion.created_at.isoformat(),
                'updated_at': conversion.updated_at.isoformat(),
                'preview_url': conversion.preview_url,
                'download_url': conversion.download_url,
                'retry_count': conversion.retry_count
            }
            
        except Exception as e:
            logger.error(f"Error getting conversion status {conversion_uuid}: {str(e)}")
            return {'success': False, 'error': str(e)}
