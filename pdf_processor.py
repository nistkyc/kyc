import fitz  # PyMuPDF
import streamlit as st
from typing import Optional

class PDFProcessor:
    """Handles PDF text extraction with support for Nepali and English text"""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_file) -> str:
        """
        Extract text from uploaded PDF file using PyMuPDF
        
        Args:
            pdf_file: Streamlit uploaded file object
            
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Read the PDF file
            pdf_bytes = pdf_file.read()
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            extracted_text = ""
            
            # Extract text from each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text with Unicode support (important for Nepali text)
                page_text = page.get_text("text")
                extracted_text += page_text + "\n"
            
            pdf_document.close()
            
            # Clean up the extracted text
            extracted_text = self._clean_text(extracted_text)
            
            return extracted_text
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize line breaks
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Strip whitespace and skip empty lines
            cleaned_line = line.strip()
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def extract_text_with_metadata(self, pdf_file) -> dict:
        """
        Extract text along with metadata from PDF
        
        Args:
            pdf_file: Streamlit uploaded file object
            
        Returns:
            dict: Contains text, page_count, and other metadata
        """
        try:
            pdf_bytes = pdf_file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            result = {
                'text': '',
                'page_count': pdf_document.page_count,
                'metadata': pdf_document.metadata,
                'pages': []
            }
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                page_text = page.get_text("text")
                
                result['pages'].append({
                    'page_number': page_num + 1,
                    'text': page_text,
                    'char_count': len(page_text)
                })
                
                result['text'] += page_text + "\n"
            
            pdf_document.close()
            result['text'] = self._clean_text(result['text'])
            
            return result
            
        except Exception as e:
            st.error(f"Error extracting text with metadata: {str(e)}")
            return {'text': '', 'page_count': 0, 'metadata': {}, 'pages': []}
