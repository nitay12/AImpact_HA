# Pure Data Extraction Script Plan

**Session Date**: 2025-01-11
**Objective**: Create a focused data extraction script that extracts ONLY regulatory data from the Hebrew PDF, without adding any hardcoded business logic.

## Context from Assignment (משימה.md)

The system needs to support:
1. **Digital questionnaire**: גודל העסק (m²), מספר מקומות ישיבה, מאפיין נוסף (גז, בשר, משלוחים)
2. **Matching engine**: סינון לפי גודל ותפוסה, התחשבות במאפיינים מיוחדים  
3. **AI report generation**: המודל יקבל את הנתונים הגולמיים ויעבד אותם לדוח ברור

## Problem with Previous Approach

The previous `requirements_matcher.py` script added hardcoded business logic:
- Cost estimates (`"500-800 ₪ למטף"`) - **NOT from PDF**
- Timeline estimates (`"1 יום"`, `"2-4 שבועות"`) - **NOT from PDF**
- Next steps (`["רכישת מטף...", "התקנה..."]`) - **Hardcoded action items**

**The assignment requires pure data extraction from PDF → AI processing → business guidance**

## New Pure Extraction Strategy

### 1. Hebrew Text Processing
- Use PyMuPDF for reliable Hebrew text extraction
- Preserve original Hebrew context for AI processing
- Handle RTL text properly with UTF-8 encoding

### 2. Regex Pattern Matching
Create precise patterns for:
- **Area thresholds**: `(\d+)\s*מ["\']ר` patterns
- **Capacity thresholds**: `(\d+)\s*איש` patterns  
- **Section identification**: `\.(\d+(?:\.\d+)*)\s+` format (5.5.1, 6.9.1)
- **Israeli standards**: `תקן ישראל[יי]?\s*ת["\']י\s*(\d+)` patterns
- **Certification requirements**: `גורם מוסמך|מהנדס|הנדסאי` patterns

### 3. Context Preservation
- Extract surrounding Hebrew text for each requirement
- Maintain original regulatory language for AI processing
- Link requirements to their source sections

### 4. Structured Output Format

```json
{
  "metadata": {
    "source_file": "כיבוי אש.pdf",
    "extraction_date": "ISO timestamp",
    "chapters_processed": [5, 6],
    "total_text_length": "number"
  },
  "business_thresholds": {
    "area_thresholds": [
      {
        "threshold_sqm": 150,
        "trigger_type": "maximum|minimum",
        "context_hebrew": "original regulatory text...",
        "section": "5.1.1",
        "chapter": 5
      }
    ],
    "capacity_thresholds": [
      {
        "threshold_people": 50,
        "trigger_type": "maximum|minimum", 
        "context_hebrew": "original regulatory text...",
        "section": "6.9.1",
        "chapter": 6
      }
    ],
    "combined_thresholds": [
      {
        "threshold_sqm": 301,
        "threshold_people": 300,
        "context_hebrew": "original regulatory text...",
        "section": "6.14.1"
      }
    ]
  },
  "requirements": [
    {
      "requirement_id": "CHAPTER_5_SECTION_5_1",
      "chapter": 5,
      "section": "5.5.1",
      "category": "fire_equipment|electrical|gas|signage|certifications",
      "title_hebrew": "ציוד כיבוי",
      "content_hebrew": "full Hebrew regulatory text...",
      "size_applicability": {
        "min_sqm": 0,
        "max_sqm": 150
      },
      "capacity_applicability": {
        "min_people": 0,
        "max_people": 50
      },
      "special_features": ["gas_usage"],
      "israeli_standards": ["ת\"י 129", "ת\"י 158"],
      "certifications": ["גורם מוסמך"]
    }
  ],
  "israeli_standards": [
    {
      "standard_number": "ת\"י 129",
      "contexts": ["list of Hebrew contexts where mentioned"],
      "related_requirements": ["requirement IDs"]
    }
  ],
  "certification_authorities": [
    {
      "authority": "גורם מוסמך",
      "contexts": ["Hebrew contexts"],
      "standards": ["ת\"י 129"],
      "requirements": ["requirement IDs"]
    }
  ]
}
```

## Implementation Approach

### File Structure
- Create: `backend/data_processing/pure_extractor.py`
- Remove: Previous `requirements_matcher.py` (contained hardcoded logic)
- Output: `backend/fire_safety_regulatory_data.json`

### Key Features
1. **Zero hardcoded business logic** - only extracted data
2. **Original Hebrew preservation** for AI processing
3. **Threshold-based structure** for matching engine
4. **Categorical organization** for questionnaire logic  
5. **Reference mapping** (standards, certifications)
6. **Section-based organization** for regulatory accuracy

### Data Categories for Extraction
- **Fire Equipment** (מטפי כיבוי, מערכות כיבוי)
- **Electrical Systems** (מערכת החשמל, תאורת חירום)
- **Gas Systems** (מערכת גפ"מ)
- **Signage** (שילוט, שלטים)
- **Emergency Exits** (דרכי מוצא, יציאות)
- **Certifications** (אישורים, תעודות)

## Pipeline Integration

This pure extracted data will support:
1. **Questionnaire Logic**: Use thresholds for size/capacity questions
2. **Matching Engine**: Filter requirements by business characteristics
3. **AI Processing**: Provide original Hebrew regulatory context
4. **Report Generation**: AI converts regulatory language to business guidance

## Next Session Tasks

1. Create `pure_extractor.py` with focused regex patterns
2. Test extraction on Hebrew PDF
3. Validate threshold detection accuracy
4. Structure output for pipeline consumption
5. Prepare for FastAPI integration

---

**Key Principle**: Extract regulatory data faithfully from PDF. Let AI add business intelligence in the report generation phase, not in data extraction.