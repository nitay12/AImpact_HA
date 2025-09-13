#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule Processor for Complex Business Logic
Handles edge cases, conflicts, and complex requirement relationships.
"""

import logging
from typing import List, Dict, Set, Any, Optional
from dataclasses import dataclass

try:
    from .engine import RequirementMatch
    from ..models.business_profile import BusinessProfile, SpecialFeature
except ImportError:
    from matching.engine import RequirementMatch
    from models.business_profile import BusinessProfile, SpecialFeature

logger = logging.getLogger(__name__)


@dataclass
class RuleConflict:
    """Represents a conflict between requirements."""
    requirement1_id: str
    requirement2_id: str
    conflict_type: str
    resolution: str
    preferred_requirement_id: str


class RuleProcessor:
    """
    Processes complex business rules and resolves conflicts in requirement matching.
    """
    
    def __init__(self):
        """Initialize rule processor."""
        self.conflict_resolutions = []
        
    def process_matches(self, matches: List[RequirementMatch], 
                       business_profile: BusinessProfile) -> List[RequirementMatch]:
        """
        Process matched requirements through business rules.
        
        Args:
            matches: Raw requirement matches from engine
            business_profile: Business characteristics
            
        Returns:
            Processed and refined requirement matches
        """
        logger.info(f"Processing {len(matches)} raw matches through business rules")
        
        # Apply rule processing steps
        processed_matches = matches.copy()
        
        # 1. Handle threshold boundary conditions
        processed_matches = self._handle_threshold_boundaries(processed_matches, business_profile)
        
        # 2. Resolve chapter conflicts (Chapter 5 vs Chapter 6)
        processed_matches = self._resolve_chapter_conflicts(processed_matches, business_profile)
        
        # 3. Apply feature combination rules
        processed_matches = self._apply_feature_combination_rules(processed_matches, business_profile)
        
        # 4. Prioritize and deduplicate requirements
        processed_matches = self._prioritize_requirements(processed_matches)
        
        # 5. Validate final requirement set
        processed_matches = self._validate_requirement_set(processed_matches, business_profile)
        
        logger.info(f"Final processed matches: {len(processed_matches)} requirements")
        return processed_matches
    
    def _handle_threshold_boundaries(self, matches: List[RequirementMatch], 
                                   business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Handle edge cases at threshold boundaries."""
        
        # Key thresholds from fire safety regulations
        CHAPTER_5_MAX_SIZE = 150  # m²
        CHAPTER_5_MAX_CAPACITY = 50  # people
        
        # If business is exactly at Chapter 5 thresholds
        if (business_profile.size_sqm == CHAPTER_5_MAX_SIZE or 
            business_profile.capacity_people == CHAPTER_5_MAX_CAPACITY):
            
            logger.info("Business at Chapter 5 threshold boundary - applying Chapter 5 rules")
            
            # Prefer Chapter 5 requirements for exact threshold matches
            chapter_5_matches = [m for m in matches if m.chapter == 5]
            chapter_6_matches = [m for m in matches if m.chapter == 6]
            
            # If we have both Chapter 5 and 6 requirements, prefer Chapter 5
            if chapter_5_matches and chapter_6_matches:
                # Keep Chapter 5, filter out conflicting Chapter 6 requirements
                filtered_matches = chapter_5_matches.copy()
                
                # Add non-conflicting Chapter 6 requirements
                for ch6_match in chapter_6_matches:
                    if not self._conflicts_with_chapter_5(ch6_match, chapter_5_matches):
                        filtered_matches.append(ch6_match)
                
                matches = filtered_matches
        
        return matches
    
    def _resolve_chapter_conflicts(self, matches: List[RequirementMatch], 
                                 business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Resolve conflicts between Chapter 5 and Chapter 6 requirements."""
        
        chapter_5_matches = [m for m in matches if m.chapter == 5]
        chapter_6_matches = [m for m in matches if m.chapter == 6] 
        
        if not (chapter_5_matches and chapter_6_matches):
            return matches  # No conflicts to resolve
        
        logger.info(f"Resolving conflicts between {len(chapter_5_matches)} Chapter 5 "
                   f"and {len(chapter_6_matches)} Chapter 6 requirements")
        
        resolved_matches = []
        conflicts_found = []
        
        # Business size determines primary chapter
        if business_profile.size_sqm <= 150 and business_profile.capacity_people <= 50:
            primary_chapter = 5
            secondary_chapter = 6
            primary_matches = chapter_5_matches
            secondary_matches = chapter_6_matches
        else:
            primary_chapter = 6
            secondary_chapter = 5
            primary_matches = chapter_6_matches
            secondary_matches = chapter_5_matches
        
        # Start with primary chapter requirements
        resolved_matches.extend(primary_matches)
        
        # Add non-conflicting secondary chapter requirements
        for secondary_match in secondary_matches:
            conflicts = False
            
            for primary_match in primary_matches:
                if self._requirements_conflict(primary_match, secondary_match):
                    conflicts = True
                    conflicts_found.append(RuleConflict(
                        requirement1_id=primary_match.requirement_id,
                        requirement2_id=secondary_match.requirement_id,
                        conflict_type="chapter_overlap",
                        resolution=f"Prefer Chapter {primary_chapter} requirement",
                        preferred_requirement_id=primary_match.requirement_id
                    ))
                    break
            
            if not conflicts:
                resolved_matches.append(secondary_match)
        
        self.conflict_resolutions.extend(conflicts_found)
        
        if conflicts_found:
            logger.info(f"Resolved {len(conflicts_found)} chapter conflicts")
        
        return resolved_matches
    
    def _apply_feature_combination_rules(self, matches: List[RequirementMatch], 
                                       business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Apply rules for special feature combinations."""
        
        features = business_profile.special_features
        
        # Gas usage rules  
        # Handle both enum and string features
        feature_values = [f.value if hasattr(f, 'value') else f for f in features]
        if SpecialFeature.GAS_USAGE.value in feature_values or SpecialFeature.GAS_USAGE in features:
            matches = self._apply_gas_usage_rules(matches, business_profile)
        
        # Delivery service rules  
        if SpecialFeature.DELIVERY.value in feature_values or SpecialFeature.DELIVERY in features:
            matches = self._apply_delivery_rules(matches, business_profile)
        
        # Alcohol service rules
        if SpecialFeature.ALCOHOL.value in feature_values or SpecialFeature.ALCOHOL in features:
            matches = self._apply_alcohol_rules(matches, business_profile)
        
        # Combined feature rules
        if len(features) > 1:
            matches = self._apply_multi_feature_rules(matches, business_profile)
        
        return matches
    
    def _apply_gas_usage_rules(self, matches: List[RequirementMatch], 
                             business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Apply special rules for gas usage businesses."""
        
        # Ensure gas-related requirements have higher priority
        for match in matches:
            if match.category == 'gas':
                match.priority = 1  # Critical for gas usage
        
        # Add mandatory ventilation requirements for gas usage
        gas_matches = [m for m in matches if match.category == 'gas']
        
        if gas_matches:
            logger.info("Applied gas usage rules - elevated priority for gas requirements")
        
        return matches
    
    def _apply_delivery_rules(self, matches: List[RequirementMatch], 
                            business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Apply special rules for delivery service businesses."""
        
        # Delivery businesses may need additional signage requirements
        signage_matches = [m for m in matches if m.category == 'signage']
        
        if signage_matches:
            for match in signage_matches:
                match.match_reasons.append("נדרש עבור שירותי משלוחים")
        
        return matches
    
    def _apply_alcohol_rules(self, matches: List[RequirementMatch], 
                           business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Apply special rules for alcohol service businesses."""
        
        # Alcohol service may require additional safety measures
        # This is handled in the base requirements - no special processing needed
        
        return matches
    
    def _apply_multi_feature_rules(self, matches: List[RequirementMatch], 
                                 business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Apply rules for businesses with multiple special features."""
        
        features = business_profile.special_features
        
        # Complex businesses (3+ features) get enhanced requirements
        if len(features) >= 3:
            logger.info("Complex business (3+ features) - applying enhanced requirements")
            
            # Elevate all requirement priorities for complex businesses
            for match in matches:
                if match.priority > 1:
                    match.priority = max(1, match.priority - 1)
                    match.match_reasons.append("עסק מורכב עם מאפיינים מרובים")
        
        return matches
    
    def _prioritize_requirements(self, matches: List[RequirementMatch]) -> List[RequirementMatch]:
        """Prioritize and deduplicate requirements."""
        
        # Remove exact duplicates
        seen_ids = set()
        deduplicated_matches = []
        
        for match in matches:
            if match.requirement_id not in seen_ids:
                deduplicated_matches.append(match)
                seen_ids.add(match.requirement_id)
        
        if len(matches) != len(deduplicated_matches):
            logger.info(f"Removed {len(matches) - len(deduplicated_matches)} duplicate requirements")
        
        # Sort by priority, then by chapter and section
        deduplicated_matches.sort(key=lambda x: (x.priority, x.chapter, x.section))
        
        return deduplicated_matches
    
    def _validate_requirement_set(self, matches: List[RequirementMatch], 
                                business_profile: BusinessProfile) -> List[RequirementMatch]:
        """Validate final requirement set for completeness and consistency."""
        
        # Check for mandatory categories
        categories_present = {match.category for match in matches}
        
        mandatory_categories = ['fire_equipment', 'certifications']
        missing_categories = set(mandatory_categories) - categories_present
        
        if missing_categories:
            logger.warning(f"Missing mandatory categories: {missing_categories}")
        
        # Check for gas requirements if gas feature present
        feature_values = [f.value if hasattr(f, 'value') else f for f in business_profile.special_features]
        if ((SpecialFeature.GAS_USAGE.value in feature_values or SpecialFeature.GAS_USAGE in business_profile.special_features) and 
            'gas' not in categories_present):
            logger.warning("Gas usage specified but no gas requirements found")
        
        # Log validation summary
        logger.info(f"Validation complete. Final requirement set contains: "
                   f"{len(matches)} requirements across categories: {categories_present}")
        
        return matches
    
    def _conflicts_with_chapter_5(self, ch6_match: RequirementMatch, 
                                ch5_matches: List[RequirementMatch]) -> bool:
        """Check if Chapter 6 requirement conflicts with Chapter 5 requirements."""
        for ch5_match in ch5_matches:
            if self._requirements_conflict(ch5_match, ch6_match):
                return True
        return False
    
    def _requirements_conflict(self, req1: RequirementMatch, req2: RequirementMatch) -> bool:
        """Check if two requirements conflict with each other."""
        # Same category requirements from different chapters often conflict
        if (req1.category == req2.category and 
            req1.chapter != req2.chapter and
            req1.category in ['fire_equipment', 'electrical', 'signage']):
            return True
        
        # Check for content similarity (simplified)
        if req1.title_hebrew == req2.title_hebrew and req1.chapter != req2.chapter:
            return True
        
        return False
    
    def get_conflict_report(self) -> List[RuleConflict]:
        """Get report of all conflicts resolved during processing."""
        return self.conflict_resolutions.copy()
    
    def reset_conflicts(self):
        """Reset conflict tracking for new processing session."""
        self.conflict_resolutions.clear()