# app/tasks/email_templates.py
"""Email template definitions."""

def get_email_templates():
    """Get all email templates as a dictionary."""
    return {
        'conversion_complete': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Conversion Complete</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Your Conversion is Ready!</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Great news! Your screenshot conversion has been completed successfully.</p>
                    <p><strong>File:</strong> {{ conversion.original_filename }}<br>
                       <strong>Framework:</strong> {{ conversion.framework|title }}<br>
                       <strong>Completed:</strong> {{ conversion.updated_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
                    <p><a href="{{ result_url }}" class="button">View Your Code</a></p>
                    <p>You can view, edit, and download your converted code from your dashboard.</p>
                </div>
                <div class="footer">
                    <p>Happy coding!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'low_credit_warning': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Low Credits Warning</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #F59E0B, #EF4444); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #fff8f1; padding: 30px 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #F59E0B; }
                .button { display: inline-block; background: #F59E0B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ Running Low on Credits</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>You currently have <strong>{{ account.credits_remaining|int }} credit</strong> remaining.</p>
                    <p>Don't let your creative flow stop! Get more credits to continue converting your screenshots into beautiful code.</p>
                    <p><a href="{{ pricing_url }}" class="button">Buy More Credits</a></p>
                    <p>Our credit packages start at just $1.99 for 2 conversions.</p>
                </div>
                <div class="footer">
                    <p>Keep creating!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'welcome': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Screenshot to Code</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 5px; }
                .feature { background: white; padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #8B5CF6; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 Welcome to Screenshot to Code!</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Welcome to the most powerful AI-powered screenshot-to-code converter! We're excited to have you on board.</p>
                    
                    <div class="feature">
                        <h3>🎁 You have 3 FREE conversions</h3>
                        <p>Start exploring right away with your complimentary credits!</p>
                    </div>
                    
                    <div class="feature">
                        <h3>⚡ Supported Frameworks</h3>
                        <p>React, Vue.js, HTML/CSS/JS, Svelte, and Angular</p>
                    </div>
                    
                    <div class="feature">
                        <h3>🎨 CSS Frameworks</h3>
                        <p>Tailwind CSS, Bootstrap, or plain CSS</p>
                    </div>
                    
                    <p><a href="{{ upload_url }}" class="button">Start Converting</a>
                       <a href="{{ dashboard_url }}" class="button">Visit Dashboard</a></p>
                </div>
                <div class="footer">
                    <p>Happy coding!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'weekly_summary': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Weekly Summary</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #8B5CF6, #06B6D4); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f9f9f9; padding: 30px 20px; border-radius: 8px; margin: 20px 0; }
                .stat { background: white; padding: 20px; margin: 10px 0; border-radius: 6px; text-align: center; }
                .stat h3 { margin: 0; color: #8B5CF6; font-size: 2em; }
                .button { display: inline-block; background: #8B5CF6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Your Weekly Summary</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Here's a summary of your activity this week:</p>
                    
                    <div class="stat">
                        <h3>{{ weekly_conversions }}</h3>
                        <p>Total Conversions</p>
                    </div>
                    
                    <div class="stat">
                        <h3>{{ success_rate }}%</h3>
                        <p>Success Rate</p>
                    </div>
                    
                    <div class="stat">
                        <h3>{{ account.credits_remaining|int }}</h3>
                        <p>Credits Remaining</p>
                    </div>
                    
                    <p><a href="{{ dashboard_url }}" class="button">View Dashboard</a></p>
                </div>
                <div class="footer">
                    <p>Keep up the great work!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        ''',
        
        'purchase_receipt': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Purchase Receipt</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #10B981, #059669); color: white; padding: 30px 20px; text-align: center; border-radius: 8px; }
                .content { background: #f0fdf4; padding: 30px 20px; border-radius: 8px; margin: 20px 0; border: 2px solid #10B981; }
                .receipt { background: white; padding: 20px; border-radius: 6px; margin: 20px 0; }
                .button { display: inline-block; background: #10B981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }
                .footer { text-align: center; color: #666; font-size: 12px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Purchase Receipt</h1>
                </div>
                <div class="content">
                    <p>Hi {{ account.username }},</p>
                    <p>Thank you for your purchase! Your credits have been added to your account.</p>
                    
                    <div class="receipt">
                        <h3>Order Details</h3>
                        <p><strong>Package:</strong> {{ order.package_type|replace('_', ' ')|title }}</p>
                        <p><strong>Credits:</strong> {{ order.credits_purchased }} credits</p>
                        <p><strong>Amount:</strong> ${{ order.amount }}</p>
                        <p><strong>Date:</strong> {{ order.created_at.strftime('%B %d, %Y at %I:%M %p') }}</p>
                        <p><strong>Order ID:</strong> {{ order.id }}</p>
                    </div>
                    
                    <p><a href="{{ billing_url }}" class="button">View Billing History</a></p>
                    <p>Your credits are now available and ready to use!</p>
                </div>
                <div class="footer">
                    <p>Happy converting!<br>The Screenshot to Code Team</p>
                </div>
            </div>
        </body>
        </html>
        '''
    }
