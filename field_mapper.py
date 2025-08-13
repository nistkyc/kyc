import PyPDF2
import io
import os
from typing import Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import fitz  # PyMuPDF for overlay method

class FieldMapper:
    """Handles PDF form field mapping and filling using PyPDF2"""
    
    def __init__(self):
        self.template_path = "EditablePdf.pdf"
        
        # Define mapping from extracted fields to PDF form field names
        self.form_field_mappings = {
            'name': ['name', 'full_name', 'applicant_name', 'first_name', 'last_name', 'fname', 'lname'],
            'date_of_birth': ['dob', 'date_of_birth', 'birth_date', 'birthday'],
            'address': ['address', 'home_address', 'residential_address', 'street_address', 'addr'],
            'phone': ['phone', 'telephone', 'mobile', 'contact_number', 'phone_number', 'tel'],
            'email': ['email', 'e_mail', 'email_address', 'electronic_mail'],
            'occupation': ['occupation', 'job', 'profession', 'employment', 'work', 'job_title'],
            'nationality': ['nationality', 'citizenship', 'country_of_birth'],
            'gender': ['gender', 'sex'],
            'age': ['age', 'years_old'],
            'city': ['city', 'town', 'municipality'],
            'state': ['state', 'province', 'region'],
            'zip_code': ['zip', 'postal_code', 'zip_code', 'postcode'],
            'country': ['country', 'nation'],
            'education': ['education', 'qualification', 'degree', 'school', 'university'],
            'experience': ['experience', 'work_experience', 'years_of_experience'],
            'salary': ['salary', 'income', 'wage', 'compensation'],
            'marital_status': ['marital_status', 'married', 'single', 'divorced', 'widowed'],
            'emergency_contact': ['emergency_contact', 'next_of_kin', 'emergency_person'],
            'skills': ['skills', 'abilities', 'competencies', 'expertise'],
            'languages': ['languages', 'language_skills', 'spoken_languages']
        }
    
    def fill_template(self, extracted_data: Dict[str, str]) -> bytes:
        """Fill the PDF template with extracted data using text overlay"""
        try:
            # Check if template exists
            if not os.path.exists(self.template_path):
                raise Exception(f"Template PDF not found: {self.template_path}")
            
            # First try the traditional form filling approach
            try:
                return self._fill_form_fields(extracted_data)
            except Exception as form_error:
                print(f"Form field filling failed, trying text overlay: {form_error}")
                # If form filling fails, use text overlay approach
                return self._fill_with_text_overlay(extracted_data)
                
        except Exception as e:
            raise Exception(f"PDF form filling failed: {str(e)}")
    
    def _fill_form_fields(self, extracted_data: Dict[str, str]) -> bytes:
        """Try to fill PDF form fields using PyPDF2"""
        with open(self.template_path, 'rb') as template_file:
            pdf_reader = PyPDF2.PdfReader(template_file)
            pdf_writer = PyPDF2.PdfWriter()
            
            # Get form fields from the first page
            if len(pdf_reader.pages) == 0:
                raise Exception("Template PDF has no pages")
            
            page = pdf_reader.pages[0]
            
            # Get all form fields
            form_fields = {}
            if "/AcroForm" in pdf_reader.trailer["/Root"]:
                acro_form = pdf_reader.trailer["/Root"]["/AcroForm"]
                if "/Fields" in acro_form:
                    form_fields = self._extract_form_fields(pdf_reader)
            
            # Create field updates
            field_updates = self._create_field_updates(extracted_data, form_fields)
            
            # Debug: print available fields and updates
            print(f"Available form fields: {list(form_fields.keys())}")
            print(f"Field updates to apply: {field_updates}")
            
            # Add the page first
            pdf_writer.add_page(page)
            
            # Fill the form fields
            if field_updates:
                pdf_writer.update_page_form_field_values(pdf_writer.pages[0], field_updates)
            
            # Copy remaining pages if any
            for page_num in range(1, len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])
            
            # Write to bytes
            output_stream = io.BytesIO()
            pdf_writer.write(output_stream)
            output_stream.seek(0)
            
            return output_stream.getvalue()
    
    def _fill_with_text_overlay(self, extracted_data: Dict[str, str]) -> bytes:
        """Fill PDF by overlaying text at specific coordinates"""
        # Open the template PDF with PyMuPDF
        doc = fitz.open(self.template_path)
        
        # Define field positions for the Nepali form (approximate coordinates)
        field_positions = {
            'name': (150, 750),  # Name field position
            'date_of_birth': (250, 720),  # Date of birth
            'gender': (150, 695),  # Gender
            'citizenship_no': (150, 665),  # Citizenship number
            'email': (150, 535),  # Email
            'phone': (400, 525),  # Mobile number
            'address': (150, 500),  # Address
            'country': (150, 470),  # Country
            'state': (300, 470),  # Province
            'district': (450, 470),  # District
            'city': (150, 445),  # Municipality
            'ward_no': (400, 445),  # Ward number
            'tole': (150, 420),  # Tole
            'fathers_name': (150, 350),  # Father's name
            'mothers_name': (150, 320),  # Mother's name
            'spouse_name': (150, 290),  # Spouse name
            'occupation': (150, 180),  # Occupation
        }
        
        # Add text to the first page
        page = doc[0]
        
        for field_name, value in extracted_data.items():
            if field_name in field_positions and value:
                x, y = field_positions[field_name]
                # Insert text at the specified position
                page.insert_text((x, y), str(value), fontsize=10, color=(0, 0, 0))
        
        # Save to bytes
        output_stream = io.BytesIO()
        doc.save(output_stream)
        doc.close()
        output_stream.seek(0)
        
        return output_stream.getvalue()
    
    def _extract_form_fields(self, pdf_reader: PyPDF2.PdfReader) -> Dict[str, str]:
        """Extract form field names from PDF"""
        form_fields = {}
        
        try:
            # Try to get form fields
            if hasattr(pdf_reader, 'get_form_text_fields'):
                form_fields = pdf_reader.get_form_text_fields() or {}
            elif hasattr(pdf_reader, 'getFormTextFields'):
                form_fields = pdf_reader.getFormTextFields() or {}
            else:
                # Alternative method to get field names
                if "/AcroForm" in pdf_reader.trailer["/Root"]:
                    acro_form = pdf_reader.trailer["/Root"]["/AcroForm"]
                    if "/Fields" in acro_form:
                        fields = acro_form["/Fields"]
                        for field in fields:
                            field_obj = field.get_object()
                            if "/T" in field_obj:
                                field_name = field_obj["/T"]
                                form_fields[field_name] = ""
        except Exception:
            # If we can't extract field names, we'll try common field names
            pass
        
        return form_fields
    
    def _create_field_updates(self, extracted_data: Dict[str, str], form_fields: Dict[str, str]) -> Dict[str, str]:
        """Create field updates mapping extracted data to form fields"""
        field_updates = {}
        
        # Get available field names (case-insensitive)
        available_fields = {name.lower(): name for name in form_fields.keys()}
        
        # Map extracted data to form fields
        for data_field, data_value in extracted_data.items():
            if not data_value:
                continue
            
            # Find matching form fields for this data field
            possible_field_names = self.form_field_mappings.get(data_field, [])
            
            for field_name in possible_field_names:
                field_name_lower = field_name.lower()
                
                # Check for exact match
                if field_name_lower in available_fields:
                    actual_field_name = available_fields[field_name_lower]
                    field_updates[actual_field_name] = str(data_value)
                
                # Check for partial matches
                for available_field_lower, available_field_actual in available_fields.items():
                    if field_name_lower in available_field_lower or available_field_lower in field_name_lower:
                        field_updates[available_field_actual] = str(data_value)
        
        # If no form fields were detected, try common field names
        if not form_fields:
            field_updates = self._create_fallback_field_updates(extracted_data)
        
        return field_updates
    
    def _create_fallback_field_updates(self, extracted_data: Dict[str, str]) -> Dict[str, str]:
        """Create field updates using common field names when form fields can't be detected"""
        field_updates = {}
        
        # Common field name mappings
        common_mappings = {
            'name': 'name',
            'date_of_birth': 'dob',
            'address': 'address',
            'phone': 'phone',
            'email': 'email',
            'occupation': 'occupation',
            'nationality': 'nationality',
            'gender': 'gender',
            'age': 'age',
            'city': 'city',
            'state': 'state',
            'zip_code': 'zip',
            'country': 'country'
        }
        
        for data_field, data_value in extracted_data.items():
            if data_value and data_field in common_mappings:
                field_updates[common_mappings[data_field]] = str(data_value)
        
        return field_updates
    
    def get_template_fields(self) -> list:
        """Get available form fields from the template"""
        try:
            if not os.path.exists(self.template_path):
                return []
            
            with open(self.template_path, 'rb') as template_file:
                pdf_reader = PyPDF2.PdfReader(template_file)
                form_fields = self._extract_form_fields(pdf_reader)
                return list(form_fields.keys())
                
        except Exception:
            return []
