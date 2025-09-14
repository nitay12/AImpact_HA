"""
Business Profiler for conversational information gathering.
Extracts business information through natural Hebrew conversation.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class BusinessInfo:
    """Business information extracted from conversation."""
    seating_capacity: Optional[int] = None
    size_sqm: Optional[int] = None
    business_type: Optional[str] = None
    floors: Optional[int] = None
    has_kitchen: Optional[bool] = None
    has_storage: Optional[bool] = None
    has_outdoor_seating: Optional[bool] = None
    is_complete: bool = False


class BusinessProfiler:
    """Extracts business information from Hebrew conversation."""

    def __init__(self):
        self.business_info = BusinessInfo()
        self.required_fields = ["seating_capacity", "size_sqm", "business_type"]
        self.current_question_index = 0

        # Patterns for extracting information from Hebrew text
        self.patterns = {
            "seating_capacity": [
                r"(\d+)\s*מקומות?\s*(?:ישיבה|יושבים|איש|אנשים)",
                r"(?:מקומות?\s*ישיבה|יושבים|איש|אנשים)\s*(\d+)",
                r"(\d+)\s*(?:מקום|מקומות)",
                r"עד\s*(\d+)\s*(?:איש|אנשים|מקומות)"
            ],
            "size_sqm": [
                r"(\d+)\s*(?:מ״ר|מטר|מ\"ר|מ\'ר|מ²)",
                r"שטח\s*(?:של\s*)?(\d+)",
                r"(\d+)\s*מטר\s*רבוע"
            ],
            "floors": [
                r"(\d+)\s*קומות?",
                r"קומה\s*(\d+)",
                r"(\d+)\s*קומה"
            ]
        }

        # Business type patterns
        self.business_types = {
            "מסעדה": ["מסעדה", "מסעדת", "בית אוכל", "מקום אוכל"],
            "בית קפה": ["בית קפה", "קפה", "בית-קפה", "קפיטריה"],
            "בר": ["בר", "פאב", "ביר-בר"],
            "מועדון": ["מועדון", "קלאב", "מועדון לילה"],
            "חנות": ["חנות", "חנות בגדים", "בוטיק"],
            "משרד": ["משרד", "משרדים", "חברה"],
            "מפעל": ["מפעל", "בית חרושת", "פעילות תעשייתית"],
            "מרכז קניות": ["מרכז קניות", "קניון", "גלריה"],
            "בית ספר": ["בית ספר", "בי״ס", "מוסד חינוכי"],
            "מלון": ["מלון", "בית מלון", "אכסניה"]
        }

        # Questions to ask for missing information
        self.questions = [
            {
                "field": "business_type",
                "question": "שלום! בואו נתחיל. איזה סוג עסק אתה מפעיל? (למשל: מסעדה, בית קפה, חנות, משרד...)"
            },
            {
                "field": "seating_capacity",
                "question": "כמה מקומות ישיבה יש בעסק שלך? (אם אין מקומות ישיבה, כתוב 0)"
            },
            {
                "field": "size_sqm",
                "question": "מה השטח הכולל של העסק במטר רבוע?"
            }
        ]

    def extract_info_from_text(self, text: str) -> Dict[str, Any]:
        """Extract business information from Hebrew text."""
        extracted = {}

        # Extract numerical information
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = int(match.group(1))
                        if field not in extracted or value > 0:  # Prefer positive values
                            extracted[field] = value
                    except (ValueError, IndexError):
                        continue

        # Extract business type
        text_lower = text.lower()
        for standard_type, variations in self.business_types.items():
            for variation in variations:
                if variation in text_lower:
                    extracted["business_type"] = standard_type
                    break
            if "business_type" in extracted:
                break

        # Extract boolean information
        if any(word in text_lower for word in ["מטבח", "בישול", "מזון"]):
            extracted["has_kitchen"] = True

        if any(word in text_lower for word in ["מחסן", "אחסון"]):
            extracted["has_storage"] = True

        if any(word in text_lower for word in ["חצר", "גינה", "מרפסת", "בחוץ", "פתוח"]):
            extracted["has_outdoor_seating"] = True

        return extracted

    def update_business_info(self, text: str) -> Dict[str, Any]:
        """Update business information from user input."""
        extracted = self.extract_info_from_text(text)

        # Update business info object
        for field, value in extracted.items():
            if hasattr(self.business_info, field):
                setattr(self.business_info, field, value)

        # Check if profile is complete
        self.business_info.is_complete = all(
            getattr(self.business_info, field) is not None
            for field in self.required_fields
        )

        return extracted

    def get_next_question(self) -> Optional[str]:
        """Get the next question to ask the user."""
        # Check what information is missing
        missing_fields = []
        for field in self.required_fields:
            if getattr(self.business_info, field) is None:
                missing_fields.append(field)

        if not missing_fields:
            return None  # All required information collected

        # Find the next question to ask
        for question_data in self.questions:
            if question_data["field"] in missing_fields:
                return question_data["question"]

        return None

    def get_missing_info_summary(self) -> List[str]:
        """Get a list of missing information."""
        missing = []
        field_names = {
            "seating_capacity": "מספר מקומות ישיבה",
            "size_sqm": "שטח במטר רבוע",
            "business_type": "סוג העסק"
        }

        for field in self.required_fields:
            if getattr(self.business_info, field) is None:
                missing.append(field_names.get(field, field))

        return missing

    def generate_welcome_message(self) -> str:
        """Generate initial welcome message."""
        return """שלום וברוכים הבאים לרגו-ביז! 👋

