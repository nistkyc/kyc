import re
import PyPDF2
import io
import fitz  # PyMuPDF for better form handling
from typing import Dict, Optional
import streamlit as st


class FormFiller:
    """Handles filling editable PDF forms with extracted data"""

    def __init__(self):
        # Mapping between parsed data keys and actual PDF form field names from EditablePdf.pdf
        self.field_mapping = {
            # Personal Information
            'name': 'Name In Block Letter',
            'date_of_birth': 'O    A D',
            'gender': 'Gender',
            'citizenship_no': 'Citizenship Number',
            'beneficiary_id': 'Beneficiary ID Number',
            'pan_no': 'PAN',
            'national_id': 'National ID Number',
            'issue_district': 'IssueDistrict',
            'issue_date': 'hfL ldlt Issue Date',
            
            # Current Address
            'current_country': 'Current Address Country',
            'current_province': 'Current Address Province',
            'current_district': 'Current Address District',
            'current_municipality': 'Current Address Municipality',
            'current_ward_no': 'Current Address Ward Number',
            'current_tole': 'Current Address Tole',
            'current_telephone': 'Telephone Number',
            'current_mobile': 'Mobile Number',
            'current_email': 'Email Address',
            
            # Permanent Address (clearly separated)
            'permanent_country': 'Permanent Address Country',
            'permanent_province': 'Permanent Address Province',
            'permanent_district': 'Permanent Address District',
            'permanent_municipality': 'Permanent municipality',
            'permanent_ward_no': 'Permanent Ward Number',
            'permanent_tole': 'Permanent Address Tole',
            'permanent_telephone': 'Permanent Telephone Number',
            'permanent_block_no': 'Permanent Block Number',

            # Financial Details
            'income_limit': 'Financial Details',

            # Family Members
            'father_name': "Father",
            'mother_name': "Mother",
            'grandfather_name': "GrandFather",
            'spouse_name': "Spouses Name",
            'son_name': "Son",
            'daughter_name': "Daughter",
            'daughter_in_law_name': "DaughterInLawName",
            'father_in_law_name': "Father in Laws Name",
            'mother_in_law_name': "Mother in Laws Name",

            # Bank Details
            'bank_account_number': 'Bank Account Number',
            'bank_name': 'Bank Name and Address',

            # Occupation
            'organization_name': "Organization's Name",
            'designation': 'Designation',

            'occupation': {
                'business_type': 'TypeOfBusiness'
            },

            #guardian details
            'guardian_name': "NameSurname  In Block letter",    
            'guardian_relationship': "Relationship with applicant",  
            
            #Minor details
            'minor_telephone': "Minor Telephone No",  
            'minor_mobile': "Minor Mobile No",   

        }

        # Gender checkbox mappings
        self.gender_mapping = {'male': 'MaleCheck', 'female': 'FemaleCheck', 'other':'OthersCheck'}

        # Occupation checkbox mappings
        self.business_type_mapping = {'manufacturing': 'Manufacturing', 'service oriented': 'Check', 'others':'Check Box12'}

        # Occupation checkbox mappings
        self.occupation_mapping = {
            'agriculture': 'Agriculture',
            'business': 'Businessperson',
            'service': 'Govt',  
            'student': 'Student',
            'retired': 'Retired',
            'housewife': 'House Wife',
            'foreign': 'Foreign Employment',
            'public': 'Public/Private Sector',
            'private': 'Public/Private Sector',
            'ngo': 'NGO/INGO',
            'ingo': 'NGO/INGO',
            'expert': 'Expert',
            'others': 'Other Occupation',
            'self_employed': 'Self Employed',
            
        }

         # Money laundering checkbox mappings
        self.money_laundering_mapping = {
            'politician_or_high_ranking_person': 'PoliticianOrHighRankingPersonCheck',
            'related_to_politician_or_high_ranking_official': 'RelatedToPoliticianOrHighRankingOfficialCheck',
            'have_a_beneficiary': 'HaveBeneficiaryCheck',
            'convicted_of_felony': 'ConvictedOfFelonyCheck'
        }

        # Bank account type mappings
        self.account_type_mapping = {
            'saving': 'Saving Account',
            'current': 'Current Account'
        }

        # Default template path
        self.default_template_path = './EditablePdf.pdf'

    def fill_template_with_default(self, parsed_data: Dict) -> Optional[bytes]:
        """
        Fill the default PDF template with parsed data
        
        Args:
            parsed_data: Dictionary containing extracted data
            
        Returns:
            bytes: Filled PDF as bytes, or None if failed
        """
        try:
            # Read the default template
            with open(self.default_template_path, 'rb') as f:
                template_bytes = f.read()

            # Create a mock file object for compatibility
            class MockFile:

                def __init__(self, data):
                    self.data = data
                    self.position = 0

                def read(self):
                    return self.data

                def seek(self, position):
                    self.position = position

                @property
                def name(self):
                    return 'EditablePdf.pdf'

            mock_file = MockFile(template_bytes)
            return self.fill_template(mock_file, parsed_data)

        except Exception as e:
            st.error(f"Error loading default template: {str(e)}")
            return None

    def fill_template(self, template_file,
                      parsed_data: Dict) -> Optional[bytes]:
        """
        Fill the PDF template with parsed data using PyMuPDF for better form handling
        
        Args:
            template_file: Streamlit uploaded file object (PDF template)
            parsed_data: Dictionary containing extracted data
            
        Returns:
            bytes: Filled PDF as bytes, or None if failed
        """
        try:
            # Reset file pointer
            template_file.seek(0)
            template_bytes = template_file.read()

            # Use PyMuPDF for form handling
            doc = fitz.open(stream=template_bytes, filetype="pdf")

            # Prepare field updates based on our mapping
            field_updates = self._prepare_field_updates(parsed_data, {})

            # Get all form fields in the document
            for page_num in range(len(doc)):
                page = doc[page_num]
                widgets = page.widgets()

                if widgets:
                    # st.info(f"Found {len(widgets)} form fields on page {page_num + 1}")

                    for widget in widgets:
                        field_name = widget.field_name
                        if field_name in field_updates:
                            try:
                                # Set the field value
                                value = str(field_updates[field_name])

                                # Handle different field types
                                if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                    widget.field_value = value
                                    widget.update()
                                elif widget.field_type == fitz.PDF_WIDGET_TYPE_CHECKBOX:
                                    # For checkboxes, set based on Yes/On values
                                    if value.lower() in [
                                            'yes', 'on', 'true', '1'
                                    ]:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                                    widget.update()
                                elif widget.field_type == fitz.PDF_WIDGET_TYPE_RADIOBUTTON:
                                    # For radio buttons
                                    if value.lower() in [
                                            'yes', 'on', 'true', '1'
                                    ]:
                                        widget.field_value = True
                                    else:
                                        widget.field_value = False
                                    widget.update()

                                # st.success(f"Updated field '{field_name}' with value '{value}'")

                            except Exception as widget_error:
                                st.warning(
                                    f"Could not update field '{field_name}': {str(widget_error)}"
                                )
                        else:
                            # Debug: show unmapped fields (using info instead of debug)
                            pass  # st.info(f"Field '{field_name}' not in mapping")
                else:
                    st.warning(f"No form fields found on page {page_num + 1}")

            # Save the filled PDF with compression to reduce file size
            output_buffer = io.BytesIO()

            # Apply compression settings to reduce file size
            doc.save(output_buffer, 
                    garbage=4,     # Remove unused objects
                    clean=True,    # Clean the document
                    deflate=True)  # Compress streams
            doc.close()
            output_buffer.seek(0)

            return output_buffer.getvalue()

        except Exception as e:
            st.error(f"Error filling PDF template: {str(e)}")
            import traceback
            st.error(f"Detailed error: {traceback.format_exc()}")
            return None

    def _get_form_fields(self, pdf_reader) -> Dict:
        """Extract form fields from PDF"""
        form_fields = {}

        try:
            # Try different methods to get form fields
            if hasattr(pdf_reader, 'get_form_text_fields'):
                form_fields = pdf_reader.get_form_text_fields() or {}
            elif hasattr(pdf_reader, 'get_fields'):
                fields = pdf_reader.get_fields()
                if fields:
                    form_fields = {
                        name: field.get('/V', '')
                        for name, field in fields.items()
                    }

            # If still no fields, try to extract from annotations
            if not form_fields:
                for page in pdf_reader.pages:
                    if '/Annots' in page:
                        for annot_ref in page['/Annots']:
                            try:
                                annot = annot_ref.get_object()
                                if '/T' in annot:  # Field name
                                    field_name = annot['/T']
                                    field_value = annot.get('/V', '')
                                    form_fields[field_name] = field_value
                            except:
                                continue

        except Exception as e:
            st.warning(f"Could not extract form fields: {str(e)}")

        return form_fields

    def _prepare_field_updates(self, parsed_data: Dict,
                               form_fields: Dict) -> Dict:
        """Prepare field updates based on mapping"""
        field_updates = {}

        # Handle regular text fields
        # for data_key, pdf_field_name in self.field_mapping.items():
        #     if data_key in parsed_data and parsed_data[data_key]:
        #         value = str(parsed_data[data_key]).strip()
        #         if value and value != '-':
        #             field_updates[pdf_field_name] = value
                # Handle regular and nested text fields
        for data_key, pdf_field_name in self.field_mapping.items():
            if isinstance(pdf_field_name, dict):
                # Nested mapping (e.g., occupation -> business_type)
                for sub_key, sub_field_name in pdf_field_name.items():
                    if sub_key in parsed_data:
                        value = str(parsed_data[sub_key]).strip()
                        if value and value != '-':
                            field_updates[sub_field_name] = value
            else:
                if data_key in parsed_data:
                    value = str(parsed_data[data_key]).strip()
                    if value and value != '-':
                        field_updates[pdf_field_name] = value
                            # Handle occupation checkboxes
            if 'occupation' in parsed_data:
                occupation = str(parsed_data.get('occupation', '')).lower()
                occupation = re.sub(r'\s+', ' ', occupation.strip())

                # Fallback if occupation is just a label
                if occupation in ['occupation', ''] and 'sector' in parsed_data:
                    sector = str(parsed_data['sector']).lower()
                    occupation = re.sub(r'\s+', ' ', sector.strip())

                # Match using occupation_mapping
                for keyword, field in self.occupation_mapping.items():
                    if keyword in occupation:
                        field_updates[field] = 'Yes'
                        break


        # Handle gender checkboxes
        if 'gender' in parsed_data:
            gender_value = str(parsed_data['gender']).upper()
            if gender_value in ['M', 'MALE']:
                field_updates['MaleCheck'] = 'Yes'
                field_updates['FemaleCheck'] = 'Off'
            elif gender_value in ['F', 'FEMALE']:
                field_updates['FemaleCheck'] = 'Yes'
                field_updates['MaleCheck'] = 'Off'

        # Handle bank account type checkboxes
        if 'bank_account_type' in parsed_data:
            account_type = str(parsed_data['bank_account_type']).lower()
            if 'saving' in account_type:
                field_updates['Saving Account'] = 'Yes'
                field_updates['Current Account'] = 'Off'
            elif 'current' in account_type:
                field_updates['Current Account'] = 'Yes'
                field_updates['Saving Account'] = 'Off'
        
        
          # Handle income limit checkboxes
        if 'income_limit' in parsed_data:
            income_limit = str(parsed_data['income_limit']).lower()
            if 'upto 5,00,000' in income_limit:
                field_updates['Upto 5,00,000'] = 'Yes'
                field_updates['From Rs. 5,00,001 to Rs. 10,00,000'] = 'Off'
                field_updates['Above Rs. 10,00,000'] = 'Off'
            elif 'from rs. 5,00,001 to rs. 10,00,000' in income_limit:
                field_updates['Upto 5,00,000'] = 'Off'
                field_updates['From Rs. 5,00,001 to Rs. 10,00,000'] = 'Yes'
                field_updates['Above Rs. 10,00,000'] = 'Off'
            elif 'above rs. 10,00,000' in income_limit:
                field_updates['Upto 5,00,000'] = 'Off'
                field_updates['From Rs. 5,00,001 to Rs. 10,00,000'] = 'Off'
                field_updates['Above Rs. 10,00,000'] = 'Yes'


        # Handle occupation checkboxes
        # if 'occupation' in parsed_data:
        #     occupation = str(parsed_data['occupation']).lower()
        #     if 'agriculture' in occupation:
        #         field_updates['Agriculture'] = 'Yes'
        #     elif 'business' in occupation:
        #         field_updates['Businessperson'] = 'Yes'
        #     elif 'expert' in occupation:
        #         field_updates['Expert'] = 'Yes'
        #     elif 'others' in occupation:
        #         field_updates['Other Occupation'] = 'Yes'
        #     elif 'service' in occupation or 'govt' in occupation:
        #         field_updates['Govt'] = 'Yes'
        #     elif 'student' in occupation:
        #         field_updates['Student'] = 'Yes'
        #     elif 'retired' in occupation:
        #         field_updates['Retired'] = 'Yes'
        #     elif 'house' in occupation or 'wife' in occupation:
        #         field_updates['House Wife'] = 'Yes'
        #     elif 'foreign' in occupation or 'employment' in occupation:
        #         field_updates['Foreign Employment'] = 'Yes'
        #     elif 'public' in occupation or 'private' in occupation:
        #         field_updates['Public/Private Sector'] = 'Yes'
        #     elif 'ngo' in occupation or 'ingo' in occupation:
        #         field_updates['NGO/INGO'] = 'Yes'
                
            # occupation = str(parsed_data.get('occupation', '')).lower()
            # # fallback if occupation is just a label
            # if occupation in ['occupation', ''] and 'sector' in parsed_data:
            #     occupation = str(parsed_data['sector']).lower()
            occupation = str(parsed_data.get('occupation', '')).lower()
            occupation = re.sub(r'\s+', ' ', occupation.strip())  # normalize whitespace

            # fallback if occupation is meaningless
            if occupation in ['occupation', ''] and 'sector' in parsed_data:
                sector = str(parsed_data['sector']).lower()
                occupation = re.sub(r'\s+', ' ', sector.strip())    

            if 'agriculture' in occupation:
                field_updates['Agriculture'] = 'Yes'
            elif 'business' in occupation:
                field_updates['Businessperson'] = 'Yes'
            elif 'expert' in occupation:
                field_updates['Expert'] = 'Yes'
            elif 'others' in occupation:
                field_updates['Other Occupation'] = 'Yes'
            elif 'service' in occupation or 'govt' in occupation:
                field_updates['Govt'] = 'Yes'
            elif 'student' in occupation:
                field_updates['Student'] = 'Yes'
            elif 'retired' in occupation:
                field_updates['Retired'] = 'Yes'
            elif 'house' in occupation or 'wife' in occupation:
                field_updates['House Wife'] = 'Yes'
            elif 'foreign' in occupation or 'employment' in occupation:
                field_updates['Foreign Employment'] = 'Yes'
            elif 'public' in occupation or 'private' in occupation:
                field_updates['Public/Private Sector'] = 'Yes'
            elif 'ngo' in occupation or 'ingo' in occupation:
                field_updates['NGO/INGO'] = 'Yes'

                
         # Handle money laundering checkboxes
            if 'politician_or_high_ranking_person' in parsed_data:
                if parsed_data['politician_or_high_ranking_person'] == 'Yes':
                    field_updates['Rajniti/padh yes'] = 'Yes'
                    field_updates['Rajniti/padh no'] = 'Off'
                else:
                    field_updates['Rajniti/padh yes'] = 'Off'
                    field_updates['Rajniti/padh no'] = 'Yes'

            if 'related_to_politician_or_high_ranking_official' in parsed_data:
                if parsed_data['related_to_politician_or_high_ranking_official'] == 'Yes':
                    field_updates['Rajniti/padh sambandha yes'] = 'Yes'
                    field_updates['Rajniti/padh sambandha no'] = 'Off'
                else:
                    field_updates['Rajniti/padh sambandha yes'] = 'Off'
                    field_updates['Rajniti/padh sambandha no'] = 'Yes'

            if 'have_a_beneficiary' in parsed_data:
                if parsed_data['have_a_beneficiary'] == 'Yes':
                    field_updates['hitadhikari yes'] = 'Yes'
                    field_updates['hitadhikari no'] = 'Off'
                else:
                    field_updates['hitadhikari yes'] = 'Off'
                    field_updates['hitadhikari no'] = 'Yes'

            if 'convicted_of_felony' in parsed_data:
                if parsed_data['convicted_of_felony'] == 'Yes':
                    field_updates['Dosh yes'] = 'Yes'
                    field_updates['Dosh no'] = 'Off'
                else:
                    field_updates['Dosh yes'] = 'Off'
                    field_updates['Dosh no'] = 'Yes'
 
          # Handle business type checkboxes
        # if 'business_type' in parsed_data:
        #     business_type_value = parsed_data['business_type'].strip().lower()
        #     for business_key, business_value in self.business_type_mapping.items():
        #         if business_type_value == business_key:
        #             field_updates[business_value] = 'Yes'
        #             break
            
            # Handle business type checkboxes like Yes/Off
        if 'business_type' in parsed_data:
            business_type_value = parsed_data['business_type'].strip().lower()
            for business_key, field_name in self.business_type_mapping.items():
                if business_type_value == business_key:
                    # Set the matched one to 'Yes', others to 'Off'
                    for _, other_field in self.business_type_mapping.items():
                        field_updates[other_field] = 'Yes' if field_name == other_field else 'Off'
                    break

        return field_updates

    def _update_form_fields(self, page, field_updates: Dict):
        """Update form fields in the page"""
        if '/Annots' not in page:
            return

        for annot_ref in page['/Annots']:
            try:
                annot = annot_ref.get_object()
                if '/T' in annot:  # Field name
                    field_name = annot['/T']
                    if field_name in field_updates:
                        # Update field value
                        annot.update({
                            PyPDF2.generic.NameObject('/V'):
                            PyPDF2.generic.TextStringObject(
                                field_updates[field_name])
                        })
            except Exception:
                continue

    def _update_field_by_annotation(self, pdf_writer, field_name: str,
                                    value: str):
        """Update form field by directly modifying annotations"""
        try:
            for page_num, page in enumerate(pdf_writer.pages):
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annot_ref in annotations:
                        try:
                            annot = annot_ref.get_object()
                            if '/T' in annot and annot['/T'] == field_name:
                                # Update the field value
                                annot.update({
                                    PyPDF2.generic.NameObject('/V'):
                                    PyPDF2.generic.TextStringObject(value)
                                })
                                # Force appearance update
                                if '/AP' in annot:
                                    annot.pop('/AP', None)
                                return  # Field found and updated
                        except Exception:
                            continue
        except Exception:
            pass  # Silently handle annotation update errors

    def _fill_template_alternative(self, template_bytes: bytes,
                                   parsed_data: Dict) -> Optional[bytes]:
        """
        Alternative method to fill PDF when form fields are not detected
        This method creates a new PDF with the original template as background
        and overlays text at approximate positions
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Create a new PDF with the data
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            # Set font (try to use a font that supports Unicode)
            try:
                c.setFont("Helvetica", 10)
            except:
                c.setFont("Courier", 10)

            # Define approximate positions for different fields based on the template structure
            y_position = 750  # Start from top
            x_position = 100
            line_height = 20

            # Add data to PDF
            c.drawString(x_position, y_position, "FILLED PDF FORM")
            y_position -= line_height * 2

            # Add extracted data
            for key, value in parsed_data.items():
                if value and str(value).strip():
                    display_key = key.replace('_', ' ').title()
                    text = f"{display_key}: {value}"
                    c.drawString(x_position, y_position, text)
                    y_position -= line_height

                    # Start new page if needed
                    if y_position < 100:
                        c.showPage()
                        c.setFont("Helvetica", 10)
                        y_position = 750

            c.save()
            buffer.seek(0)

            # Try to merge with original template
            try:
                template_reader = PyPDF2.PdfReader(io.BytesIO(template_bytes))
                overlay_reader = PyPDF2.PdfReader(buffer)
                writer = PyPDF2.PdfWriter()

                # Merge pages
                for i in range(len(template_reader.pages)):
                    template_page = template_reader.pages[i]

                    if i < len(overlay_reader.pages):
                        overlay_page = overlay_reader.pages[i]
                        template_page.merge_page(overlay_page)

                    writer.add_page(template_page)

                # Create final output
                final_buffer = io.BytesIO()
                writer.write(final_buffer)
                final_buffer.seek(0)

                return final_buffer.getvalue()

            except Exception:
                # If merging fails, return the overlay only
                buffer.seek(0)
                return buffer.getvalue()

        except ImportError:
            st.error(
                "ReportLab library not available for alternative PDF filling method"
            )
            return None
        except Exception as e:
            st.error(f"Alternative PDF filling method failed: {str(e)}")
            return None

    def _format_text_for_field(self, value: str, field_name: str, widget) -> str:
        """
        Format text for optimal display in PDF form fields
        
        Args:
            value: Text value to format
            field_name: Name of the form field
            widget: PyMuPDF widget object
            
        Returns:
            str: Formatted text value
        """
        if not value or not value.strip():
            return value
        
        # Clean up the value first - remove extra spaces
        cleaned_value = ' '.join(value.strip().split())
        
        # For all fields, return cleaned value without any character spacing
        return cleaned_value

    def get_field_mapping_info(self) -> Dict:
        """Return information about field mappings for debugging"""
        return {
            'total_mappings': len(self.field_mapping),
            'categories': {
                'personal':
                len([
                    k for k in self.field_mapping.keys() if k in [
                        'name', 'date_of_birth', 'gender', 'citizenship_no',
                        'beneficiary_id', 'pan_no'
                    ]
                ]),
                'address':
                len([
                    k for k in self.field_mapping.keys()
                    if k.startswith('current_')
                ]),
                'family':
                len([
                    k for k in self.field_mapping.keys() if k.endswith('_name')
                ]),
                'bank':
                len([
                    k for k in self.field_mapping.keys()
                    if k.startswith('bank_')
                ]),
                'occupation':
                len([
                    k for k in self.field_mapping.keys()
                    if k in ['occupation', 'organization', 'designation']
                ])
            },
            'mappings': self.field_mapping
        }
