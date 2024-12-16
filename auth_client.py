import requests
from flask import session, redirect, request, url_for
from functools import wraps
from urllib.parse import quote

class AuthClient:
    def __init__(self, auth_server_url, app_name):
        self.auth_server_url = auth_server_url
        self.app_name = app_name
        self.app = None

    def init_app(self, app):
        self.app = app

        @app.route('/auth')
        def handle_auth():
            """Handle the authentication token"""
            token = request.args.get('token')
            if not token:
                return redirect(url_for('login'))

            # Verify token with auth server
            try:
                verify_response = requests.post(
                    f"{self.auth_server_url}/api/verify_token",
                    json={
                        'token': token,
                        'app_name': self.app_name
                    }
                )

                if verify_response.status_code != 200:
                    return redirect(url_for('login'))

                token_data = verify_response.json()
                if not token_data.get('valid'):
                    return redirect(url_for('login'))

                # Set session data
                session['authenticated'] = True
                session['token'] = token
                session['user_data'] = token_data.get('data', {})

                # Redirect to next_url if it exists, otherwise to dashboard
                next_url = session.pop('next_url', None)
                return redirect(next_url if next_url else url_for('dashboard'))

            except Exception as e:
                print(f"Error during token verification: {str(e)}")
                return redirect(url_for('login'))

    def login_required(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('authenticated'):
                session['next_url'] = request.url
                return redirect(self.auth_server_url + '/login?redirect_uri=' + 
                              quote(url_for('handle_auth', _external=True)) + 
                              '&app_name=' + self.app_name)
            return f(*args, **kwargs)
        return decorated_function