אני היועץ הרגולטורי החכם שלכם. כדי לתת לכם הנחיות מדויקות ומותאמות אישית, אני צריך לדעת כמה פרטים על העסק שלכם.

בואו נתחיל:"""

    def generate_summary_message(self) -> str:
        """Generate summary of collected information."""
        if not self.business_info.is_complete:
            return "עדיין חסרים פרטים. בואו נמשיך..."

        summary_parts = [
            "מעולה! אספתי את המידע הבסיסי על העסק שלכם:",
            f"🏢 סוג עסק: {self.business_info.business_type}",
            f"👥 מקומות ישיבה: {self.business_info.seating_capacity}",
            f"📐 שטח: {self.business_info.size_sqm} מ\"ר"
        ]

        # Add optional information if available
        if self.business_info.floors:
            summary_parts.append(f"🏗️ קומות: {self.business_info.floors}")
        if self.business_info.has_kitchen:
            summary_parts.append("🍳 כולל מטבח")
        if self.business_info.has_storage:
            summary_parts.append("📦 כולל מחסן")
        if self.business_info.has_outdoor_seating:
            summary_parts.append("🌿 כולל ישיבה חיצונית")

        summary_parts.extend([
            "",
            "עכשיו אני יכול לעזור לכם! שאלו אותי על:",
            "• דרישות בטיחות אש",
            "• רישוי עסקים",
            "• ציוד בטיחות נדרש",
            "• דרישות רגולטוריות",
            "",
            "מה תרצו לדעת? 🔍"
        ])

        return "\n".join(summary_parts)

    def get_business_profile_dict(self) -> Dict[str, Any]:
        """Get business profile as dictionary."""
        profile = {}

        if self.business_info.seating_capacity is not None:
            profile["seating_capacity"] = self.business_info.seating_capacity

        if self.business_info.size_sqm is not None:
            profile["size_sqm"] = self.business_info.size_sqm

        if self.business_info.business_type:
            profile["business_type"] = self.business_info.business_type

        if self.business_info.floors:
            profile["floors"] = self.business_info.floors

        if self.business_info.has_kitchen is not None:
            profile["has_kitchen"] = self.business_info.has_kitchen

        if self.business_info.has_storage is not None:
            profile["has_storage"] = self.business_info.has_storage

        if self.business_info.has_outdoor_seating is not None:
            profile["has_outdoor_seating"] = self.business_info.has_outdoor_seating

        return profile

    def reset(self):
        """Reset the business profiler."""
        self.business_info = BusinessInfo()
        self.current_question_index = 0


def test_profiler():
    """Test the business profiler."""
    profiler = BusinessProfiler()

    test_inputs = [
        "אני מפעיל מסעדה עם 50 מקומות ישיבה",
        "השטח הוא 120 מטר רבוע",
        "יש לי גם מטבח גדול ומחסן",
        "השטח שלי 200 מ״ר עם 80 איש"
    ]

    print("Testing Business Profiler:")
    print("=" * 40)

    for i, text in enumerate(test_inputs, 1):
        print(f"\nInput {i}: {text}")
        extracted = profiler.update_business_info(text)
        print(f"Extracted: {extracted}")

        if not profiler.business_info.is_complete:
            next_q = profiler.get_next_question()
            if next_q:
                print(f"Next question: {next_q}")

    print(f"\nFinal profile: {profiler.get_business_profile_dict()}")
    print(f"Complete: {profiler.business_info.is_complete}")

    if profiler.business_info.is_complete:
        print("\nSummary message:")
        print(profiler.generate_summary_message())


if __name__ == "__main__":
    test_profiler()