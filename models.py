from pydantic import BaseModel, Field
from typing import Optional


class InsuranceDataResponse(BaseModel):
    """Response model for extracted insurance data"""
    name: Optional[str] = Field(None, description="Policy holder name")
    policy_number: Optional[str] = Field(None, description="Policy number or ID")
    email: Optional[str] = Field(None, description="Email address")
    policy_name: Optional[str] = Field(None, description="Insurance plan/product name")
    plan_type: Optional[str] = Field(None, description="Type of insurance plan")
    sum_assured: Optional[str] = Field(None, description="Coverage amount")
    room_rent_limit: Optional[str] = Field(None, description="Room rent limit per day")
    waiting_period: Optional[str] = Field(None, description="Waiting period duration")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
