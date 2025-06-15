# cosmic-oracle-backend/run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Running in debug mode. For production, use a WSGI server like Gunicorn.
    app.run(host='0.0.0.0', port=5000, debug=True)