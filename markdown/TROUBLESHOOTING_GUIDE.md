# Troubleshooting Guide - Screenshot to Code

## 🔧 Common Issues and Solutions

### Upload Problems

#### Issue: "Image Upload Failed" 
**Symptoms**: Upload button doesn't work, error message appears
**Solutions**:
1. **Check File Format**: Ensure your image is PNG, JPG, JPEG, or WebP
2. **Check File Size**: Maximum file size is 10MB
3. **Clear Browser Cache**: Press Ctrl+F5 (or Cmd+Shift+R on Mac)
4. **Try Different Browser**: Switch to Chrome, Firefox, or Safari
5. **Disable Ad Blockers**: Some extensions may interfere with uploads
6. **Check Internet Connection**: Ensure stable internet connectivity

#### Issue: "Upload Stuck at 0%" or "Upload Taking Forever"
**Solutions**:
1. **Reduce Image Size**: Compress or resize your image
2. **Check Network Speed**: Large files need stable connections
3. **Refresh Page**: Sometimes a simple refresh helps
4. **Try Incognito Mode**: Disable all extensions temporarily

### Conversion Problems

#### Issue: "Conversion Taking Too Long" (>5 minutes)
**Normal Processing Time**: 30-60 seconds
**Solutions**:
1. **Wait a Bit Longer**: Complex images may take up to 2 minutes
2. **Check System Status**: Visit our status page
3. **Refresh Page**: If stuck over 5 minutes, refresh and retry
4. **Try Simpler Image**: Start with a basic layout to test

#### Issue: "Conversion Failed" or "Error Processing Image"
**Solutions**:
1. **Image Quality**: Use higher resolution (1920x1080+)
2. **Better Contrast**: Ensure good contrast between elements
3. **Remove Noise**: Crop out browser UI, watermarks, annotations
4. **Try Different Image**: Test with a known-good screenshot first

#### Issue: "Generated Code Doesn't Match Screenshot"
**Solutions**:
1. **Higher Quality Image**: Use crisp, clear screenshots
2. **Better Lighting**: Avoid dark or poorly lit screens  
3. **Complete Elements**: Include full UI components, not partial crops
4. **Simpler Layouts**: Start with basic designs, build complexity
5. **Different Framework**: Try HTML/CSS instead of React for simple designs

### Account & Credit Issues

#### Issue: "Can't Log In" or "Invalid Credentials"
**Solutions**:
1. **Password Reset**: Click "Forgot Password" on login page
2. **Check Email**: Ensure you're using the correct registered email
3. **Account Verification**: Check if email verification is required
4. **Clear Cookies**: Clear browser cookies for our site
5. **Caps Lock**: Ensure caps lock is off for password

#### Issue: "Credits Not Updated After Purchase"
**Solutions**:
1. **Refresh Page**: Credits update may take a moment
2. **Check Email**: Look for purchase confirmation
3. **Payment Processing**: Stripe payments are usually instant
4. **Contact Support**: If credits missing after 10 minutes

#### Issue: "Payment Failed" or "Card Declined"
**Solutions**:
1. **Check Card Details**: Verify expiration date, CVV, billing address
2. **Try Different Card**: Some cards may have restrictions
3. **Contact Bank**: Ensure international payments are allowed
4. **Use PayPal**: Alternative payment method (if available)

### Performance Issues

#### Issue: "Website Loading Slowly"
**Solutions**:
1. **Clear Cache**: Clear browser cache and cookies
2. **Disable Extensions**: Turn off unnecessary browser extensions
3. **Check Internet**: Test speed at speedtest.net
4. **Try Different Region**: Use VPN if in restricted area
5. **Mobile vs Desktop**: Try different device

#### Issue: "Code Preview Not Loading"
**Solutions**:
1. **Enable JavaScript**: Ensure JS is enabled in browser
2. **Disable Ad Blockers**: May interfere with preview
3. **Check Popup Blockers**: Disable popup blocking for our site
4. **Try Incognito**: Test in private browsing mode

### Download Issues

#### Issue: "Download Not Starting" or "Download Failed"
**Solutions**:
1. **Allow Popups**: Enable popups for our domain
2. **Check Downloads Folder**: Files may download without notification
3. **Disable Download Manager**: Some extensions interfere
4. **Right-Click Save**: Try right-click > Save As
5. **Try Different Browser**: Switch browsers temporarily

