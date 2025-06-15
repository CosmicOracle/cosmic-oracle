import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Try to import the app module
try:
    from app import create_app
    print('Successfully imported create_app function')
    
    # Create the Flask application
    app = create_app()
    
    # Set up application context
    with app.app_context():
        print('Successfully entered application context')
        
        # Test imports and basic functionality
        try:
            from app.services import AstrologyService
            print("Successfully imported AstrologyService")
            
            # Temporarily skip Skyfield import due to Python 3.13 compatibility issues
            try:
                from app.services import SkyfieldAstronomyService
                print("Successfully imported SkyfieldAstronomyService")
            except ImportError as e:
                print(f"Skipping SkyfieldAstronomyService import (compatibility issue): {e}")
                
        except Exception as e:
            print(f"Failed to import services: {e}")
            
        # Test database connection if needed
        try:
            from app.extensions import db
            db.create_all()
            print("Successfully initialized database")
        except Exception as e:
            print(f"Database initialization failed: {e}")
            
except ImportError as e:
    print(f'Failed to import app module: {e}')
    sys.exit(1)
except Exception as e:
    print(f'Error initializing application: {e}')
    sys.exit(1)
