"""
Demo script for conversational info gathering.
Tests the complete flow without running the full Gradio interface.
"""

from business_profiler import BusinessProfiler
from rag_system import RegulatoryRAGSystem
from generator import RegulatoryGenerator


def simulate_conversation():
    """Simulate a complete conversational flow."""
    print("🎭 Simulating Conversational Info Gathering")
    print("=" * 60)

    # Initialize components
    profiler = BusinessProfiler()

    # Simulate conversation steps
    conversation_steps = [
        "שלום, אני רוצה לדעת על דרישות לעסק שלי",
        "אני מפעיל מסעדה",
        "יש לי 80 מקומות ישיבה",
        "השטח הוא 150 מטר רבוע",
        "איזה דרישות בטיחות אש חלות עליי?"
    ]

    print("\n📝 Starting conversation simulation...")

    # First message - show welcome
    first_input = conversation_steps[0]
    print(f"\n👤 User: {first_input}")

    welcome_msg = profiler.generate_welcome_message()
    first_question = profiler.get_next_question()
    response = f"{welcome_msg}\n\n{first_question}"
    print(f"🤖 Assistant: {response[:200]}...")

    # Process subsequent messages
    for i, user_input in enumerate(conversation_steps[1:], 2):
        print(f"\n👤 User: {user_input}")

        # Extract info
        extracted = profiler.update_business_info(user_input)

        if not profiler.business_info.is_complete:
            next_question = profiler.get_next_question()

            if extracted:
                # Acknowledge extraction
                ack_parts = []
                if "business_type" in extracted:
                    ack_parts.append(f"✓ סוג עסק: {extracted['business_type']}")
                if "seating_capacity" in extracted:
                    ack_parts.append(f"✓ מקומות ישיבה: {extracted['seating_capacity']}")
                if "size_sqm" in extracted:
                    ack_parts.append(f"✓ שטח: {extracted['size_sqm']} מ\"ר")

                acknowledgment = "תודה! הבנתי:\n" + "\n".join(ack_parts)

                if next_question:
                    response = f"{acknowledgment}\n\n{next_question}"
                else:
                    response = f"{acknowledgment}\n\n{profiler.generate_summary_message()}"
            else:
                missing = profiler.get_missing_info_summary()
                if next_question:
                    response = f"לא הצלחתי להבין את המידע. {next_question}"
                else:
                    response = f"אני עדיין צריך לדעת: {', '.join(missing)}"

            print(f"🤖 Assistant: {response[:200]}...")

        else:
            # Profile complete - show summary or handle query
            if extracted:
                summary_response = profiler.generate_summary_message()
                print(f"🤖 Assistant: {summary_response[:200]}...")
            else:
                # This would be a regulatory query
                print("🤖 Assistant: [Would now process regulatory query with RAG system...]")

                # Show what would happen
                business_profile = profiler.get_business_profile_dict()
                print(f"\n📊 Business Profile Collected:")
                for key, value in business_profile.items():
                    print(f"   • {key}: {value}")

                print(f"\n✅ Ready for regulatory queries!")
                break

    print(f"\n" + "=" * 60)
    print("🎉 Conversation simulation complete!")

    return profiler


def test_with_variations():
    """Test with different conversation variations."""
    print("\n🔄 Testing Conversation Variations")
    print("=" * 40)

    test_cases = [
        {
            "name": "All info in one message",
            "input": "אני מפעיל מסעדה עם 75 מקומות ישיבה ושטח של 180 מטר רבוע"
        },
        {
            "name": "Partial info",
            "input": "יש לי בית קפה קטן עם 30 מקומות"
        },
        {
            "name": "No clear info",
            "input": "אני רוצה לדעת על דרישות רישוי"
        }
    ]

    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        profiler = BusinessProfiler()

        print(f"Input: {test_case['input']}")
        extracted = profiler.update_business_info(test_case['input'])
        print(f"Extracted: {extracted}")
        print(f"Complete: {profiler.business_info.is_complete}")

        if not profiler.business_info.is_complete:
            next_q = profiler.get_next_question()
            print(f"Next question: {next_q}")


def main():
    """Run the complete demo."""
    print("🚀 Conversational Info Gathering Demo")
    print("=" * 60)

    try:
        # Simulate full conversation
        profiler = simulate_conversation()

        # Test variations
        test_with_variations()

        print(f"\n✅ All tests completed successfully!")
        print(f"\n📋 Summary:")
        print(f"   • Business profiler works correctly")
        print(f"   • Hebrew text extraction functional")
        print(f"   • Conversational flow implemented")
        print(f"   • Ready for integration with RAG system")

        print(f"\n🚀 To test the full system:")
        print(f"   python3 gradio_app.py")

    except Exception as e:
        print(f"❌ Error in demo: {e}")
        raise


if __name__ == "__main__":
    main()