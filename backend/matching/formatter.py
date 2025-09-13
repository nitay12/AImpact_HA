#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Formatter for AI Consumption
Structures matched requirements for optimal AI processing and report generation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel

try:
    from .engine import RequirementMatch
    from .rules import RuleConflict
    from ..models.business_profile import BusinessProfile, BusinessProfileSummary
except ImportError:
    from matching.engine import RequirementMatch
    from matching.rules import RuleConflict
    from models.business_profile import BusinessProfile, BusinessProfileSummary

logger = logging.getLogger(__name__)


class RequirementCategory(BaseModel):
    """Categorized requirements for structured AI processing."""
    category_name: str
    category_hebrew: str
    priority: int
    requirements: List[Dict[str, Any]]
    combined_hebrew_text: str
    requirement_count: int


class MatchedRequirements(BaseModel):
    """Complete structured output for AI processing."""
    
    # Business context
    business_profile: BusinessProfile
    business_summary: BusinessProfileSummary
    
    # Matched requirements
    applicable_requirements: List[Dict[str, Any]]
    requirements_by_category: List[RequirementCategory]
    priority_requirements: List[Dict[str, Any]]
    
    # AI processing context
    hebrew_context_full: str
    hebrew_context_summary: str
    business_context_hebrew: str
    
    # Metadata
    total_requirements: int
    processing_timestamp: str
    match_statistics: Dict[str, Any]
    conflicts_resolved: List[Dict[str, Any]]


