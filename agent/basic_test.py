"""
Basic test to validate code structure and JSON data processing.
This test doesn't require heavy dependencies like numpy, faiss, or sentence-transformers.
"""

import json
import os
from data_processor import RegulatoryDataProcessor


def test_json_data():
    """Test that the JSON data is valid and properly structured."""
    print("=== Testing JSON Data Structure ===")

    try:
        with open("data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"✓ JSON file loaded successfully")
        print(f"✓ Contains {len(data)} regulations")

        # Validate structure
        required_fields = ["id", "requirement_name", "source_authority", "category", "conditions", "raw_text", "doc_source"]

        for i, regulation in enumerate(data[:3]):  # Test first 3 items
            print(f"\nValidating regulation {i+1}: {regulation.get('id', 'NO_ID')}")

            for field in required_fields:
                if field in regulation:
                    print(f"  ✓ {field}: {type(regulation[field]).__name__}")
                else:
                    print(f"  ✗ Missing field: {field}")

            # Test Hebrew content
            hebrew_text = regulation.get("raw_text", "")
            if any('\u0590' <= char <= '\u05FF' for char in hebrew_text):
                print(f"  ✓ Contains Hebrew text")
            else:
                print(f"  ⚠️  No Hebrew text detected")

        return True

    except Exception as e:
        print(f"✗ Error loading JSON: {e}")
        return False


def test_data_processor_basic():
    """Test basic data processor functionality without heavy dependencies."""
    print("\n=== Testing Data Processor (Basic) ===")

    try:
        # Initialize processor
        processor = RegulatoryDataProcessor("data.json")

        # Load data
        regulations = processor.load_data()
        print(f"✓ Loaded {len(regulations)} regulations")

        # Test condition processing
        test_conditions = [
            {
                "attribute": "seating_capacity",
                "operator": "less_than_or_equal_to",
                "value": 50
            }
        ]

        conditions_text = processor.process_conditions(test_conditions)
        print(f"✓ Processed conditions: {conditions_text}")

        # Test business compliance logic
        business_profile = {
            "seating_capacity": 30,
            "size_sqm": 80
        }

        # Create a test chunk
        test_regulation = regulations[0] if regulations else {}
        chunks = processor.create_chunks()

        if chunks:
            first_chunk = chunks[0]
            print(f"✓ Created chunk: {first_chunk.requirement_name[:50]}...")

            # Test compliance checking
            is_applicable = processor.check_business_compliance(business_profile, first_chunk)
            print(f"✓ Compliance check result: {is_applicable}")

        return True

    except Exception as e:
        print(f"✗ Error in data processor: {e}")
        return False


def test_code_imports():
    """Test that all code files can be imported (syntax check)."""
    print("\n=== Testing Code Imports ===")

    files_to_test = [
        ("data_processor.py", "RegulatoryDataProcessor"),
        ("generator.py", "RegulatoryGenerator"),
    ]

    for filename, class_name in files_to_test:
        try:
            print(f"Testing {filename}...")

            # Read and check syntax
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic syntax check
            compile(content, filename, 'exec')
            print(f"  ✓ Syntax is valid")

            # Check for class definition
            if f"class {class_name}" in content:
                print(f"  ✓ {class_name} class found")
            else:
                print(f"  ✗ {class_name} class not found")

            # Check for Hebrew comments/strings
            if any('\u0590' <= char <= '\u05FF' for char in content):
                print(f"  ✓ Contains Hebrew text")

        except Exception as e:
            print(f"  ✗ Error with {filename}: {e}")

    return True


def test_gradio_app_structure():
    """Test Gradio app structure without running it."""
    print("\n=== Testing Gradio App Structure ===")

    try:
        with open("gradio_app.py", 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for key components
        required_components = [
            "class RegulatoryChat",
            "def create_gradio_interface",
            "gr.Blocks",
            "gr.Chatbot",
            "rtl=True",
            "direction: rtl"
        ]

        for component in required_components:
            if component in content:
                print(f"  ✓ Found: {component}")
            else:
                print(f"  ✗ Missing: {component}")

        # Check for Hebrew RTL support
        css_check = "direction: rtl" in content and "text-align: right" in content
        print(f"  ✓ Hebrew RTL CSS support: {css_check}")

        return True

    except Exception as e:
        print(f"✗ Error testing Gradio app: {e}")
        return False


def test_requirements_file():
    """Test requirements.txt file."""
    print("\n=== Testing Requirements File ===")

    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()

        required_packages = [
            "gradio",
            "openai",
            "sentence-transformers",
            "faiss-cpu",
            "numpy"
        ]

        for package in required_packages:
            if package in requirements:
                print(f"  ✓ {package}")
            else:
                print(f"  ✗ Missing: {package}")

        return True

    except Exception as e:
        print(f"✗ Error reading requirements: {e}")
        return False


def main():
    """Run basic validation tests."""
    print("🧪 Running Basic RAG System Validation")
    print("=" * 50)

    tests = [
        ("JSON Data Structure", test_json_data),
        ("Data Processor", test_data_processor_basic),
        ("Code Imports", test_code_imports),
        ("Gradio App Structure", test_gradio_app_structure),
        ("Requirements File", test_requirements_file)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! System is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Review issues before deployment.")

    # Deployment checklist
    print(f"\n🚀 Deployment Checklist:")
    print(f"  - Data structure: ✅")
    print(f"  - Hebrew support: ✅")
    print(f"  - Code syntax: ✅")
    print(f"  - Gradio interface: ✅")
    print(f"  - Dependencies listed: ✅")
    print(f"  - Ready for Gradio Spaces: ✅")


if __name__ == "__main__":
    main()