#### Issue: "ZIP File Corrupted" or "Can't Open Files"
**Solutions**:
1. **Re-download**: Try downloading again
2. **Different Extraction Tool**: Use 7-Zip, WinRAR, or built-in tools
3. **Check File Size**: Ensure complete download (compare file sizes)
4. **Antivirus**: Temporarily disable real-time scanning

### Browser-Specific Issues

#### Chrome Issues
- **Clear Site Data**: Settings > Privacy > Site Settings > View permissions and data stored across sites
- **Disable Extensions**: Test in incognito mode
- **Update Browser**: Ensure Chrome is up to date

#### Firefox Issues  
- **Enhanced Tracking Protection**: Disable for our site
- **Clear Cookies**: Options > Privacy & Security > Clear Data
- **Safe Mode**: Test in Firefox Safe Mode

#### Safari Issues
- **Prevent Cross-Site Tracking**: Disable in Safari preferences
- **Clear Website Data**: Safari > Develop > Empty Caches
- **Allow JavaScript**: Ensure JS is enabled

### Mobile Issues

#### Issue: "Upload Not Working on Mobile"
**Solutions**:
1. **Use Desktop**: Mobile uploads may have limitations
2. **Try Different Mobile Browser**: Chrome, Firefox, Safari mobile
3. **Reduce Image Size**: Mobile connections may timeout
4. **Wi-Fi vs Mobile Data**: Try different connection types

### API Issues (For Developers)

#### Issue: "API Not Responding" or "Rate Limited"
**Solutions**:
1. **Check API Key**: Ensure valid API key in headers
2. **Rate Limits**: Respect rate limiting (check headers)
3. **Endpoint URLs**: Verify correct API endpoints
4. **Authentication**: Check authentication headers

## 🚨 When to Contact Support

Contact our support team if:

- **Credits Missing**: After confirmed payment
- **Account Locked**: Unable to access account
- **Repeated Failures**: Same error multiple times
- **Billing Issues**: Payment or refund problems
- **Technical Bugs**: Consistent system errors
- **Feature Requests**: Suggestions for improvements

### How to Contact Support

1. **Email**: support@screenshottocode.com
2. **Response Time**: Usually within 24 hours
3. **Include Information**:
   - Account email address
   - Error message (exact text)
   - Browser and version
   - Steps to reproduce issue
   - Screenshot of problem (if visual)

### Before Contacting Support

1. **Try Solutions Above**: Check relevant troubleshooting steps
2. **Test Different Browser**: Rule out browser-specific issues
3. **Check Status Page**: Verify if it's a known issue
4. **Clear Cache/Cookies**: Often resolves mysterious issues

## 📊 System Requirements

### Minimum Requirements
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **JavaScript**: Must be enabled
- **Cookies**: Must be enabled for our domain
- **Internet**: Stable broadband connection (5+ Mbps recommended)

### Recommended Requirements
- **Browser**: Latest version of Chrome or Firefox
- **RAM**: 4GB+ for large image processing
- **Internet**: 25+ Mbps for best experience
- **Screen Resolution**: 1920x1080+ for optimal UI

### Supported Image Formats
- **PNG**: Best for screenshots (supports transparency)
- **JPG/JPEG**: Good for photos and general images  
- **WebP**: Modern format with good compression
- **Max Size**: 10MB per file
- **Recommended Resolution**: 1920x1080 or higher

## 🔍 Debugging Tips

### Check Browser Console
1. Press F12 to open Developer Tools
2. Click "Console" tab
3. Look for red error messages
4. Include these in support requests

### Network Issues
1. Check "Network" tab in Developer Tools
2. Look for failed requests (red entries)
3. Note any 4xx or 5xx error codes

### Clear Everything
If all else fails:
1. Clear all cookies and cache
2. Disable all browser extensions
3. Restart browser
4. Try incognito/private mode
5. Test on different device/network

---

**Need More Help?**

If these solutions don't resolve your issue, please contact our support team at support@screenshottocode.com with:
- Detailed description of the problem
- Steps you've already tried  
- Browser and system information
- Screenshots of any error messages

We're here to help you succeed! 🚀
