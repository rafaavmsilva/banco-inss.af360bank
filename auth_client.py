import requests
from flask import session, redirect, request
from urllib.parse import quote

class AuthClient:
    def __init__(self, auth_server_url, app_name):
        self.auth_server_url = auth_server_url
        self.app_name = app_name

    def get_authorization_url(self, redirect_uri):
        """Generate the authorization URL for the auth server"""
        encoded_redirect = quote(redirect_uri)
        return f"{self.auth_server_url}/login?redirect_uri={encoded_redirect}&app_name={self.app_name}"
    
    def init_app(self, app):
        self.app = app

        @app.route('/auth')
        def auth():
            """Handle the authentication token"""
            token = request.args.get('token')
            if not token:
                return 'No token provided', 400

            # Verify token with auth server
            verify_response = requests.post(
                f"{self.auth_server_url}/api/verify_token",
                json={
                    'token': token,
                    'app_name': self.app_name
                }
            )

            if verify_response.status_code != 200:
                return 'Token verification failed', 400

            token_data = verify_response.json()
            if not token_data.get('valid'):
                return 'Invalid token', 400

            session['authenticated'] = True
            session['user_id'] = token_data.get('data', {}).get('user_id')
            session['access_token'] = token
            session['user_role'] = token_data.get('data', {}).get('role')

            # Redirect to dashboard or stored next_url
            next_url = session.get('next_url')
            if next_url:
                session.pop('next_url', None)
                return redirect(next_url)
            return redirect('/')

        @app.route('/auth/callback')
        def auth_callback():
            """Handle the authentication callback from the auth server"""
            code = request.args.get('code')
            if not code:
                return 'Authentication failed', 400

            # Exchange code for access token
            token_response = requests.post(
                f"{self.auth_server_url}/api/token",
                json={
                    'code': code,
                    'app_name': self.app_name
                }
            )

            if token_response.status_code != 200:
                return 'Token exchange failed', 400

            token_data = token_response.json()
            session['authenticated'] = True
            session['user_id'] = token_data.get('user_id')
            session['access_token'] = token_data.get('access_token')
            session['user_role'] = token_data.get('role')

            return redirect('/')

