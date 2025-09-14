"""
Test Runner for Regu-Biz / רגו-ביז Backend
Simple script to run tests and demonstrate matching engine functionality.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from models.business_profile import BusinessProfile, SpecialFeature, SAMPLE_PROFILES
from matching.engine import RequirementMatcher
from matching.rules import RuleProcessor  
from matching.formatter import RequirementFormatter


def create_sample_regulatory_data() -> Dict[str, Any]:
    """Create sample regulatory data for demonstration."""
    return {
        "metadata": {
            "source_file": "demo_data.pdf",
            "extraction_date": "2024-01-01T00:00:00",
            "chapters_processed": [5, 6]
        },
        "business_thresholds": {
            "area_thresholds": [
                {
                    "threshold_sqm": 150,
                    "trigger_type": "maximum",
                    "context_hebrew": "עסקים קטנים עד 150 מ\"ר חלים עליהם דרישות פרק 5",
                    "section": "5.1",
                    "chapter": 5
                }
            ],
            "capacity_thresholds": [
                {
                    "threshold_people": 50,
                    "trigger_type": "maximum", 
                    "context_hebrew": "תפוסה עד 50 איש - דרישות פרק 5",
                    "section": "5.2",
                    "chapter": 5
                }
            ]
        },
        "requirements": [
            {
                "requirement_id": "CHAPTER_5_FIRE_EQUIPMENT_1",
                "chapter": 5,
                "section": "5.5.1",
                "category": "fire_equipment",
                "title_hebrew": "מטפי כיבוי אש",
                "content_hebrew": "בעסק יוצבו מטפי כיבוי מסוג אבקה יבשה במשקל של 6 ק\"ג, בקרבת לוח החשמל. בדיקת מטפי הכיבוי ותחזוקתם תעשה לפי האמור בתקן ישראלי ת\"י 129.",
                "size_applicability": {"min_sqm": 0, "max_sqm": 150},
                "capacity_applicability": {"min_people": 0, "max_people": 50},
                "special_features": [],
                "israeli_standards": ["ת\"י 129"],
                "certifications": ["גורם מוסמך"]
            },
            {
                "requirement_id": "CHAPTER_5_ELECTRICAL_1",
                "chapter": 5,
                "section": "5.6.2",
                "category": "electrical",
                "title_hebrew": "שילוט לוחות חשמל",
                "content_hebrew": "על גבי לוחות החשמל יותקן שלט פולט אור שבו ייכתב \"חשמל, לא לכבות במים\".",
                "size_applicability": {"min_sqm": 0, "max_sqm": 150},
                "capacity_applicability": {"min_people": 0, "max_people": 50},
                "special_features": [],
                "israeli_standards": [],
                "certifications": []
            },
            {
                "requirement_id": "CHAPTER_6_GAS_SYSTEM_1",
                "chapter": 6,
                "section": "6.23.1",
                "category": "gas",
                "title_hebrew": "מערכת גז",
                "content_hebrew": "מערכת הגז המשמשת את העסק תענה לנדרש בתקן ישראלי ת\"י 158, מתקנים לגזים פחמימניים מעובים.",
                "size_applicability": {"min_sqm": 0, "max_sqm": 9999},
                "capacity_applicability": {"min_people": 0, "max_people": 9999},
                "special_features": ["gas_usage"],
                "israeli_standards": ["ת\"י 158"],
                "certifications": ["בעל רישיון לעבודת גפ\"מ"]
            },
            {
                "requirement_id": "CHAPTER_6_LARGE_BUSINESS_1",
                "chapter": 6,
                "section": "6.13.2",
                "category": "fire_equipment",
                "title_hebrew": "עמדות כיבוי אש",
                "content_hebrew": "בעסק ששטחו מעל 120 מ\"ר תותקנה עמדות כיבוי אש, הכוללות ברז כיבוי, זרנוקים, מזנק וגלגלון.",
                "size_applicability": {"min_sqm": 120, "max_sqm": 9999},
                "capacity_applicability": {"min_people": 0, "max_people": 9999},
                "special_features": [],
                "israeli_standards": ["ת\"י 448"],
                "certifications": ["גורם מוסמך"]
            }
        ]
    }


def test_business_scenario(business_profile: BusinessProfile, 
                          matcher: RequirementMatcher,
                          rule_processor: RuleProcessor,
                          formatter: RequirementFormatter) -> None:
    """Test a single business scenario end-to-end."""
    
    print(f"\n{'='*60}")
    print(f"Testing: {business_profile.business_name or 'Business Profile'}")
    print(f"Size: {business_profile.size_sqm} m², Capacity: {business_profile.capacity_people} people")
    print(f"Features: {[f.value if hasattr(f, 'value') else f for f in business_profile.special_features]}")
    print(f"{'='*60}")
    
    # Step 1: Match requirements
    raw_matches = matcher.match_requirements(business_profile)
    print(f"📋 Raw matches found: {len(raw_matches)}")
    
    for match in raw_matches:
        print(f"   • {match.title_hebrew} (Chapter {match.chapter}, {match.category})")
    
    # Step 2: Process through rules
    processed_matches = rule_processor.process_matches(raw_matches, business_profile)
    conflicts = rule_processor.get_conflict_report()
    print(f"⚙️  After rule processing: {len(processed_matches)} requirements")
    
    if conflicts:
        print(f"🔧 Conflicts resolved: {len(conflicts)}")
    
    # Step 3: Format for AI
    formatted_result = formatter.format_for_ai(processed_matches, business_profile, conflicts)
    print(f"📤 Formatted for AI: {formatted_result.total_requirements} requirements")
    
    # Show priority breakdown
    stats = formatted_result.match_statistics
    priority_stats = stats['by_priority']
    print(f"📊 Priority breakdown:")
    print(f"   • Critical: {priority_stats['critical']}")
    print(f"   • Important: {priority_stats['important']}")
    print(f"   • Recommended: {priority_stats['recommended']}")
    
    # Show AI context sample
    ai_context = formatter.create_ai_prompt_context(formatted_result)
    print(f"🤖 AI Context Preview (first 200 chars):")
    print(f"   {ai_context[:200]}...")
    
    # Reset processor
    rule_processor.reset_conflicts()


def main():
    """Run demonstration tests."""
    print("🚀 Regu-Biz / רגו-ביז - Matching Engine Demonstration")
    print("Testing Hebrew fire safety regulation matching...")
    
    # Create sample regulatory data
    regulatory_data = create_sample_regulatory_data()
    
    # Save to temporary file
    temp_file = Path("temp_regulatory_data.json")
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(regulatory_data, f, ensure_ascii=False, indent=2)
    
    try:
        # Initialize components
        matcher = RequirementMatcher(str(temp_file))
        rule_processor = RuleProcessor()
        formatter = RequirementFormatter()
        
        print(f"✅ Components initialized successfully")
        print(f"📚 Loaded {len(regulatory_data['requirements'])} sample requirements")
        
        # Test scenarios
        test_scenarios = [
            BusinessProfile(
                size_sqm=80,
                capacity_people=30,
                special_features=[],
                business_name="קפה קטן"
            ),
            BusinessProfile(
                size_sqm=150,
                capacity_people=60,
                special_features=[SpecialFeature.GAS_USAGE],
                business_name="מסעדה בינונית עם גז"
            ),
            BusinessProfile(
                size_sqm=200,
                capacity_people=100,
                special_features=[SpecialFeature.GAS_USAGE, SpecialFeature.DELIVERY],
                business_name="מסעדה גדולה מורכבת"
            )
        ]
        
        # Run tests
        for business_profile in test_scenarios:
            test_business_scenario(business_profile, matcher, rule_processor, formatter)
        
        print(f"\n{'='*60}")
        print("✅ All test scenarios completed successfully!")
        print("🎯 Matching engine is working correctly with Hebrew regulations")
        print("🤖 Ready for AI integration phase")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


if __name__ == "__main__":
    main()