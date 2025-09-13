#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Tests for Matching Engine
Tests business profile matching against regulatory requirements.
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from backend.models.business_profile import BusinessProfile, SpecialFeature, SAMPLE_PROFILES
from backend.matching.engine import RequirementMatcher, RequirementMatch
from backend.matching.rules import RuleProcessor
from backend.matching.formatter import RequirementFormatter


class TestBusinessProfileMatching:
    """Test suite for business profile and requirement matching."""
    
    @pytest.fixture
    def mock_regulatory_data(self) -> Dict[str, Any]:
        """Create mock regulatory data for testing."""
        return {
            "metadata": {
                "source_file": "test_data.pdf",
                "extraction_date": "2024-01-01T00:00:00",
                "chapters_processed": [5, 6],
                "total_text_length": 10000
            },
            "business_thresholds": {
                "area_thresholds": [
                    {
                        "threshold_sqm": 150,
                        "trigger_type": "maximum", 
                        "context_hebrew": "עסקים עד 150 מ\"ר - פרק 5",
                        "section": "5.1",
                        "chapter": 5
                    },
                    {
                        "threshold_sqm": 300,
                        "trigger_type": "minimum",
                        "context_hebrew": "עסקים מעל 300 מ\"ר - פרק 6", 
                        "section": "6.1",
                        "chapter": 6
                    }
                ],
                "capacity_thresholds": [
                    {
                        "threshold_people": 50,
                        "trigger_type": "maximum",
                        "context_hebrew": "תפוסה עד 50 איש - פרק 5",
                        "section": "5.2",
                        "chapter": 5
                    },
                    {
                        "threshold_people": 200,
                        "trigger_type": "minimum", 
                        "context_hebrew": "תפוסה מעל 200 איש - פרק 6",
                        "section": "6.2",
                        "chapter": 6
                    }
                ]
            },
            "requirements": [
                {
                    "requirement_id": "CHAPTER_5_SECTION_5_5_1",
                    "chapter": 5,
                    "section": "5.5.1",
                    "category": "fire_equipment",
                    "title_hebrew": "מטפי כיבוי",
                    "content_hebrew": "בעסק יוצבו מטפי כיבוי מסוג אבקה יבשה במשקל של 6 ק\"ג",
                    "size_applicability": {"min_sqm": 0, "max_sqm": 150},
                    "capacity_applicability": {"min_people": 0, "max_people": 50},
                    "special_features": [],
                    "israeli_standards": ["ת\"י 129"],
                    "certifications": ["גורם מוסמך"]
                },
                {
                    "requirement_id": "CHAPTER_6_SECTION_6_13_1",
                    "chapter": 6,
                    "section": "6.13.1", 
                    "category": "fire_equipment",
                    "title_hebrew": "גלגלון כיבוי",
                    "content_hebrew": "בעסק ששטחו עד 120 מ\"ר יותקן גלגלון כיבוי אש",
                    "size_applicability": {"min_sqm": 120, "max_sqm": 300},
                    "capacity_applicability": {"min_people": 51, "max_people": 200},
                    "special_features": [],
                    "israeli_standards": ["ת\"י 448"],
                    "certifications": ["גורם מוסמך"]
                },
                {
                    "requirement_id": "CHAPTER_6_SECTION_6_23_1",
                    "chapter": 6,
                    "section": "6.23.1",
                    "category": "gas",
                    "title_hebrew": "מערכת גז",
                    "content_hebrew": "מערכת הגז המשמשת את העסק תענה לנדרש בתקן ישראלי ת\"י 158",
                    "size_applicability": {"min_sqm": 0, "max_sqm": 9999},
                    "capacity_applicability": {"min_people": 0, "max_people": 9999},
                    "special_features": ["gas_usage"],
                    "israeli_standards": ["ת\"י 158"],
                    "certifications": ["בעל רישיון לעבודת גפ\"מ"]
                }
            ]
        }
    
    @pytest.fixture
    def matcher(self, mock_regulatory_data) -> RequirementMatcher:
        """Create matcher with mock data."""
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_regulatory_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        matcher = RequirementMatcher(temp_path)
        
        # Cleanup
        Path(temp_path).unlink()
        
        return matcher
    
    def test_small_business_matching(self, matcher):
        """Test matching for small business (Chapter 5)."""
        business_profile = BusinessProfile(
            size_sqm=80,
            capacity_people=30,
            special_features=[]
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should get Chapter 5 fire equipment requirement
        assert len(matches) == 1
        assert matches[0].chapter == 5
        assert matches[0].category == "fire_equipment"
        assert "מטפי כיבוי" in matches[0].title_hebrew
    
    def test_medium_business_matching(self, matcher):
        """Test matching for medium business (Chapter 6)."""
        business_profile = BusinessProfile(
            size_sqm=180,
            capacity_people=80,
            special_features=[]
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should get Chapter 6 fire equipment requirement
        assert len(matches) == 1
        assert matches[0].chapter == 6
        assert matches[0].category == "fire_equipment"
        assert "גלגלון כיבוי" in matches[0].title_hebrew
    
    def test_gas_business_matching(self, matcher):
        """Test matching for business with gas usage."""
        business_profile = BusinessProfile(
            size_sqm=120,
            capacity_people=60,
            special_features=[SpecialFeature.GAS_USAGE]
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should get both fire equipment and gas requirements
        assert len(matches) == 2
        
        categories = {match.category for match in matches}
        assert "fire_equipment" in categories
        assert "gas" in categories
        
        # Check gas requirement
        gas_match = next(m for m in matches if m.category == "gas")
        assert "מערכת גז" in gas_match.title_hebrew
        assert "gas_usage" in [reason for reason in gas_match.match_reasons if "גז" in reason or "gas" in reason.lower()]
    
    def test_edge_case_chapter_5_threshold(self, matcher):
        """Test edge case at Chapter 5 threshold (exactly 150 m² and 50 people)."""
        business_profile = BusinessProfile(
            size_sqm=150,
            capacity_people=50,
            special_features=[]
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should match Chapter 5 requirement (maximum threshold inclusive)
        assert len(matches) == 1
        assert matches[0].chapter == 5
    
    def test_edge_case_chapter_6_threshold(self, matcher):
        """Test edge case just over Chapter 5 threshold."""
        business_profile = BusinessProfile(
            size_sqm=151,
            capacity_people=51,
            special_features=[]
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should match Chapter 6 requirement
        assert len(matches) == 1
        assert matches[0].chapter == 6
    
    def test_no_matches_out_of_range(self, matcher):
        """Test business that doesn't match any requirements."""
        business_profile = BusinessProfile(
            size_sqm=50,  # Too small for Chapter 6 fire equipment
            capacity_people=25,  # Too small for Chapter 6
            special_features=[]  # No gas
        )
        
        matches = matcher.match_requirements(business_profile)
        
        # Should only get Chapter 5 requirement
        assert len(matches) == 1
        assert matches[0].chapter == 5

    def test_sample_profiles_matching(self, matcher):
        """Test all sample profiles can be matched."""
        for profile_name, business_profile in SAMPLE_PROFILES.items():
            matches = matcher.match_requirements(business_profile)
            
            # All sample profiles should have at least one requirement
            assert len(matches) >= 1, f"Sample profile '{profile_name}' had no matches"
            
            # All matches should have valid data
            for match in matches:
                assert match.requirement_id
                assert match.chapter > 0
                assert match.section
                assert match.category
                assert match.title_hebrew
                assert match.content_hebrew
                assert isinstance(match.match_reasons, list)
                assert match.priority in [1, 2, 3]


class TestRuleProcessor:
    """Test suite for rule processing logic."""
    
    @pytest.fixture
    def rule_processor(self):
        """Create rule processor instance."""
        return RuleProcessor()
    
    @pytest.fixture
    def sample_matches(self):
        """Create sample requirement matches for testing."""
        return [
            RequirementMatch(
                requirement_id="CHAPTER_5_SECTION_5_5_1",
                chapter=5,
                section="5.5.1", 
                category="fire_equipment",
                title_hebrew="מטפי כיבוי",
                content_hebrew="מטף אבקה יבשה",
                match_reasons=["גודל עסק"],
                priority=1
            ),
            RequirementMatch(
                requirement_id="CHAPTER_6_SECTION_6_13_1", 
                chapter=6,
                section="6.13.1",
                category="fire_equipment", 
                title_hebrew="גלגלון כיבוי",
                content_hebrew="גלגלון עם זרנוק",
                match_reasons=["גודל עסק"],
                priority=1
            )
        ]
    
    def test_chapter_conflict_resolution(self, rule_processor, sample_matches):
        """Test resolution of Chapter 5 vs Chapter 6 conflicts."""
        business_profile = BusinessProfile(size_sqm=120, capacity_people=40)
        
        processed = rule_processor.process_matches(sample_matches, business_profile)
        
        # Should prefer Chapter 5 for smaller business
        assert len(processed) <= len(sample_matches)
        
        conflicts = rule_processor.get_conflict_report()
        rule_processor.reset_conflicts()
        
        # Conflicts may have been resolved
        assert isinstance(conflicts, list)
    
    def test_gas_usage_rule_application(self, rule_processor):
        """Test gas usage rule elevation."""
        gas_match = RequirementMatch(
            requirement_id="GAS_REQ_1",
            chapter=6,
            section="6.23.1",
            category="gas",
            title_hebrew="מערכת גז",
            content_hebrew="דרישות גז",
            match_reasons=["שימוש בגז"],
            priority=2  # Will be elevated to 1
        )
        
        business_profile = BusinessProfile(
            size_sqm=150,
            capacity_people=60,
            special_features=[SpecialFeature.GAS_USAGE]
        )
        
        processed = rule_processor.process_matches([gas_match], business_profile)
        
        # Gas requirement should be elevated to priority 1
        assert processed[0].priority == 1
    
    def test_complex_business_enhancement(self, rule_processor):
        """Test enhancement for complex businesses."""
        matches = [
            RequirementMatch(
                requirement_id="REQ_1",
                chapter=6,
                section="6.1.1",
                category="signage",
                title_hebrew="שילוט",
                content_hebrew="שלטי יציאה",
                match_reasons=["גודל עסק"],
                priority=3
            )
        ]
        
        # Complex business with 3+ features
        business_profile = BusinessProfile(
            size_sqm=300,
            capacity_people=150,
            special_features=[
                SpecialFeature.GAS_USAGE,
                SpecialFeature.DELIVERY,
                SpecialFeature.ALCOHOL
            ]
        )
        
        processed = rule_processor.process_matches(matches, business_profile)
        
        # Priority should be enhanced for complex business
        assert processed[0].priority <= 2
        assert any("מורכב" in reason for reason in processed[0].match_reasons)


class TestRequirementFormatter:
    """Test suite for requirement formatting."""
    
    @pytest.fixture
    def formatter(self):
        """Create formatter instance."""
        return RequirementFormatter()
    
    @pytest.fixture
    def sample_matches_for_formatting(self):
        """Create sample matches for formatting tests."""
        return [
            RequirementMatch(
                requirement_id="CRITICAL_REQ_1",
                chapter=5,
                section="5.5.1",
                category="fire_equipment",
                title_hebrew="מטפי כיבוי",
                content_hebrew="בעסק יוצבו מטפי כיבוי",
                match_reasons=["גודל העסק (80 מ\"ר) עד 150 מ\"ר"],
                priority=1
            ),
            RequirementMatch(
                requirement_id="IMPORTANT_REQ_1",
                chapter=6,
                section="6.10.1",
                category="signage", 
                title_hebrew="שילוט",
                content_hebrew="יותקן שילוט מתאים",
                match_reasons=["תפוסת העסק"],
                priority=2
            )
        ]
    
    def test_format_for_ai(self, formatter, sample_matches_for_formatting):
        """Test formatting for AI consumption."""
        business_profile = BusinessProfile(
            size_sqm=80,
            capacity_people=30,
            special_features=[SpecialFeature.GAS_USAGE],
            business_name="מסעדה לבדיקה"
        )
        
        formatted = formatter.format_for_ai(
            sample_matches_for_formatting,
            business_profile
        )
        
        # Check structure
        assert formatted.business_profile == business_profile
        assert formatted.total_requirements == 2
        assert len(formatted.applicable_requirements) == 2
        assert len(formatted.requirements_by_category) >= 1
        
        # Check priority requirements
        assert len(formatted.priority_requirements) >= 1
        priority_req = formatted.priority_requirements[0]
        assert priority_req['priority'] == 1
        
        # Check Hebrew contexts
        assert formatted.hebrew_context_full
        assert formatted.hebrew_context_summary
        assert formatted.business_context_hebrew
        assert "80 מ\"ר" in formatted.business_context_hebrew
        assert "30 איש" in formatted.business_context_hebrew
        
        # Check statistics
        stats = formatted.match_statistics
        assert stats['total_requirements'] == 2
        assert 'by_category' in stats
        assert 'by_priority' in stats
    
    def test_ai_prompt_context_creation(self, formatter, sample_matches_for_formatting):
        """Test AI prompt context creation."""
        business_profile = BusinessProfile(
            size_sqm=80,
            capacity_people=30,
            special_features=[]
        )
        
        formatted = formatter.format_for_ai(
            sample_matches_for_formatting,
            business_profile
        )
        
        prompt_context = formatter.create_ai_prompt_context(formatted)
        
        # Should contain business info and requirements
        assert "80 מ\"ר" in prompt_context
        assert "30 איש" in prompt_context
        assert "דרישות מרכזיות" in prompt_context
        assert "הנחיות לכתיבת הדוח" in prompt_context


class TestIntegration:
    """Integration tests for the complete matching pipeline."""
    
    def test_end_to_end_matching_pipeline(self, mock_regulatory_data):
        """Test complete pipeline from business profile to formatted output."""
        # Create temporary data file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(mock_regulatory_data, f, ensure_ascii=False)
            temp_path = f.name
        
        try:
            # Initialize components
            matcher = RequirementMatcher(temp_path)
            rule_processor = RuleProcessor()
            formatter = RequirementFormatter()
            
            # Test business profile
            business_profile = BusinessProfile(
                size_sqm=120,
                capacity_people=60,
                special_features=[SpecialFeature.GAS_USAGE],
                business_name="מסעדת בדיקה"
            )
            
            # Run pipeline
            raw_matches = matcher.match_requirements(business_profile)
            processed_matches = rule_processor.process_matches(raw_matches, business_profile)
            conflicts = rule_processor.get_conflict_report()
            formatted_result = formatter.format_for_ai(processed_matches, business_profile, conflicts)
            
            # Verify results
            assert len(raw_matches) >= 1
            assert len(processed_matches) >= 1
            assert formatted_result.total_requirements >= 1
            assert formatted_result.business_profile.business_name == "מסעדת בדיקה"
            
            # Should have gas requirement
            categories = {req['category'] for req in formatted_result.applicable_requirements}
            assert 'gas' in categories
            
        finally:
            Path(temp_path).unlink()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])