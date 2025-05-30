from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class IntentCategory(str, Enum):
    DINING = "dining"
    TRAVEL = "travel"
    GIFTING = "gifting"
    CAB_BOOKING = "cab_booking"
    OTHER = "other"

class EntityModel(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    destination: Optional[str] = None
    cuisine: Optional[str] = None
    party_size: Optional[int] = None
    budget: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    accommodation_type: Optional[str] = None
    duration: Optional[str] = None
    gift_type: Optional[str] = None
    recipient: Optional[str] = None
    vehicle_type: Optional[str] = None
    pickup_location: Optional[str] = None
    additional_requirements: Optional[List[str]] = None

class WebSearchResult(BaseModel):
    title: str
    url: str
    snippet: str

class AssistantResponse(BaseModel):
    intent_category: IntentCategory
    entities: EntityModel
    confidence_score: float = Field(ge=0.0, le=1.0)
    follow_up_questions: List[str] = []
    web_search_results: Optional[List[WebSearchResult]] = None
    reasoning: Optional[str] = None

class UserRequest(BaseModel):
    user_input: str