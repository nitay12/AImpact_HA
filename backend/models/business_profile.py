#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Business Profile Models
Defines data structures for business characteristics used in requirement matching.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class SpecialFeature(str, Enum):
    """Special business features that affect regulatory requirements."""
    GAS_USAGE = "gas_usage"
    DELIVERY = "delivery" 
    ALCOHOL = "alcohol"
    MEAT = "meat"


class BusinessProfile(BaseModel):
    """
    Complete business profile for regulatory requirement matching.
    Based on questionnaire data from משימה.md requirements.
    """
    
    # Core business characteristics
    size_sqm: int = Field(
        ..., 
        gt=0, 
        le=10000,
        description="Business size in square meters"
    )
    
    capacity_people: int = Field(
        ..., 
        gt=0, 
        le=5000,
        description="Maximum number of people (seats/capacity)"
    )
    
    # Special features from questionnaire
    special_features: List[SpecialFeature] = Field(
        default_factory=list,
        description="Special business features that affect requirements"
    )
    
    # Business type (fixed for this project)
    business_type: str = Field(
        default="restaurant",
        description="Type of business (restaurant/cafe/bar)"
    )
    
    # Optional metadata
    business_name: Optional[str] = Field(
        None,
        description="Business name for personalized reports"
    )
    
    additional_info: Optional[str] = Field(
        None,
        description="Additional business information"
    )

    @validator('special_features')
    def validate_features(cls, v):
        """Ensure special features are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Special features must be unique")
        return v

    @validator('size_sqm')
    def validate_size_reasonable(cls, v):
        """Ensure business size is reasonable for restaurant."""
        if v > 5000:  # Very large restaurant
            raise ValueError("Business size seems unusually large for a restaurant")
        return v

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True


class QuestionnaireResponse(BaseModel):
    """
    Raw questionnaire response data before processing into BusinessProfile.
    Matches the digital questionnaire structure from משימה.md.
    """
    
    # Hebrew field names matching questionnaire
    business_size_sqm: int = Field(..., alias="גודל העסק")
    seating_capacity: int = Field(..., alias="מספר מקומות ישיבה") 
    
    # Special features checkboxes
    uses_gas: bool = Field(default=False, alias="שימוש בגז")
    serves_meat: bool = Field(default=False, alias="מגיש בשר") 
    offers_delivery: bool = Field(default=False, alias="משלוחים")
    serves_alcohol: bool = Field(default=False, alias="משקאות משכרים")
    
    # Optional fields
    business_name: Optional[str] = Field(None, alias="שם העסק")
    additional_notes: Optional[str] = Field(None, alias="הערות נוספות")

    def to_business_profile(self) -> BusinessProfile:
        """Convert questionnaire response to BusinessProfile."""
        special_features = []
        
        if self.uses_gas:
            special_features.append(SpecialFeature.GAS_USAGE)
        if self.serves_meat:
            special_features.append(SpecialFeature.MEAT)
        if self.offers_delivery:
            special_features.append(SpecialFeature.DELIVERY)
        if self.serves_alcohol:
            special_features.append(SpecialFeature.ALCOHOL)
        
        return BusinessProfile(
            size_sqm=self.business_size_sqm,
            capacity_people=self.seating_capacity,
            special_features=special_features,
            business_name=self.business_name,
            additional_info=self.additional_notes
        )

    class Config:
        """Pydantic configuration."""
        populate_by_name = True
        validate_assignment = True


class BusinessProfileSummary(BaseModel):
    """Summary view of business profile for reports and logging."""
    
    size_category: str = Field(..., description="Small/Medium/Large")
    capacity_category: str = Field(..., description="Low/Medium/High")
    feature_count: int = Field(..., description="Number of special features")
    complexity_score: float = Field(..., description="Business complexity (0-1)")
    
    @classmethod
    def from_profile(cls, profile: BusinessProfile) -> 'BusinessProfileSummary':
        """Create summary from full business profile."""
        
        # Size categorization
        if profile.size_sqm <= 100:
            size_category = "Small"
        elif profile.size_sqm <= 300:
            size_category = "Medium"
        else:
            size_category = "Large"
            
        # Capacity categorization  
        if profile.capacity_people <= 50:
            capacity_category = "Low"
        elif profile.capacity_people <= 200:
            capacity_category = "Medium"
        else:
            capacity_category = "High"
            
        # Complexity calculation
        base_complexity = min(profile.size_sqm / 1000, 0.5)  # Size component
        capacity_complexity = min(profile.capacity_people / 500, 0.3)  # Capacity component
        feature_complexity = len(profile.special_features) * 0.05  # Feature component
        
        complexity_score = min(base_complexity + capacity_complexity + feature_complexity, 1.0)
        
        return cls(
            size_category=size_category,
            capacity_category=capacity_category,
            feature_count=len(profile.special_features),
            complexity_score=complexity_score
        )


# Sample business profiles for testing
SAMPLE_PROFILES = {
    "small_simple": BusinessProfile(
        size_sqm=80,
        capacity_people=30,
        special_features=[],
        business_name="קפה קטן"
    ),
    
    "medium_gas": BusinessProfile(
        size_sqm=150,
        capacity_people=80,
        special_features=[SpecialFeature.GAS_USAGE],
        business_name="מסעדה בינונית"
    ),
    
    "large_complex": BusinessProfile(
        size_sqm=400,
        capacity_people=200,
        special_features=[
            SpecialFeature.GAS_USAGE, 
            SpecialFeature.DELIVERY, 
            SpecialFeature.ALCOHOL
        ],
        business_name="מסעדה גדולה"
    ),
    
    "edge_case_chapter5": BusinessProfile(
        size_sqm=150,  # Exactly at Chapter 5 threshold
        capacity_people=50,  # Exactly at capacity threshold
        special_features=[SpecialFeature.GAS_USAGE],
        business_name="בדיקת גבול פרק 5"
    ),
    
    "edge_case_chapter6": BusinessProfile(
        size_sqm=151,  # Just over Chapter 5 threshold
        capacity_people=51,  # Just over capacity threshold  
        special_features=[SpecialFeature.GAS_USAGE, SpecialFeature.DELIVERY],
        business_name="בדיקת גבול פרק 6"
    )
}