# wsgi.py

from app import app  # Import the Flask app from your main application file (e.g., app.py)

if __name__ == "__main__":
    app.run(debug=True)  # This will run the app locally if you run wsgi.py directly, though Gunicorn will handle it in production.
