#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pure Data Extraction Script for Hebrew Fire Safety Regulations
Extracts regulatory data from Hebrew PDF without adding hardcoded business logic.
"""

import fitz  # PyMuPDF
import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HebrewFireSafetyExtractor:
    def __init__(self, pdf_path: str):
        """Initialize the extractor with PDF path."""
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self.text_content = ""
        self.extracted_data = {
            "metadata": {},
            "business_thresholds": {
                "area_thresholds": [],
                "capacity_thresholds": [],
                "combined_thresholds": []
            },
            "requirements": [],
            "israeli_standards": [],
            "certification_authorities": []
        }
        
    def load_document(self) -> bool:
        """Load the PDF document."""
        try:
            self.doc = fitz.open(str(self.pdf_path))
            logger.info(f"Successfully loaded PDF: {self.pdf_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            return False
    
    def extract_text(self) -> str:
        """Extract all text from PDF with proper Hebrew handling."""
        if not self.doc:
            logger.error("Document not loaded")
            return ""
        
        full_text = ""
        for page_num in range(len(self.doc)):
            try:
                page = self.doc[page_num]
                text = page.get_text()
                full_text += f"\n=== עמוד {page_num + 1} ===\n{text}"
            except Exception as e:
                logger.error(f"Error extracting text from page {page_num + 1}: {e}")
        
        self.text_content = full_text
        return full_text
    
    def extract_area_thresholds(self) -> List[Dict[str, Any]]:
        """Extract area-based thresholds in square meters."""
        patterns = [
            r'(\d+)\s*מ["\']ר',  # XX m²
            r'עד\s*(\d+)\s*מ["\']ר',  # up to XX m²
            r'מעל\s*(\d+)\s*מ["\']ר',  # over XX m²
            r'ששטחו\s*(?:הכולל\s*)?(?:עד\s*|מעל\s*)?(\d+)\s*מ["\']ר',  # whose area is up to/over XX m²
        ]
        
        area_thresholds = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.text_content, re.MULTILINE | re.UNICODE)
            for match in matches:
                area_value = int(match.group(1))
                
                # Extract surrounding context
                start = max(0, match.start() - 200)
                end = min(len(self.text_content), match.end() + 200)
                context = self.text_content[start:end].strip()
                
                # Determine trigger type
                trigger_type = "maximum"  # Default
                if "מעל" in match.group(0) or "למעלה" in context:
                    trigger_type = "minimum"
                
                # Find section reference
                section_match = re.search(r'\.(\d+(?:\.\d+)*)', context)
                section = section_match.group(1) if section_match else ""
                
                # Find chapter reference
                chapter_match = re.search(r'פרק\s*(\d+)', context)
                chapter = int(chapter_match.group(1)) if chapter_match else 0
                
                threshold_data = {
                    "threshold_sqm": area_value,
                    "trigger_type": trigger_type,
                    "context_hebrew": context,
                    "section": section,
                    "chapter": chapter
                }
                
                area_thresholds.append(threshold_data)
        
        return area_thresholds
    
    def extract_capacity_thresholds(self) -> List[Dict[str, Any]]:
        """Extract capacity-based thresholds (number of people)."""
        patterns = [
            r'(\d+)\s*איש',  # XX people
            r'עד\s*(\d+)\s*איש',  # up to XX people
            r'מעל\s*(\d+)\s*איש',  # over XX people
            r'ל(?:־)?(\d+)\s*איש',  # for XX people
        ]
        
        capacity_thresholds = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.text_content, re.MULTILINE | re.UNICODE)
            for match in matches:
                capacity_value = int(match.group(1))
                
                # Extract surrounding context
                start = max(0, match.start() - 200)
                end = min(len(self.text_content), match.end() + 200)
                context = self.text_content[start:end].strip()
                
                # Determine trigger type
                trigger_type = "maximum"  # Default
                if "מעל" in match.group(0) or "למעלה" in context:
                    trigger_type = "minimum"
                
                # Find section reference
                section_match = re.search(r'\.(\d+(?:\.\d+)*)', context)
                section = section_match.group(1) if section_match else ""
                
                # Find chapter reference
                chapter_match = re.search(r'פרק\s*(\d+)', context)
                chapter = int(chapter_match.group(1)) if chapter_match else 0
                
                threshold_data = {
                    "threshold_people": capacity_value,
                    "trigger_type": trigger_type,
                    "context_hebrew": context,
                    "section": section,
                    "chapter": chapter
                }
                
                capacity_thresholds.append(threshold_data)
        
        return capacity_thresholds
    
    def extract_combined_thresholds(self) -> List[Dict[str, Any]]:
        """Extract thresholds that combine both area and capacity."""
        # Look for patterns that mention both area and capacity in close proximity
        combined_pattern = r'(\d+)\s*מ["\']ר.*?(\d+)\s*איש|(\d+)\s*איש.*?(\d+)\s*מ["\']ר'
        
        combined_thresholds = []
        matches = re.finditer(combined_pattern, self.text_content, re.MULTILINE | re.UNICODE)
        
        for match in matches:
            # Extract area and capacity values
            groups = match.groups()
            area_val = int(groups[0]) if groups[0] else int(groups[3]) if groups[3] else 0
            capacity_val = int(groups[1]) if groups[1] else int(groups[2]) if groups[2] else 0
            
            if area_val > 0 and capacity_val > 0:
                # Extract surrounding context
                start = max(0, match.start() - 250)
                end = min(len(self.text_content), match.end() + 250)
                context = self.text_content[start:end].strip()
                
                # Find section reference
                section_match = re.search(r'\.(\d+(?:\.\d+)*)', context)
                section = section_match.group(1) if section_match else ""
                
                threshold_data = {
                    "threshold_sqm": area_val,
                    "threshold_people": capacity_val,
                    "context_hebrew": context,
                    "section": section
                }
                
                combined_thresholds.append(threshold_data)
        
        return combined_thresholds
    
    def extract_israeli_standards(self) -> List[Dict[str, Any]]:
        """Extract Israeli standards (תקן ישראלי) references."""
        pattern = r'תקן\s*ישראל[יי]?\s*ת["\']י\s*(\d+(?:\s*,?\s*חלק\s*\d+)?)'
        
        standards = {}
        matches = re.finditer(pattern, self.text_content, re.MULTILINE | re.UNICODE)
        
        for match in matches:
            standard_num = match.group(1).strip()
            
            # Extract context
            start = max(0, match.start() - 150)
            end = min(len(self.text_content), match.end() + 150)
            context = self.text_content[start:end].strip()
            
            if standard_num not in standards:
                standards[standard_num] = {
                    "standard_number": f'ת"י {standard_num}',
                    "contexts": [],
                    "related_requirements": []
                }
            
            standards[standard_num]["contexts"].append(context)
        
        return list(standards.values())
    
    def extract_certification_authorities(self) -> List[Dict[str, Any]]:
        """Extract certification authorities and authorized personnel."""
        patterns = [
            r'גורם\s*מוסמך',
            r'מהנדס\s*רשום',
            r'הנדסאי\s*רשום',
            r'בעל\s*רישיון\s*(?:ל?עבודות?\s*)?(?:חשמל|גפ["\']מ)',
        ]
        
        authorities = {}
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.text_content, re.MULTILINE | re.UNICODE)
            
            for match in matches:
                authority = match.group(0)
                
                # Extract context
                start = max(0, match.start() - 200)
                end = min(len(self.text_content), match.end() + 200)
                context = self.text_content[start:end].strip()
                
                if authority not in authorities:
                    authorities[authority] = {
                        "authority": authority,
                        "contexts": [],
                        "standards": [],
                        "requirements": []
                    }
                
                authorities[authority]["contexts"].append(context)
        
        return list(authorities.values())
    
    def extract_requirements_by_section(self) -> List[Dict[str, Any]]:
        """Extract requirements organized by section."""
        requirements = []
        
        # Split text by sections
        section_pattern = r'\.(\d+(?:\.\d+)*)\s+([^\.]+?)(?=\.\d+|\Z)'
        section_matches = re.finditer(section_pattern, self.text_content, re.MULTILINE | re.UNICODE | re.DOTALL)
        
        for match in section_matches:
            section_num = match.group(1)
            section_text = match.group(2).strip()
            
            if len(section_text) < 50:  # Skip very short sections
                continue
            
            # Determine chapter
            chapter_match = re.search(r'פרק\s*(\d+)', section_text)
            chapter = int(chapter_match.group(1)) if chapter_match else 0
            
            # Categorize requirement
            category = self._categorize_requirement(section_text)
            
            # Extract title
            title_match = re.match(r'^([^\n]{1,100})', section_text)
            title = title_match.group(1).strip() if title_match else ""
            
            # Extract applicable size ranges
            size_applicability = self._extract_size_applicability(section_text)
            capacity_applicability = self._extract_capacity_applicability(section_text)
            
            # Extract special features
            special_features = self._extract_special_features(section_text)
            
            # Extract standards
            standards = re.findall(r'ת["\']י\s*(\d+(?:\s*,?\s*חלק\s*\d+)?)', section_text)
            
            # Extract certifications
            cert_matches = re.findall(r'(גורם\s*מוסמך|מהנדס|הנדסאי)', section_text)
            
            requirement = {
                "requirement_id": f"CHAPTER_{chapter}_SECTION_{section_num.replace('.', '_')}",
                "chapter": chapter,
                "section": section_num,
                "category": category,
                "title_hebrew": title,
                "content_hebrew": section_text,
                "size_applicability": size_applicability,
                "capacity_applicability": capacity_applicability,
                "special_features": special_features,
                "israeli_standards": [f'ת"י {std}' for std in standards],
                "certifications": cert_matches
            }
            
            requirements.append(requirement)
        
        return requirements
    
    def _categorize_requirement(self, text: str) -> str:
        """Categorize requirement by content."""
        categories = {
            "fire_equipment": [r'מטפ', r'כיבוי', r'גלגלון', r'עמדת\s*כיבוי'],
            "electrical": [r'חשמל', r'תאורת\s*חירום', r'לוח\s*חשמל'],
            "gas": [r'גפ["\']מ', r'גז', r'מנדפ'],
            "signage": [r'שילוט', r'שלט', r'יציאה'],
            "certifications": [r'אישור', r'תעודה', r'בדיקה']
        }
        
        for category, patterns in categories.items():
            for pattern in patterns:
                if re.search(pattern, text, re.UNICODE):
                    return category
        
        return "general"
    
    def _extract_size_applicability(self, text: str) -> Dict[str, int]:
        """Extract size applicability from text."""
        # Look for size mentions
        size_match = re.search(r'(?:עד\s*)?(\d+)\s*מ["\']ר', text)
        if size_match:
            size = int(size_match.group(1))
            if "עד" in size_match.group(0):
                return {"min_sqm": 0, "max_sqm": size}
            else:
                return {"min_sqm": size, "max_sqm": 9999}
        
        return {"min_sqm": 0, "max_sqm": 9999}
    
    def _extract_capacity_applicability(self, text: str) -> Dict[str, int]:
        """Extract capacity applicability from text."""
        # Look for capacity mentions
        capacity_match = re.search(r'(?:עד\s*)?(\d+)\s*איש', text)
        if capacity_match:
            capacity = int(capacity_match.group(1))
            if "עד" in capacity_match.group(0):
                return {"min_people": 0, "max_people": capacity}
            else:
                return {"min_people": capacity, "max_people": 9999}
        
        return {"min_people": 0, "max_people": 9999}
    
    def _extract_special_features(self, text: str) -> List[str]:
        """Extract special features mentioned in text."""
        features = []
        
        if re.search(r'גפ["\']מ|גז', text, re.UNICODE):
            features.append("gas_usage")
        if re.search(r'משלוח', text, re.UNICODE):
            features.append("delivery")
        if re.search(r'משקאות\s*משכרים', text, re.UNICODE):
            features.append("alcohol")
        if re.search(r'בשר', text, re.UNICODE):
            features.append("meat")
        
        return features
    
    def extract_all_data(self) -> Dict[str, Any]:
        """Extract all regulatory data from the document."""
        if not self.load_document():
            return {}
        
        logger.info("Extracting text from PDF...")
        self.extract_text()
        
        logger.info("Extracting area thresholds...")
        self.extracted_data["business_thresholds"]["area_thresholds"] = self.extract_area_thresholds()
        
        logger.info("Extracting capacity thresholds...")
        self.extracted_data["business_thresholds"]["capacity_thresholds"] = self.extract_capacity_thresholds()
        
        logger.info("Extracting combined thresholds...")
        self.extracted_data["business_thresholds"]["combined_thresholds"] = self.extract_combined_thresholds()
        
        logger.info("Extracting requirements...")
        self.extracted_data["requirements"] = self.extract_requirements_by_section()
        
        logger.info("Extracting Israeli standards...")
        self.extracted_data["israeli_standards"] = self.extract_israeli_standards()
        
        logger.info("Extracting certification authorities...")
        self.extracted_data["certification_authorities"] = self.extract_certification_authorities()
        
        # Add metadata
        self.extracted_data["metadata"] = {
            "source_file": self.pdf_path.name,
            "extraction_date": datetime.now().isoformat(),
            "chapters_processed": [5, 6],
            "total_text_length": len(self.text_content)
        }
        
        return self.extracted_data
    
    def save_to_json(self, output_path: str) -> bool:
        """Save extracted data to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.extracted_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            return False
    
    def close(self):
        """Close the document."""
        if self.doc:
            self.doc.close()

