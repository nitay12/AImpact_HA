#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI Endpoints for Requirement Matching
REST API for business questionnaire and requirement matching services.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

from models.business_profile import BusinessProfile, QuestionnaireResponse, SAMPLE_PROFILES
from matching.engine import RequirementMatcher, create_matcher
from matching.rules import RuleProcessor
from matching.formatter import RequirementFormatter, MatchedRequirements, create_formatter
from services.ai_service import AIService, ReportGenerationRequest, AIReportResponse, get_ai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances (initialized on startup)
matcher: Optional[RequirementMatcher] = None
rule_processor = RuleProcessor()
formatter = create_formatter()


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    regulatory_data_loaded: bool
    total_requirements: int
    service_version: str


class MatchingStatsResponse(BaseModel):
    """Statistics about loaded regulatory data."""
    stats: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None


def get_matcher() -> RequirementMatcher:
    """Dependency to get matcher instance."""
    if matcher is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Regulatory data not loaded. Check service configuration."
        )
    return matcher


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title="AImpact HA - Business Licensing API",
        description="API for matching Israeli fire safety regulations to business characteristics",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup."""
        global matcher
        
        logger.info("Initializing AImpact HA services...")
        
        # Try to load regulatory data
        backend_dir = Path(__file__).parent.parent
        data_file = backend_dir / "fire_safety_regulatory_data.json"
        
        if data_file.exists():
            matcher = create_matcher(str(data_file))
            logger.info("Regulatory data loaded successfully")
        else:
            logger.warning(f"Regulatory data file not found: {data_file}")
            logger.warning("Run data extraction first: python backend/data/data_extractor.py")
    
    @app.get("/", response_model=Dict[str, str])
    async def root():
        """Root endpoint."""
        return {
            "service": "AImpact HA - Business Licensing API",
            "status": "running",
            "docs": "/docs"
        }
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint."""
        has_data = matcher is not None
        requirement_count = 0
        
        if has_data:
            stats = matcher.get_statistics()
            requirement_count = stats.get('total_requirements', 0)
        
        return HealthResponse(
            status="healthy" if has_data else "degraded",
            regulatory_data_loaded=has_data,
            total_requirements=requirement_count,
            service_version="1.0.0"
        )
    
    @app.get("/stats", response_model=MatchingStatsResponse)
    async def get_stats(matcher_instance: RequirementMatcher = Depends(get_matcher)):
        """Get statistics about loaded regulatory data."""
        stats = matcher_instance.get_statistics()
        return MatchingStatsResponse(stats=stats)
    
    @app.post("/api/questionnaire/submit", response_model=MatchedRequirements)
    async def submit_questionnaire(
        questionnaire: QuestionnaireResponse,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """
        Submit questionnaire and get matched requirements.
        
        This is the main endpoint that processes questionnaire responses
        and returns applicable regulatory requirements.
        """
        try:
            # Convert questionnaire to business profile
            business_profile = questionnaire.to_business_profile()
            
            logger.info(f"Processing questionnaire for: {business_profile.size_sqm}m², "
                       f"{business_profile.capacity_people} people")
            
            # Match requirements
            raw_matches = matcher_instance.match_requirements(business_profile)
            
            # Process through business rules
            processed_matches = rule_processor.process_matches(raw_matches, business_profile)
            
            # Get conflicts for reporting
            conflicts = rule_processor.get_conflict_report()
            
            # Format for AI consumption
            formatted_result = formatter.format_for_ai(
                processed_matches, 
                business_profile, 
                conflicts
            )
            
            # Reset processor for next request
            rule_processor.reset_conflicts()
            
            logger.info(f"Successfully processed questionnaire. "
                       f"Found {len(processed_matches)} applicable requirements")
            
            return formatted_result
            
        except ValidationError as e:
            logger.error(f"Questionnaire validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid questionnaire data: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error processing questionnaire: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during questionnaire processing"
            )
    
    @app.post("/api/match-requirements", response_model=MatchedRequirements)
    async def match_requirements_direct(
        business_profile: BusinessProfile,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """
        Direct requirement matching with BusinessProfile.
        
        Alternative endpoint for direct API usage without questionnaire conversion.
        """
        try:
            logger.info(f"Direct matching for: {business_profile.size_sqm}m², "
                       f"{business_profile.capacity_people} people")
            
            # Match requirements
            raw_matches = matcher_instance.match_requirements(business_profile)
            
            # Process through business rules
            processed_matches = rule_processor.process_matches(raw_matches, business_profile)
            
            # Get conflicts
            conflicts = rule_processor.get_conflict_report()
            
            # Format for AI
            formatted_result = formatter.format_for_ai(
                processed_matches,
                business_profile,
                conflicts
            )
            
            # Reset processor
            rule_processor.reset_conflicts()
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"Error in direct matching: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error during requirement matching"
            )
    
    @app.get("/api/sample-profiles", response_model=Dict[str, BusinessProfile])
    async def get_sample_profiles():
        """Get sample business profiles for testing."""
        return SAMPLE_PROFILES
    
    @app.post("/api/sample-profiles/{profile_name}", response_model=MatchedRequirements)
    async def test_sample_profile(
        profile_name: str,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """Test matching with a sample profile."""
        if profile_name not in SAMPLE_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample profile '{profile_name}' not found"
            )
        
        business_profile = SAMPLE_PROFILES[profile_name]
        
        # Match requirements
        raw_matches = matcher_instance.match_requirements(business_profile)
        processed_matches = rule_processor.process_matches(raw_matches, business_profile)
        conflicts = rule_processor.get_conflict_report()
        
        # Format result
        formatted_result = formatter.format_for_ai(
            processed_matches,
            business_profile, 
            conflicts
        )
        
        rule_processor.reset_conflicts()
        
        return formatted_result
    
    @app.get("/api/ai-prompt-context/{profile_name}", response_model=Dict[str, str])
    async def get_ai_prompt_context(
        profile_name: str,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """
        Get AI prompt context for a sample profile.
        Useful for testing AI integration.
        """
        if profile_name not in SAMPLE_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample profile '{profile_name}' not found"
            )
        
        business_profile = SAMPLE_PROFILES[profile_name]
        
        # Process requirements
        raw_matches = matcher_instance.match_requirements(business_profile)
        processed_matches = rule_processor.process_matches(raw_matches, business_profile)
        conflicts = rule_processor.get_conflict_report()
        
        # Format for AI
        formatted_result = formatter.format_for_ai(
            processed_matches,
            business_profile,
            conflicts
        )
        
        # Create AI prompt context
        prompt_context = formatter.create_ai_prompt_context(formatted_result)
        
        rule_processor.reset_conflicts()
        
        return {
            "profile_name": profile_name,
            "ai_prompt_context": prompt_context,
            "total_requirements": len(processed_matches)
        }
    
    @app.post("/api/generate-report", response_model=AIReportResponse)
    async def generate_report(
        questionnaire: QuestionnaireResponse,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """
        Generate AI-powered compliance report from questionnaire.
        
        This is the main AI integration endpoint that takes a questionnaire,
        matches requirements, and generates a personalized Hebrew report.
        """
        try:
            ai_service = get_ai_service()
            
            # Convert questionnaire to business profile
            business_profile = questionnaire.to_business_profile()
            
            logger.info(f"Generating AI report for: {business_profile.size_sqm}m², "
                       f"{business_profile.capacity_people} people")
            
            # Match requirements
            raw_matches = matcher_instance.match_requirements(business_profile)
            processed_matches = rule_processor.process_matches(raw_matches, business_profile)
            conflicts = rule_processor.get_conflict_report()
            
            # Format for AI
            formatted_result = formatter.format_for_ai(
                processed_matches, 
                business_profile, 
                conflicts
            )
            
            # Create AI request
            ai_request = ReportGenerationRequest(
                business_name=questionnaire.business_name,
                business_type="מסעדה",
                hebrew_context=formatted_result.hebrew_context_full,
                requirements_summary=formatted_result.hebrew_context_summary,
                priority_requirements=formatted_result.priority_requirements,
                business_characteristics={
                    "size_sqm": business_profile.size_sqm,
                    "capacity_people": business_profile.capacity_people,
                    "special_characteristics": list(business_profile.special_characteristics)
                }
            )
            
            # Generate report using AI
            report_response = await ai_service.generate_report(ai_request)
            
            # Reset processor
            rule_processor.reset_conflicts()
            
            logger.info(f"Successfully generated AI report. "
                       f"Tokens: {report_response.tokens_used}, "
                       f"Time: {report_response.processing_time:.2f}s")
            
            return report_response
            
        except ValueError as e:
            logger.error(f"AI service configuration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not configured. Please set OPENAI_API_KEY environment variable."
            )
        except Exception as e:
            logger.error(f"Error generating AI report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate AI report: {str(e)}"
            )
    
    @app.post("/api/generate-report/sample/{profile_name}", response_model=AIReportResponse)
    async def generate_report_sample(
        profile_name: str,
        matcher_instance: RequirementMatcher = Depends(get_matcher)
    ):
        """Generate AI report for a sample profile - useful for testing."""
        if profile_name not in SAMPLE_PROFILES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sample profile '{profile_name}' not found"
            )
        
        try:
            ai_service = get_ai_service()
            business_profile = SAMPLE_PROFILES[profile_name]
            
            # Process requirements
            raw_matches = matcher_instance.match_requirements(business_profile)
            processed_matches = rule_processor.process_matches(raw_matches, business_profile)
            conflicts = rule_processor.get_conflict_report()
            
            # Format for AI
            formatted_result = formatter.format_for_ai(
                processed_matches,
                business_profile,
                conflicts
            )
            
            # Create AI request
            ai_request = ReportGenerationRequest(
                business_name=f"דוגמה - {profile_name}",
                business_type="מסעדה",
                hebrew_context=formatted_result.hebrew_context_full,
                requirements_summary=formatted_result.hebrew_context_summary,
                priority_requirements=formatted_result.priority_requirements,
                business_characteristics={
                    "size_sqm": business_profile.size_sqm,
                    "capacity_people": business_profile.capacity_people,
                    "special_characteristics": list(business_profile.special_characteristics)
                }
            )
            
            # Generate report
            report_response = await ai_service.generate_report(ai_request)
            
            rule_processor.reset_conflicts()
            
            return report_response
            
        except ValueError as e:
            logger.error(f"AI service configuration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not configured. Please set OPENAI_API_KEY environment variable."
            )
        except Exception as e:
            logger.error(f"Error generating sample AI report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate AI report: {str(e)}"
            )
    
    @app.get("/api/ai/test-connection")
    async def test_ai_connection():
        """Test AI service connection and configuration."""
        try:
            ai_service = get_ai_service()
            connection_ok = await ai_service.test_connection()
            
            return {
                "ai_service_available": connection_ok,
                "model": ai_service.model,
                "status": "connected" if connection_ok else "failed"
            }
        except ValueError as e:
            return {
                "ai_service_available": False,
                "error": str(e),
                "status": "configuration_error"
            }
        except Exception as e:
            return {
                "ai_service_available": False,
                "error": str(e),
                "status": "connection_error"
            }
    
    return app


# Create the FastAPI app instance
app = create_app()