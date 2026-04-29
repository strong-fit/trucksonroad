from pydantic import BaseModel
from typing import List, Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class InquiryCreate(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = ""
    email: str
    phone: str
    event_date: str
    event_time: Optional[str] = ""
    location: str
    guest_count: int
    event_type: str
    indoor_outdoor: Optional[str] = "Outdoor"
    selected_trucks: List[str] = []
    extras: List[str] = []
    budget: Optional[str] = ""
    remarks: Optional[str] = ""
    is_organizer: bool = False
    privacy_accepted: bool = True
    customer_type: Optional[str] = "Privatkunde"
    lang: Optional[str] = "de"


class InquiryStatusUpdate(BaseModel):
    status: str
    internal_notes: Optional[str] = ""
    assigned_employees: Optional[List[str]] = None


class CalendarBlockCreate(BaseModel):
    truck_slug: str
    date: str
    status: str = "blocked"
    notes: Optional[str] = ""


class FAQCreate(BaseModel):
    question_de: str
    answer_de: str
    question_en: str
    answer_en: str
    order: int = 0


class QuickInquiryCreate(BaseModel):
    name: str
    contact: Optional[str] = ""
    event_date: Optional[str] = ""
    location: Optional[str] = ""
    guest_count: Optional[int] = 0


class MenuCategoryCreate(BaseModel):
    name_de: str
    name_en: Optional[str] = ""
    name_fr: Optional[str] = ""
    name_it: Optional[str] = ""
    truck_slug: Optional[str] = ""
    order: int = 0
    concept: Optional[str] = ""
    email: Optional[str] = ""
    phone: Optional[str] = ""


class SettingsUpdate(BaseModel):
    company_name: Optional[str] = "TrucksOnRoad"
    company_address: Optional[str] = ""
    company_phone: Optional[str] = ""
    company_email: Optional[str] = ""
    whatsapp_number: Optional[str] = ""
    social_google_business: Optional[str] = ""
    social_instagram: Optional[str] = ""
    social_facebook: Optional[str] = ""
    social_tiktok: Optional[str] = ""
    social_linkedin: Optional[str] = ""
    email_notifications: Optional[bool] = False
    notification_email: Optional[str] = ""
    smtp_host: Optional[str] = "smtp.gmail.com"
    smtp_port: Optional[int] = 587
    smtp_email: Optional[str] = ""
    smtp_password: Optional[str] = ""


class EmployeeCreate(BaseModel):
    name: str
    phone: Optional[str] = ""
    role: Optional[str] = ""
    notes: Optional[str] = ""
    is_active: Optional[bool] = True


class CustomerRegister(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    company: Optional[str] = ""
    phone: Optional[str] = ""


class CustomerProfileComplete(BaseModel):
    first_name: str
    last_name: str
    street: str
    plz: str
    city: str
    mobile: str
    company: Optional[str] = ""
