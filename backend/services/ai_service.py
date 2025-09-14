#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Service for Report Generation
Handles LLM integration for generating personalized regulatory compliance reports.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio

from openai import AsyncOpenAI
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ReportGenerationRequest(BaseModel):
    """Request model for AI report generation."""
    business_name: Optional[str] = None
    business_type: str = "מסעדה"
    hebrew_context: str
    requirements_summary: str
    priority_requirements: list
    business_characteristics: dict


class AIReportResponse(BaseModel):
    """Response model for AI-generated report."""
    report_content: str
    generation_timestamp: str
    model_used: str
    tokens_used: Optional[int] = None
    processing_time: Optional[float] = None


class AIService:
    """Service for AI-powered report generation using OpenAI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize AI service.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: OpenAI model to use for generation
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info(f"AI Service initialized with model: {model}")
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for regulatory report generation."""
        return """אתה מומחה ברגולציות בטיחות אש למסעדות בישראל. המטרה שלך היא ליצור דוח ברור ומעשי לבעלי עסקים.

חשוב מאוד:
- כתב בעברית ברורה ונגישה
- המר "שפת חוק" לשפה עסקית מובנת
- תן המלצות מעשיות וקונקרטיות
- סדר לפי עדיפות (דחוף/חשוב/רצוי)
- הוסף הערכת עלות כללית כשאפשר
- הבהר את הצעדים הבאים הנדרשים

מבנה הדוח:
1. סיכום מנהלים (2-3 שורות)
2. דרישות דחופות (אם יש)
3. דרישות חובה
4. דרישות רצויות
5. המלצות לביצוע
6. איש קשר מומלץ (רשויות/מומחים)

הקפד על טון מקצועי אך ידידותי."""

    def _create_user_prompt(self, request: ReportGenerationRequest) -> str:
        """Create the user prompt with business-specific data."""
        business_info = f"""פרטי העסק:
- סוג עסק: {request.business_type}
- שם העסק: {request.business_name or 'לא צוין'}
- גודל: {request.business_characteristics.get('size_sqm', 'לא צוין')} מ"ר
- תפוסה: {request.business_characteristics.get('capacity_people', 'לא צוין')} אנשים
- מאפיינים מיוחדים: {', '.join(request.business_characteristics.get('special_characteristics', []))}
"""

        return f"""{business_info}

נתוני הרגולציה החלים על העסק:
{request.hebrew_context}

סיכום דרישות בעדיפות גבוהה:
{request.requirements_summary}

דרישות עדיפות ראשונה:
{chr(10).join([f"• {req.get('hebrew_text', str(req))}" for req in request.priority_requirements[:5]])}

בהתבסס על הנתונים האלה, צור דוח מותאם אישית לבעל העסק."""

    async def generate_report(self, request: ReportGenerationRequest) -> AIReportResponse:
        """
        Generate a personalized regulatory compliance report.
        
        Args:
            request: Report generation request with business data and regulatory context
            
        Returns:
            AI-generated report response
        """
        start_time = datetime.now()
        
        try:
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(request)
            
            logger.info(f"Generating report for business type: {request.business_type}")
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
                top_p=0.9,
            )
            
            # Extract response
            report_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Report generated successfully. Tokens: {tokens_used}, Time: {processing_time:.2f}s")
            
            return AIReportResponse(
                report_content=report_content,
                generation_timestamp=datetime.now().isoformat(),
                model_used=self.model,
                tokens_used=tokens_used,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error generating AI report: {str(e)}")
            raise Exception(f"Failed to generate report: {str(e)}")
    
    async def generate_simple_report(
        self, 
        business_profile: dict, 
        requirements_text: str
    ) -> str:
        """
        Simplified report generation for quick testing.
        
        Args:
            business_profile: Basic business characteristics
            requirements_text: Raw requirements text in Hebrew
            
        Returns:
            Generated report as string
        """
        try:
            prompt = f"""תן דוח קצר ומעשי למסעדה עם המאפיינים הבאים:
- גודל: {business_profile.get('size_sqm', 'לא צוין')} מ"ר
- תפוסה: {business_profile.get('capacity_people', 'לא צוין')} אנשים

דרישות רגולטוריות:
{requirements_text[:1000]}...

צור דוח של 200-300 מילים בעברית עם המלצות מעשיות."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in simple report generation: {str(e)}")
            return f"שגיאה ביצירת הדוח: {str(e)}"
    
    async def test_connection(self) -> bool:
        """Test AI service connection."""
        try:
            # Simple test call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "שלום, בדיקה קצרה"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"AI service connection test failed: {e}")
            return False


# Factory function for dependency injection
def create_ai_service() -> AIService:
    """Create AI service instance with default configuration."""
    return AIService()


# Global instance (will be initialized with environment variables)
_ai_service_instance: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service instance."""
    global _ai_service_instance
    
    if _ai_service_instance is None:
        _ai_service_instance = create_ai_service()
    
    return _ai_service_instance