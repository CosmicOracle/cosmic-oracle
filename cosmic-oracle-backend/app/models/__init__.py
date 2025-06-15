# app/models/__init__.py

# Import all your model classes here to make them accessible when importing from app.models
from .user import User
from .birth_data import BirthData # Assuming you have this model for User.birth_data
from .journal_entry import JournalEntry
from .saved_tarot_reading import SavedTarotReading
from .numerology_report import NumerologyReport
from .subscription import Subscription # For User.subscriptions
from .payment_history import PaymentHistory # For User.payment_history
from .user_subscription import UserSubscription # For User.user_subscription
from .prediction import Prediction # Added for data analysis
from .data_source import DataSource # Added for data analysis

# If you uncommented UserPreference in User model, you'd add:
# from .user_preference import UserPreference
