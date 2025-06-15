"""
Test script to verify the Flask application setup.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_flask_app():
    """Test if the Flask application can be created and configured."""
    try:
        from app import create_app, db
        
        # Create and configure the test app
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        # Initialize the database
        with app.app_context():
            db.create_all()
            logger.info("Database tables created successfully.")
        
        # Test the root endpoint
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            logger.info(f"Root endpoint response: {response.get_json()}")
            
            # Test health check
            response = client.get('/health')
            assert response.status_code == 200
            assert response.get_json()['status'] == 'healthy'
            logger.info("Health check passed.")
        
        logger.info("All tests passed!")
        return True
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == '__main__':
    # Load environment variables
    load_dotenv()
    
    # Run the test
    success = test_flask_app()
    sys.exit(0 if success else 1)
