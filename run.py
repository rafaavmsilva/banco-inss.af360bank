from app import app

# This is the gunicorn application factory
def create_app():
    return app

if __name__ == "__main__":
    app.run()
