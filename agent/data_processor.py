"""
Data processor for regulatory requirements JSON data.
Transforms structured regulations into searchable chunks for RAG system.
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RegulationChunk:
    """Processed regulation chunk for RAG system."""
    id: str
    content: str  # Combined text for embedding
    raw_text: str  # Original Hebrew text
    requirement_name: str
    category: str
    source_authority: str
    doc_source: str
    conditions: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class RegulatoryDataProcessor:
    """Processes regulatory JSON data for RAG system."""

    def __init__(self, json_file_path: str):
        self.json_file_path = json_file_path
        self.regulations = []
        self.chunks = []

    def load_data(self) -> List[Dict[str, Any]]:
        """Load regulatory data from JSON file."""
        with open(self.json_file_path, 'r', encoding='utf-8') as f:
            self.regulations = json.load(f)
        return self.regulations

    def process_conditions(self, conditions: List[Dict[str, Any]]) -> str:
        """Convert structured conditions to readable text."""
        condition_texts = []

        for condition in conditions:
            if "logic" in condition and condition["logic"] == "OR":
                # Handle OR logic conditions
                or_clauses = []
                for clause in condition["clauses"]:
                    clause_text = self._format_single_condition(clause)
                    or_clauses.append(clause_text)
                condition_texts.append(f"({' או '.join(or_clauses)})")
            else:
                # Handle regular conditions
                condition_text = self._format_single_condition(condition)
                condition_texts.append(condition_text)

        return " ו".join(condition_texts) if condition_texts else ""

    def _format_single_condition(self, condition: Dict[str, Any]) -> str:
        """Format a single condition to Hebrew text."""
        attribute = condition.get("attribute", "")
        operator = condition.get("operator", "")
        value = condition.get("value", "")

        # Translate attributes to Hebrew
        attr_translations = {
            "seating_capacity": "כמות מקומות ישיבה",
            "size_sqm": "שטח במ\"ר"
        }

        # Translate operators to Hebrew
        op_translations = {
            "less_than_or_equal_to": "עד",
            "greater_than": "מעל",
            "greater_than_or_equal_to": "מ-",
            "equal_to": "בדיוק"
        }

        hebrew_attr = attr_translations.get(attribute, attribute)
        hebrew_op = op_translations.get(operator, operator)

        return f"{hebrew_attr} {hebrew_op} {value}"

    def create_chunks(self) -> List[RegulationChunk]:
        """Transform regulations into searchable chunks."""
        chunks = []

        for reg in self.regulations:
            # Process conditions to readable text
            conditions_text = self.process_conditions(reg.get("conditions", []))

            # Create comprehensive content for embedding
            content_parts = [
                f"דרישה: {reg.get('requirement_name', '')}",
                f"קטגוריה: {reg.get('category', '')}",
                f"רשות: {reg.get('source_authority', '')}",
                f"תנאים: {conditions_text}",
                f"תיאור: {reg.get('raw_text', '')}",
                f"מקור: {reg.get('doc_source', '')}"
            ]

            content = "\n".join(filter(None, content_parts))

            # Create metadata for filtering
            metadata = {
                "category": reg.get("category", ""),
                "source_authority": reg.get("source_authority", ""),
                "doc_source": reg.get("doc_source", ""),
                "conditions": reg.get("conditions", [])
            }

            chunk = RegulationChunk(
                id=reg.get("id", ""),
                content=content,
                raw_text=reg.get("raw_text", ""),
                requirement_name=reg.get("requirement_name", ""),
                category=reg.get("category", ""),
                source_authority=reg.get("source_authority", ""),
                doc_source=reg.get("doc_source", ""),
                conditions=reg.get("conditions", []),
                metadata=metadata
            )

            chunks.append(chunk)

        self.chunks = chunks
        return chunks

    def check_business_compliance(self, business_profile: Dict[str, Any], chunk: RegulationChunk) -> bool:
        """Check if a regulation applies to a business profile."""
        if not chunk.conditions:
            return True  # If no conditions, applies to all

        for condition in chunk.conditions:
            if "logic" in condition and condition["logic"] == "OR":
                # OR logic - at least one clause must be true
                or_result = False
                for clause in condition["clauses"]:
                    if self._evaluate_condition(clause, business_profile):
                        or_result = True
                        break
                if not or_result:
                    return False
            else:
                # Regular condition - must be true
                if not self._evaluate_condition(condition, business_profile):
                    return False

        return True

    def _evaluate_condition(self, condition: Dict[str, Any], profile: Dict[str, Any]) -> bool:
        """Evaluate a single condition against business profile."""
        attribute = condition.get("attribute")
        operator = condition.get("operator")
        threshold = condition.get("value")

        if attribute not in profile:
            return False

        business_value = profile[attribute]

        if operator == "less_than_or_equal_to":
            return business_value <= threshold
        elif operator == "greater_than":
            return business_value > threshold
        elif operator == "greater_than_or_equal_to":
            return business_value >= threshold
        elif operator == "equal_to":
            return business_value == threshold

        return False

    def get_applicable_regulations(self, business_profile: Dict[str, Any]) -> List[RegulationChunk]:
        """Get all regulations that apply to a specific business profile."""
        applicable = []

        for chunk in self.chunks:
            if self.check_business_compliance(business_profile, chunk):
                applicable.append(chunk)

        return applicable


def main():
    """Test the data processor."""
    processor = RegulatoryDataProcessor("agent/data.json")
    processor.load_data()
    chunks = processor.create_chunks()

    print(f"Processed {len(chunks)} regulation chunks")

    # Test with sample business profile
    business_profile = {
        "seating_capacity": 75,
        "size_sqm": 100
    }

    applicable = processor.get_applicable_regulations(business_profile)
    print(f"Found {len(applicable)} applicable regulations for business profile")

    for chunk in applicable:
        print(f"- {chunk.requirement_name}")


if __name__ == "__main__":
    main()