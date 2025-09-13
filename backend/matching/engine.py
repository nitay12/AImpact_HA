#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Requirement Matching Engine
Core logic for filtering regulatory requirements based on business characteristics.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass

try:
    from ..models.business_profile import BusinessProfile, SpecialFeature
except ImportError:
    from models.business_profile import BusinessProfile, SpecialFeature

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RequirementMatch:
    """Single requirement match with context."""
    requirement_id: str
    chapter: int
    section: str
    category: str
    title_hebrew: str
    content_hebrew: str
    match_reasons: List[str]  # Why this requirement applies
    priority: int  # 1=critical, 2=important, 3=recommended


class RequirementMatcher:
    """
    Core engine for matching regulatory requirements to business profiles.
    Pure filtering logic based on extracted regulatory data.
    """
    
    def __init__(self, regulatory_data_path: Optional[str] = None):
        """Initialize matcher with regulatory data."""
        self.regulatory_data = {}
        self.requirements = []
        self.thresholds = {}
        
        # Load regulatory data
        if regulatory_data_path:
            self.load_regulatory_data(regulatory_data_path)
        else:
            # Try to load from default location
            backend_dir = Path(__file__).parent.parent
            default_path = backend_dir / "fire_safety_regulatory_data.json"
            if default_path.exists():
                self.load_regulatory_data(str(default_path))
            else:
                logger.warning("No regulatory data loaded. Call load_regulatory_data() manually.")
    
    def load_regulatory_data(self, file_path: str) -> bool:
        """Load extracted regulatory data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.regulatory_data = json.load(f)
            
            self.requirements = self.regulatory_data.get('requirements', [])
            self.thresholds = self.regulatory_data.get('business_thresholds', {})
            
            logger.info(f"Loaded {len(self.requirements)} requirements from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load regulatory data: {e}")
            return False
    
    def match_requirements(self, business_profile: BusinessProfile) -> List[RequirementMatch]:
        """
        Main entry point: match all applicable requirements to business profile.
        
        Args:
            business_profile: Business characteristics from questionnaire
            
        Returns:
            List of matched requirements with context
        """
        if not self.requirements:
            logger.error("No regulatory data loaded")
            return []
        
        logger.info(f"Matching requirements for business: {business_profile.size_sqm}m², "
                   f"{business_profile.capacity_people} people, "
                   f"features: {business_profile.special_features}")
        
        matches = []
        
        for req in self.requirements:
            match_result = self._evaluate_requirement(req, business_profile)
            if match_result:
                matches.append(match_result)
        
        # Sort by priority and chapter
        matches.sort(key=lambda x: (x.priority, x.chapter, x.section))
        
        logger.info(f"Found {len(matches)} applicable requirements")
        return matches
    
    def _evaluate_requirement(self, requirement: Dict[str, Any], 
                            business_profile: BusinessProfile) -> Optional[RequirementMatch]:
        """
        Evaluate if a single requirement applies to the business profile.
        
        Args:
            requirement: Single requirement from regulatory data
            business_profile: Business characteristics
            
        Returns:
            RequirementMatch if applicable, None otherwise
        """
        match_reasons = []
        
        # Check size applicability
        size_match = self._check_size_applicability(
            requirement.get('size_applicability', {}), 
            business_profile.size_sqm
        )
        if not size_match['matches']:
            return None
        if size_match['reason']:
            match_reasons.append(size_match['reason'])
        
        # Check capacity applicability
        capacity_match = self._check_capacity_applicability(
            requirement.get('capacity_applicability', {}),
            business_profile.capacity_people
        )
        if not capacity_match['matches']:
            return None
        if capacity_match['reason']:
            match_reasons.append(capacity_match['reason'])
        
        # Check special features
        feature_match = self._check_feature_applicability(
            requirement.get('special_features', []),
            business_profile.special_features
        )
        if feature_match['reason']:
            match_reasons.append(feature_match['reason'])
        
        # Determine priority based on requirement category and business characteristics
        priority = self._calculate_priority(requirement, business_profile)
        
        return RequirementMatch(
            requirement_id=requirement.get('requirement_id', ''),
            chapter=requirement.get('chapter', 0),
            section=requirement.get('section', ''),
            category=requirement.get('category', 'general'),
            title_hebrew=requirement.get('title_hebrew', ''),
            content_hebrew=requirement.get('content_hebrew', ''),
            match_reasons=match_reasons,
            priority=priority
        )
    
    def _check_size_applicability(self, size_applicability: Dict[str, int], 
                                business_size: int) -> Dict[str, Any]:
        """Check if requirement applies based on business size."""
        min_sqm = size_applicability.get('min_sqm', 0)
        max_sqm = size_applicability.get('max_sqm', 9999)
        
        matches = min_sqm <= business_size <= max_sqm
        
        reason = None
        if matches and (min_sqm > 0 or max_sqm < 9999):
            if min_sqm > 0 and max_sqm < 9999:
                reason = f"גודל העסק ({business_size} מ\"ר) בטווח {min_sqm}-{max_sqm} מ\"ר"
            elif min_sqm > 0:
                reason = f"גודל העסק ({business_size} מ\"ר) מעל {min_sqm} מ\"ר"
            else:
                reason = f"גודל העסק ({business_size} מ\"ר) עד {max_sqm} מ\"ר"
        
        return {'matches': matches, 'reason': reason}
    
    def _check_capacity_applicability(self, capacity_applicability: Dict[str, int], 
                                    business_capacity: int) -> Dict[str, Any]:
        """Check if requirement applies based on business capacity."""
        min_people = capacity_applicability.get('min_people', 0)
        max_people = capacity_applicability.get('max_people', 9999)
        
        matches = min_people <= business_capacity <= max_people
        
        reason = None
        if matches and (min_people > 0 or max_people < 9999):
            if min_people > 0 and max_people < 9999:
                reason = f"תפוסת העסק ({business_capacity} איש) בטווח {min_people}-{max_people} איש"
            elif min_people > 0:
                reason = f"תפוסת העסק ({business_capacity} איש) מעל {min_people} איש"
            else:
                reason = f"תפוסת העסק ({business_capacity} איש) עד {max_people} איש"
        
        return {'matches': matches, 'reason': reason}
    
    def _check_feature_applicability(self, req_features: List[str], 
                                   business_features: List[SpecialFeature]) -> Dict[str, Any]:
        """Check if requirement applies based on special features."""
        # Convert business features to strings for comparison
        business_feature_strs = [f.value if hasattr(f, 'value') else f for f in business_features]
        
        # Check if any required features match business features
        matching_features = set(req_features) & set(business_feature_strs)
        
        reason = None
        if matching_features:
            feature_names_hebrew = {
                'gas_usage': 'שימוש בגז',
                'delivery': 'משלוחים', 
                'alcohol': 'משקאות משכרים',
                'meat': 'מגיש בשר'
            }
            
            hebrew_features = [feature_names_hebrew.get(f, f) for f in matching_features]
            reason = f"מאפיינים מיוחדים: {', '.join(hebrew_features)}"
        
        return {'matches': len(matching_features) > 0 if req_features else True, 'reason': reason}
    
    def _calculate_priority(self, requirement: Dict[str, Any], 
                          business_profile: BusinessProfile) -> int:
        """Calculate requirement priority based on category and business characteristics."""
        category = requirement.get('category', 'general')
        
        # Critical requirements (always priority 1)
        if category in ['fire_equipment', 'electrical', 'certifications']:
            return 1
        
        # Important requirements for specific features
        if category == 'gas' and SpecialFeature.GAS_USAGE in business_profile.special_features:
            return 1
        
        # Size/capacity based priorities
        if business_profile.size_sqm > 300 or business_profile.capacity_people > 200:
            if category in ['signage', 'electrical']:
                return 2
        
        # Default priorities by category
        priority_map = {
            'fire_equipment': 1,
            'electrical': 1, 
            'certifications': 1,
            'gas': 2,
            'signage': 2,
            'general': 3
        }
        
        return priority_map.get(category, 3)
    
    def get_applicable_thresholds(self, business_profile: BusinessProfile) -> Dict[str, List[Dict]]:
        """Get thresholds that apply to the business profile."""
        applicable_thresholds = {
            'area_thresholds': [],
            'capacity_thresholds': [],
            'combined_thresholds': []
        }
        
        # Area thresholds
        for threshold in self.thresholds.get('area_thresholds', []):
            threshold_value = threshold.get('threshold_sqm', 0)
            trigger_type = threshold.get('trigger_type', 'maximum')
            
            applies = False
            if trigger_type == 'maximum' and business_profile.size_sqm <= threshold_value:
                applies = True
            elif trigger_type == 'minimum' and business_profile.size_sqm >= threshold_value:
                applies = True
            
            if applies:
                applicable_thresholds['area_thresholds'].append(threshold)
        
        # Capacity thresholds
        for threshold in self.thresholds.get('capacity_thresholds', []):
            threshold_value = threshold.get('threshold_people', 0)
            trigger_type = threshold.get('trigger_type', 'maximum')
            
            applies = False
            if trigger_type == 'maximum' and business_profile.capacity_people <= threshold_value:
                applies = True
            elif trigger_type == 'minimum' and business_profile.capacity_people >= threshold_value:
                applies = True
            
            if applies:
                applicable_thresholds['capacity_thresholds'].append(threshold)
        
        # Combined thresholds
        for threshold in self.thresholds.get('combined_thresholds', []):
            area_threshold = threshold.get('threshold_sqm', 0)
            capacity_threshold = threshold.get('threshold_people', 0)
            
            if (business_profile.size_sqm >= area_threshold and 
                business_profile.capacity_people >= capacity_threshold):
                applicable_thresholds['combined_thresholds'].append(threshold)
        
        return applicable_thresholds
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded regulatory data."""
        if not self.regulatory_data:
            return {}
        
        category_counts = {}
        chapter_counts = {}
        
        for req in self.requirements:
            category = req.get('category', 'unknown')
            chapter = req.get('chapter', 0)
            
            category_counts[category] = category_counts.get(category, 0) + 1
            chapter_counts[f"Chapter {chapter}"] = chapter_counts.get(f"Chapter {chapter}", 0) + 1
        
        return {
            'total_requirements': len(self.requirements),
            'requirements_by_category': category_counts,
            'requirements_by_chapter': chapter_counts,
            'total_thresholds': {
                'area_thresholds': len(self.thresholds.get('area_thresholds', [])),
                'capacity_thresholds': len(self.thresholds.get('capacity_thresholds', [])),
                'combined_thresholds': len(self.thresholds.get('combined_thresholds', []))
            }
        }


def create_matcher(regulatory_data_path: Optional[str] = None) -> RequirementMatcher:
    """Factory function to create a matcher instance."""
    return RequirementMatcher(regulatory_data_path)