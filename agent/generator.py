"""
LLM Generation component for regulatory RAG system.
Handles OpenAI API integration with Hebrew-aware prompts.
"""

import os
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv
from data_processor import RegulationChunk

# Load environment variables
load_dotenv()


class RegulatoryGenerator:
    """Generates Hebrew regulatory guidance using LLM with retrieved context."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: Optional[str] = None):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        # Hebrew-aware system prompt
        self.system_prompt = """אתה יועץ רגולטורי מומחה לעסקים בישראל. התמחותך היא בדרישות בטיחות אש ורישוי עסקים.

המטרות שלך:
1. לספק הנחיות ברורות ומעשיות לבעלי עסקים
2. להסביר דרישות רגולטוריות בשפה פשוטה
3. לציין מקורות חוקיים רלוונטיים
4. לתת עדיפות לבטיחות הציבור

כללי מענה:
- ענה תמיד בעברית
- השתמש בשפה ברורה ומובנת
- הדגש דרישות חובה באופן מובהק
- ציין מקורות חוקיים ומסמכים רלוונטיים
- אם יש אי-בהירות, ממליץ לפנות לרשויות המוסמכות

כשאתה מקבל שאילתה ממשתמש, השתמש במידע הרגולטורי שסופק כדי לתת מענה מדויק ומעודכן."""

    def generate_response(
        self,
        query: str,
        retrieved_chunks: List[tuple],  # List of (RegulationChunk, score)
        business_profile: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate Hebrew regulatory guidance based on query and retrieved context.

        Args:
            query: User query in Hebrew
            retrieved_chunks: List of (RegulationChunk, score) from RAG retrieval
            business_profile: Business characteristics for personalized advice
            conversation_history: Previous conversation messages

        Returns:
            Generated Hebrew response
        """
        # Prepare context from retrieved chunks
        context = self._prepare_context(retrieved_chunks, business_profile)

        # Build messages for API call
        messages = [{"role": "system", "content": self.system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges

        # Create user message with context
        user_message = self._create_user_message(query, context, business_profile)
        messages.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1500,
                temperature=0.1,  # Low temperature for regulatory precision
                top_p=0.9
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"מצטער, אירעה שגיאה בעת יצירת המענה. אנא נסה שוב מאוחר יותר.\nשגיאה: {str(e)}"

    def _prepare_context(
        self,
        retrieved_chunks: List[tuple],
        business_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prepare regulatory context from retrieved chunks."""
        if not retrieved_chunks:
            return "לא נמצאו דרישות רגולטוריות רלוונטיות לשאילתה זו."

        context_parts = ["=== דרישות רגולטוריות רלוונטיות ===\n"]

        for i, (chunk, score) in enumerate(retrieved_chunks, 1):
            context_parts.extend([
                f"{i}. {chunk.requirement_name}",
                f"   קטגוריה: {chunk.category}",
                f"   רשות: {chunk.source_authority}",
                f"   מקור: {chunk.doc_source}",
                f"   תיאור: {chunk.raw_text}",
                ""  # Empty line for separation
            ])

            # Add conditions if they exist
            if chunk.conditions:
                conditions_text = self._format_conditions(chunk.conditions)
                if conditions_text:
                    context_parts.insert(-1, f"   תנאי יישום: {conditions_text}")

        return "\n".join(context_parts)

    def _format_conditions(self, conditions: List[Dict[str, Any]]) -> str:
        """Format conditions for display in context."""
        condition_texts = []

        for condition in conditions:
            if "logic" in condition and condition["logic"] == "OR":
                # Handle OR logic
                or_clauses = []
                for clause in condition["clauses"]:
                    clause_text = self._format_single_condition(clause)
                    or_clauses.append(clause_text)
                condition_texts.append(f"({' או '.join(or_clauses)})")
            else:
                # Handle regular condition
                condition_text = self._format_single_condition(condition)
                condition_texts.append(condition_text)

        return " ו".join(condition_texts)

    def _format_single_condition(self, condition: Dict[str, Any]) -> str:
        """Format a single condition for display."""
        attribute = condition.get("attribute", "")
        operator = condition.get("operator", "")
        value = condition.get("value", "")

        # Hebrew translations
        attr_translations = {
            "seating_capacity": "כמות מקומות ישיבה",
            "size_sqm": "שטח במ\"ר"
        }

        op_translations = {
            "less_than_or_equal_to": "עד",
            "greater_than": "מעל",
            "greater_than_or_equal_to": "החל מ-",
            "equal_to": "בדיוק"
        }

        hebrew_attr = attr_translations.get(attribute, attribute)
        hebrew_op = op_translations.get(operator, operator)

        return f"{hebrew_attr} {hebrew_op} {value}"

    def _create_user_message(
        self,
        query: str,
        context: str,
        business_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create the user message with query, context, and business profile."""
        message_parts = []

        # Add business profile if provided
        if business_profile:
            profile_text = self._format_business_profile(business_profile)
            message_parts.append(f"=== פרופיל העסק ===\n{profile_text}\n")

        # Add regulatory context
        message_parts.append(context)

        # Add user query
        message_parts.extend([
            "\n=== שאילתת המשתמש ===",
            query,
            "\nאנא ענה בעברית על סמך המידע הרגולטורי שסופק למעלה. תן הנחיות ברורות ומעשיות."
        ])

        return "\n".join(message_parts)

    def _format_business_profile(self, profile: Dict[str, Any]) -> str:
        """Format business profile for display."""
        profile_parts = []

        attr_translations = {
            "seating_capacity": "כמות מקומות ישיבה",
            "size_sqm": "שטח במ\"ר",
            "business_type": "סוג עסק",
            "floors": "מספר קומות",
            "kitchen": "מטבח",
            "storage": "מחסן"
        }

        for key, value in profile.items():
            hebrew_key = attr_translations.get(key, key)
            if isinstance(value, bool):
                hebrew_value = "כן" if value else "לא"
            else:
                hebrew_value = str(value)
            profile_parts.append(f"{hebrew_key}: {hebrew_value}")

        return "\n".join(profile_parts)

    def generate_compliance_report(
        self,
        business_profile: Dict[str, Any],
        applicable_regulations: List[RegulationChunk]
    ) -> str:
        """Generate a comprehensive compliance report for a business."""
        context = []

        # Business profile section
        profile_text = self._format_business_profile(business_profile)
        context.extend([
            "=== פרטי העסק ===",
            profile_text,
            ""
        ])

        # Applicable regulations
        if applicable_regulations:
            context.append("=== דרישות רגולטוריות חלות ===")
            for i, chunk in enumerate(applicable_regulations, 1):
                context.extend([
                    f"{i}. {chunk.requirement_name}",
                    f"   קטגוריה: {chunk.category}",
                    f"   מקור: {chunk.doc_source}",
                    f"   דרישה: {chunk.raw_text}",
                    ""
                ])
        else:
            context.append("לא נמצאו דרישות רגולטוריות חלות על עסק זה.")

        context_text = "\n".join(context)

        # Generate report using LLM
        report_prompt = """על סמך המידע לעיל, אנא הכן דוח ציות רגולטורי מפורט הכולל:

1. סיכום מצב הציות הנוכחי
2. רשימת דרישות חובה שחלות על העסק
3. המלצות מעשיות ליישום
4. זמני יישום מומלצים
5. המלצה על יועצים מקצועיים במידת הצורך

הדוח יהיה מקצועי אך קריא לבעל עסק ללא רקע משפטי."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context_text + "\n\n" + report_prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"מצטער, אירעה שגיאה ביצירת הדוח. אנא נסה שוב.\nשגיאה: {str(e)}"


def main():
    """Test the generator."""
    from rag_system import RegulatoryRAGSystem

    # Initialize components
    rag = RegulatoryRAGSystem()
    generator = RegulatoryGenerator()

    # Load or build index
    if not rag.load_index():
        print("Building index...")
        rag.build_index("data.json")

    # Test query
    query = "איזה דרישות בטיחות אש חלות על מסעדה עם 80 מקומות ישיבה?"
    business_profile = {
        "seating_capacity": 80,
        "size_sqm": 120,
        "business_type": "מסעדה"
    }

    # Retrieve relevant regulations
    results = rag.hybrid_search(query, business_profile, k=3)

    # Generate response
    response = generator.generate_response(query, results, business_profile)

    print("=== Generated Response ===")
    print(response)

    print("\n=== Compliance Report ===")
    applicable_chunks = [chunk for chunk, score in results]
    report = generator.generate_compliance_report(business_profile, applicable_chunks)
    print(report)


if __name__ == "__main__":
    main()