class RequirementFormatter:
    """
    Formats matched requirements for optimal AI consumption.
    Preserves Hebrew regulatory context while providing structured data.
    """
    
    def __init__(self):
        """Initialize formatter."""
        self.category_names_hebrew = {
            'fire_equipment': 'ציוד כיבוי',
            'electrical': 'מערכות חשמל',
            'gas': 'מערכות גז',
            'signage': 'שילוט',
            'certifications': 'אישורים',
            'general': 'דרישות כלליות'
        }
        
    def format_for_ai(self, matches: List[RequirementMatch], 
                     business_profile: BusinessProfile,
                     conflicts: Optional[List[RuleConflict]] = None) -> MatchedRequirements:
        """
        Format matched requirements for AI processing.
        
        Args:
            matches: Processed requirement matches
            business_profile: Original business profile
            conflicts: Resolved conflicts (optional)
            
        Returns:
            Structured data optimized for AI report generation
        """
        logger.info(f"Formatting {len(matches)} requirements for AI processing")
        
        # Convert matches to dictionaries
        requirements_data = [self._requirement_match_to_dict(match) for match in matches]
        
        # Group by category
        requirements_by_category = self._group_by_category(matches)
        
        # Extract priority requirements (priority 1)
        priority_requirements = [
            self._requirement_match_to_dict(match) 
            for match in matches if match.priority == 1
        ]
        
        # Generate Hebrew contexts
        hebrew_contexts = self._generate_hebrew_contexts(matches, business_profile)
        
        # Create business summary
        business_summary = BusinessProfileSummary.from_profile(business_profile)
        
        # Generate statistics
        statistics = self._generate_statistics(matches)
        
        # Format conflicts
        formatted_conflicts = []
        if conflicts:
            formatted_conflicts = [self._conflict_to_dict(conflict) for conflict in conflicts]
        
        return MatchedRequirements(
            business_profile=business_profile,
            business_summary=business_summary,
            applicable_requirements=requirements_data,
            requirements_by_category=requirements_by_category,
            priority_requirements=priority_requirements,
            hebrew_context_full=hebrew_contexts['full'],
            hebrew_context_summary=hebrew_contexts['summary'], 
            business_context_hebrew=hebrew_contexts['business'],
            total_requirements=len(matches),
            processing_timestamp=datetime.now().isoformat(),
            match_statistics=statistics,
            conflicts_resolved=formatted_conflicts
        )
    
    def _requirement_match_to_dict(self, match: RequirementMatch) -> Dict[str, Any]:
        """Convert RequirementMatch to dictionary for JSON serialization."""
        return {
            'requirement_id': match.requirement_id,
            'chapter': match.chapter,
            'section': match.section,
            'category': match.category,
            'category_hebrew': self.category_names_hebrew.get(match.category, match.category),
            'title_hebrew': match.title_hebrew,
            'content_hebrew': match.content_hebrew,
            'match_reasons': match.match_reasons,
            'priority': match.priority,
            'priority_text': self._get_priority_text(match.priority)
        }
    
    def _group_by_category(self, matches: List[RequirementMatch]) -> List[RequirementCategory]:
        """Group requirements by category for structured processing."""
        category_groups = {}
        
        for match in matches:
            category = match.category
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(match)
        
        # Create RequirementCategory objects
        categories = []
        for category_name, category_matches in category_groups.items():
            # Combine Hebrew text for category
            combined_text = '\n\n'.join([
                f"סעיף {match.section}: {match.title_hebrew}\n{match.content_hebrew}"
                for match in category_matches
            ])
            
            # Get category priority (minimum priority of requirements in category)
            category_priority = min(match.priority for match in category_matches)
            
            # Convert matches to dictionaries
            requirements_data = [self._requirement_match_to_dict(match) for match in category_matches]
            
            category = RequirementCategory(
                category_name=category_name,
                category_hebrew=self.category_names_hebrew.get(category_name, category_name),
                priority=category_priority,
                requirements=requirements_data,
                combined_hebrew_text=combined_text,
                requirement_count=len(category_matches)
            )
            
            categories.append(category)
        
        # Sort by priority then by category name
        categories.sort(key=lambda x: (x.priority, x.category_name))
        
        return categories
    
    def _generate_hebrew_contexts(self, matches: List[RequirementMatch], 
                                business_profile: BusinessProfile) -> Dict[str, str]:
        """Generate Hebrew contexts for AI processing."""
        
        # Full context: All regulatory text
        full_context_parts = []
        for match in matches:
            section_text = f"""
פרק {match.chapter} - סעיף {match.section}
{match.title_hebrew}

{match.content_hebrew}

סיבת החלה: {' | '.join(match.match_reasons)}
"""
            full_context_parts.append(section_text.strip())
        
        full_context = '\n\n' + '='*50 + '\n\n'.join(full_context_parts)
        
        # Summary context: Key requirements only
        priority_matches = [match for match in matches if match.priority <= 2]
        summary_parts = []
        
        for match in priority_matches:
            summary_text = f"סעיף {match.section}: {match.title_hebrew}"
            if match.match_reasons:
                summary_text += f" ({match.match_reasons[0]})"
            summary_parts.append(summary_text)
        
        summary_context = "דרישות מרכזיות:\n" + '\n'.join(f"• {part}" for part in summary_parts)
        
        # Business context
        feature_names_hebrew = {
            'gas_usage': 'שימוש בגז',
            'delivery': 'משלוחים',
            'alcohol': 'משקאות משכרים',
            'meat': 'מגיש בשר'
        }
        
        features_hebrew = [
            feature_names_hebrew.get(f.value if hasattr(f, 'value') else f, f.value if hasattr(f, 'value') else f) 
            for f in business_profile.special_features
        ]
        
        business_context = f"""
פרופיל העסק:
• גודל: {business_profile.size_sqm} מ"ר
• תפוסה: {business_profile.capacity_people} איש
• מאפיינים מיוחדים: {', '.join(features_hebrew) if features_hebrew else 'ללא'}
• סוג עסק: {business_profile.business_type}
"""
        
        return {
            'full': full_context,
            'summary': summary_context,
            'business': business_context.strip()
        }
    
    def _generate_statistics(self, matches: List[RequirementMatch]) -> Dict[str, Any]:
        """Generate statistics about the matched requirements."""
        if not matches:
            return {}
        
        # Count by category
        category_counts = {}
        priority_counts = {1: 0, 2: 0, 3: 0}
        chapter_counts = {}
        
        for match in matches:
            # Category counts
            category = match.category
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Priority counts
            priority = match.priority
            if priority in priority_counts:
                priority_counts[priority] += 1
            
            # Chapter counts
            chapter = f"Chapter {match.chapter}"
            chapter_counts[chapter] = chapter_counts.get(chapter, 0) + 1
        
        return {
            'total_requirements': len(matches),
            'by_category': category_counts,
            'by_priority': {
                'critical': priority_counts[1],
                'important': priority_counts[2], 
                'recommended': priority_counts[3]
            },
            'by_chapter': chapter_counts,
            'most_common_category': max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        }
    
    def _conflict_to_dict(self, conflict: RuleConflict) -> Dict[str, Any]:
        """Convert RuleConflict to dictionary."""
        return {
            'requirement1_id': conflict.requirement1_id,
            'requirement2_id': conflict.requirement2_id,
            'conflict_type': conflict.conflict_type,
            'resolution': conflict.resolution,
            'preferred_requirement_id': conflict.preferred_requirement_id
        }
    
    def _get_priority_text(self, priority: int) -> str:
        """Get Hebrew priority text."""
        priority_texts = {
            1: 'קריטי',
            2: 'חשוב',
            3: 'מומלץ'
        }
        return priority_texts.get(priority, 'לא ידוע')
    
    def create_ai_prompt_context(self, formatted_requirements: MatchedRequirements) -> str:
        """
        Create optimal context for AI prompt.
        Designed to be included in AI report generation prompts.
        """
        
        business_info = formatted_requirements.business_context_hebrew
        requirements_summary = formatted_requirements.hebrew_context_summary
        
        priority_categories = []
        for category in formatted_requirements.requirements_by_category:
            if category.priority <= 2:  # Critical and important only
                priority_categories.append(f"{category.category_hebrew} ({category.requirement_count} דרישות)")
        
        categories_text = ', '.join(priority_categories) if priority_categories else 'ללא קטגוריות מיוחדות'
        
        prompt_context = f"""
{business_info}

קטגוריות דרישות חשובות: {categories_text}

{requirements_summary}

סה"כ דרישות חלות: {formatted_requirements.total_requirements}
דרישות קריטיות: {formatted_requirements.match_statistics['by_priority']['critical']}
דרישות חשובות: {formatted_requirements.match_statistics['by_priority']['important']}

הנחיות לכתיבת הדוח:
1. התמקד בדרישות הקריטיות והחשובות בלבד
2. הסבר בשפה פשוטה ועסקית, לא משפטית
3. תן עדיפות לצעדים מעשיים וברורים
4. ציין זמני יישום ועלויות משוערות כאשר זה רלוונטי
5. הדגש את הסיכונים של אי-עמידה בדרישות
"""
        
        return prompt_context.strip()


def create_formatter() -> RequirementFormatter:
    """Factory function to create a formatter instance."""
    return RequirementFormatter()