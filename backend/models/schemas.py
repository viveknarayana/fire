from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

class FireDetectionResponse(BaseModel):
    message: str
    frame: int
    user_uuid: str
    fire_detected: bool
    confidence_score: float
    user_email: Optional[EmailStr] = None
    supabase_url: Optional[str] = None
    email_alert: Optional[str] = None
    supabase_error: Optional[str] = None