from app import create_app, db
from app.models import DataSource, Prediction, User
from datetime import datetime, timedelta
import random
import json

def seed_data():
    """Seed the database with test data for Prediction and DataSource models"""
    print("Starting database seeding...")
    
    # Create a test user if none exists
    user = User.query.filter_by(email="test@example.com").first()
    if not user:
        user = User(email="test@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        print(f"Created test user with ID: {user.id}")
    
    # Create data sources
    data_sources = [
        {
            "name": "Astrological API",
            "type": "api",
            "description": "External API providing astrological predictions and data",
            "url": "https://api.astrology-example.com",
            "apiKey": "sample_key_123",
            "status": "active",
            "reliability": 0.85,
            "lastUpdated": datetime.utcnow() - timedelta(days=2),
            "config": {"version": "v2", "endpoints": ["predictions", "transits"]}
        },
        {
            "name": "Financial Market Data",
            "type": "database",
            "description": "Historical financial market data for correlation analysis",
            "url": "jdbc:postgresql://finance-db.example.com:5432/market_data",
            "status": "active",
            "reliability": 0.95,
            "lastUpdated": datetime.utcnow() - timedelta(days=1),
            "config": {"tables": ["stocks", "forex", "commodities"]}
        },
        {
            "name": "Social Media Sentiment",
            "type": "api",
            "description": "Social media sentiment analysis for trend prediction",
            "url": "https://api.sentiment-analysis.com",
            "apiKey": "sample_key_456",
            "status": "inactive",
            "reliability": 0.72,
            "lastUpdated": datetime.utcnow() - timedelta(days=15),
            "config": {"platforms": ["twitter", "reddit", "facebook"]}
        },
        {
            "name": "Historical Events Database",
            "type": "file",
            "description": "CSV files containing historical events for pattern matching",
            "url": "/data/historical_events/",
            "status": "active",
            "reliability": 0.88,
            "lastUpdated": datetime.utcnow() - timedelta(days=30),
            "config": {"format": "csv", "update_frequency": "monthly"}
        },
        {
            "name": "Weather Patterns API",
            "type": "api",
            "description": "Weather data for correlation with astrological events",
            "url": "https://api.weather-data.com",
            "apiKey": "sample_key_789",
            "status": "error",
            "reliability": 0.65,
            "lastUpdated": datetime.utcnow() - timedelta(days=5),
            "config": {"regions": ["global", "northern_hemisphere", "southern_hemisphere"]}
        }
    ]
    
    # Add data sources to database
    created_sources = []
    for source_data in data_sources:
        # Check if data source already exists
        existing = DataSource.query.filter_by(name=source_data["name"]).first()
        if not existing:
            # Convert config to JSONB format
            if "config" in source_data and source_data["config"]:
                source_data["config"] = source_data["config"]
            
            source = DataSource(**source_data)
            db.session.add(source)
            created_sources.append(source)
    
    db.session.commit()
    print(f"Created {len(created_sources)} data sources")
    
    # Get all data sources for reference
    all_sources = DataSource.query.all()
    
    # Create predictions
    prediction_types = ["financial", "political", "personal", "global", "technological"]
    categories = ["market", "election", "relationship", "climate", "innovation"]
    outcomes = ["correct", "incorrect", "pending"]
    
    # Generate predictions for the last year
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    predictions = []
    for i in range(100):  # Create 100 sample predictions
        # Randomly select attributes
        pred_type = random.choice(prediction_types)
        category = random.choice(categories)
        
        # Create random date ranges within the last year
        created_date = start_date + timedelta(days=random.randint(0, 364))
        prediction_start = created_date + timedelta(days=random.randint(1, 30))
        prediction_end = prediction_start + timedelta(days=random.randint(30, 180))
        
        # Determine outcome based on end date
        if prediction_end < datetime.utcnow():
            outcome = random.choice(["correct", "incorrect"])
        else:
            outcome = "pending"
        
        # Create prediction
        prediction = Prediction(
            type=pred_type,
            category=category,
            description=f"Sample {pred_type} prediction about {category} trends and developments",
            startDate=prediction_start,
            endDate=prediction_end,
            intensity=round(random.uniform(1, 10), 1),  # Random intensity between 1-10
            confidence=round(random.uniform(0.1, 1.0), 2),  # Random confidence between 0.1-1.0
            outcome=outcome,
            createdAt=created_date,
            updatedAt=created_date,
            user_id=user.id if random.random() > 0.3 else None,  # 70% of predictions associated with user
            data_source_id=random.choice(all_sources).id if random.random() > 0.2 else None  # 80% with data source
        )
        
        predictions.append(prediction)
    
    # Add predictions to database
    for prediction in predictions:
        db.session.add(prediction)
    
    db.session.commit()
    print(f"Created {len(predictions)} predictions")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_data()