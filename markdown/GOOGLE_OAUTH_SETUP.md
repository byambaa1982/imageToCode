# Google OAuth Setup Guide

Google OAuth integration has been successfully added to your Screenshot to Code application!

## What Was Implemented

1. ✅ **Authlib Library** - Installed for OAuth2 support
2. ✅ **OAuth Configuration** - Added to `config.py` and `.env`
3. ✅ **Database Changes** - Added OAuth fields to Account model:
   - `oauth_provider` - Provider name (e.g., 'google')
   - `oauth_id` - Provider's user ID
   - `oauth_extra` - JSON string for extra OAuth data
   - `password_hash` - Now nullable for OAuth-only users
4. ✅ **OAuth Routes** - Added `/auth/google/login` and `/auth/google/callback`
5. ✅ **UI Updates** - Added "Sign in with Google" buttons to login and register pages
6. ✅ **Database Migration** - Applied successfully

## Important: Update Google OAuth Redirect URIs

⚠️ **Action Required:** Your Google OAuth credentials are configured for port 4242, but your Flask app runs on port 5000.

### Option 1: Update Google Cloud Console (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to: **APIs & Services > Credentials**
3. Click on your OAuth 2.0 Client ID
4. Under "Authorized redirect URIs", add:
   - `http://localhost:5000/auth/google/callback`
   - `http://127.0.0.1:5000/auth/google/callback`
5. Click **Save**

### Option 2: Change Flask Port to 4242

Alternatively, you can run Flask on port 4242 instead:

```powershell
# In app.py, change port to 4242:
app.run(host='0.0.0.0', port=4242, debug=True)
```

## How Google OAuth Works

1. User clicks "Sign in with Google" button
2. User is redirected to Google's login page
3. After successful login, Google redirects back to `/auth/google/callback`
4. Your app receives user info (email, name, etc.)
5. If user exists with that email, they're logged in
6. If new user, an account is created automatically with:
   - Email from Google
   - Username derived from email
   - Email automatically verified (no verification email needed)
   - 3.00 free credits

## Features Implemented

- **Account Linking**: If a user signs up traditionally then later uses Google OAuth with the same email, their accounts are automatically linked
- **Auto-Verification**: Users who sign up via Google have `email_verified=True` automatically
- **No Password Required**: OAuth users don't need to set a password
- **Error Handling**: Comprehensive error handling for OAuth failures
- **Welcome Email**: Sent automatically to verified OAuth users

## Testing OAuth Login

After updating the redirect URIs:

1. Start your Flask app: `.\venv\Scripts\python app.py`
2. Navigate to: http://localhost:5000/auth/login
3. Click "Sign in with Google"
4. Log in with your Google account
5. You should be redirected back and logged in automatically

## Troubleshooting

### "redirect_uri_mismatch" Error
- The redirect URI in Google Console doesn't match your app
- Make sure to add `http://localhost:5000/auth/google/callback`

### "insecure_transport" Error
- OAuth requires HTTPS in production
- For local development, Authlib allows HTTP for localhost

### User Not Found After OAuth Login
- Check that the callback route is properly receiving user info
- Check Flask logs for any errors

## Production Deployment

For production (datalogichub.com), make sure to:

1. Add production redirect URI in Google Console:
   - `https://www.datalogichub.com/auth/google/callback`
2. Use HTTPS (required by Google for production)
3. Keep OAuth credentials secret (already in `.env`)

## Security Notes

- OAuth credentials are stored in `.env` (git-ignored)
- OAuth tokens are handled by Authlib securely
- User data from Google is validated before creating accounts
- Email uniqueness is enforced at database level

## Next Steps

1. Update Google OAuth redirect URIs to port 5000
2. Test the Google login flow
3. Verify that new users are created correctly
4. Test account linking with existing email
5. Deploy to production when ready

Enjoy your new Google OAuth integration! 🎉