def main():
    """Main function to run the extraction."""
    # Get the data directory (same directory as this script)
    data_dir = Path(__file__).parent
    backend_dir = Path(__file__).parent.parent
    pdf_path = data_dir / "כיבוי אש.pdf"
    output_path = backend_dir / "fire_safety_regulatory_data.json"
    
    extractor = HebrewFireSafetyExtractor(pdf_path)
    
    try:
        logger.info("Starting fire safety regulatory data extraction...")
        data = extractor.extract_all_data()
        
        if data:
            extractor.save_to_json(output_path)
            logger.info("Extraction completed successfully!")
            
            # Print summary
            print(f"\n=== Extraction Summary ===")
            print(f"Source: {data['metadata']['source_file']}")
            print(f"Text length: {data['metadata']['total_text_length']:,} characters")
            print(f"Area thresholds found: {len(data['business_thresholds']['area_thresholds'])}")
            print(f"Capacity thresholds found: {len(data['business_thresholds']['capacity_thresholds'])}")
            print(f"Combined thresholds found: {len(data['business_thresholds']['combined_thresholds'])}")
            print(f"Requirements extracted: {len(data['requirements'])}")
            print(f"Israeli standards found: {len(data['israeli_standards'])}")
            print(f"Certification authorities found: {len(data['certification_authorities'])}")
            
        else:
            logger.error("No data extracted")
            
    finally:
        extractor.close()

if __name__ == "__main__":
    main()