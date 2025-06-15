# app/models/billing_models.py
"""
Pydantic Models for the Billing API.
"""
from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

class CreateCustomerRequest(BaseModel):
    name: Optional[str] = Field(None, example="John Doe")
    metadata: Optional[Dict[str, str]] = Field(None, example={"user_id": "123"})

class CreateCheckoutRequest(BaseModel):
    price_id: str = Field(..., example="price_1234567890")
    success_url: AnyHttpUrl = Field(..., example="https://yourapp.com/payment-success")
    cancel_url: AnyHttpUrl = Field(..., example="https://yourapp.com/payment-cancelled")
    metadata: Optional[Dict[str, str]] = Field(None, example={"user_id": "123"})

class CreatePortalRequest(BaseModel):
    return_url: AnyHttpUrl = Field(..., example="https://yourapp.com/account")

class WebhookRequest(BaseModel):
    payload: bytes
    signature: str

class PaymentRecord(BaseModel):
    id: str
    customer_id: str
    amount: int
    currency: str
    status: str
    created_at: datetime
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class Invoice(BaseModel):
    id: str
    customer_id: str
    subscription_id: Optional[str] = None
    amount_due: int
    amount_paid: int
    currency: str
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    description: Optional[str] = None
    pdf_url: Optional[str] = None

class BillingHistory(BaseModel):
    customer_id: str
    invoices: List[Invoice]
    payments: List[PaymentRecord]
    total_pages: int
    current_page: int

class SubscriptionStatus(BaseModel):
    id: str
    customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class BillingCustomer(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime
    currency: Optional[str] = None
    balance: int = 0
    metadata: Optional[Dict[str, Any]] = None

class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = Field(True, description="Cancel at the end of the current period")
