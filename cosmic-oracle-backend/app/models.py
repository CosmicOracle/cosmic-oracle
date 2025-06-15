from app import db, bcrypt # bcrypt should be initialized in __init__.py
from datetime import datetime, timezone as dt_timezone # Avoid conflict with pytz.timezone

class User(db.Model):
    __tablename__ = 'users' # Explicit table name
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc))
    full_name_for_numerology = db.Column(db.String(200), nullable=True) # For numerology

    # Relationships
    # One-to-one with BirthData
    birth_data = db.relationship('BirthData', back_populates='user', uselist=False, lazy='joined', cascade="all, delete-orphan")
    # One-to-many with JournalEntry
    journal_entries = db.relationship('JournalEntry', back_populates='author', lazy='dynamic', cascade="all, delete-orphan")
    # One-to-many with SavedTarotReading
    saved_tarot_readings = db.relationship('SavedTarotReading', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")
    # One-to-many with NumerologyReport (can be one-to-one if a user only has one primary report)
    numerology_reports = db.relationship('NumerologyReport', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User id={self.id} email={self.email}>'

class BirthData(db.Model):
    __tablename__ = 'birth_data'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True) # Ensure user_id is unique
    
    birth_datetime_utc = db.Column(db.DateTime, nullable=False) # Store as UTC
    birth_location_name = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timezone_str = db.Column(db.String(100), nullable=False) # e.g., "Europe/London"

    # Calculated and stored natal data for quick retrieval
    sun_sign_key = db.Column(db.String(20))
    sun_sign_degrees = db.Column(db.Float)
    moon_sign_key = db.Column(db.String(20))
    moon_sign_degrees = db.Column(db.Float)
    rising_sign_key = db.Column(db.String(20))
    rising_sign_degrees = db.Column(db.Float)
    
    # Store full natal chart data (planets in signs and houses, aspects) as JSONB for flexibility
    # Or create separate detailed tables if complex queries are needed on this data
    natal_chart_json = db.Column(db.JSON, nullable=True) # For PostgreSQL, JSONB is better: from sqlalchemy.dialects.postgresql import JSONB

    user = db.relationship('User', back_populates='birth_data')

    def __repr__(self):
        return f'<BirthData for User {self.user_id}>'

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    entry_type = db.Column(db.String(50), nullable=False, index=True) # daily, gratitude, dream etc.
    title = db.Column(db.String(200), nullable=True) # Optional title
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc), onupdate=lambda: datetime.now(dt_timezone.utc))
    
    # Specific fields for dream journal
    dream_date = db.Column(db.Date, nullable=True) 
    dream_mood = db.Column(db.String(50), nullable=True)

    author = db.relationship('User', back_populates='journal_entries')

    def __repr__(self):
        return f'<JournalEntry id={self.id} type={self.entry_type} user_id={self.user_id}>'

class SavedTarotReading(db.Model):
    __tablename__ = 'saved_tarot_readings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    spread_type = db.Column(db.String(50), nullable=False)
    question_asked = db.Column(db.Text, nullable=True)
    cards_drawn = db.Column(db.JSON, nullable=False) # Store as list of {'card_name': 'The Fool', 'is_reversed': False, 'position_name': 'Present'}
    interpretation_notes = db.Column(db.Text, nullable=True) # User's personal notes
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc), index=True)

    user = db.relationship('User', back_populates='saved_tarot_readings')

    def __repr__(self):
        return f'<SavedTarotReading id={self.id} user_id={self.user_id} spread={self.spread_type}>'

class NumerologyReport(db.Model):
    __tablename__ = 'numerology_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    full_name_used = db.Column(db.String(200), nullable=False)
    birth_date_used = db.Column(db.Date, nullable=False) # The date used for calculation
    
    life_path_number = db.Column(db.Integer)
    expression_number = db.Column(db.Integer)
    soul_urge_number = db.Column(db.Integer)
    personality_number = db.Column(db.Integer)
    birthday_number = db.Column(db.Integer)
    # You could store more numbers (e.g., maturity, pinnacles, challenges)
    # Or a JSON field for all calculated numbers
    # all_numbers_json = db.Column(db.JSON, nullable=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(dt_timezone.utc))

    user = db.relationship('User', back_populates='numerology_reports')

    def __repr__(self):
        return f'<NumerologyReport id={self.id} user_id={self.user_id}>'

# Example for a UserPreference model (you can expand this greatly)
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    default_house_system = db.Column(db.String(50), default='Placidus')
    # Add more: preferred_theme, notification_settings (JSON), etc.

    # user = db.relationship('User', backref=db.backref('preferences', uselist=False)) # If you want backref on User
