import streamlit as st
import io
import zipfile
import os
from pdf_processor import PDFProcessor
from data_parser import DataParser
from form_filler import FormFiller

def main():
    st.set_page_config(
        page_title="PDF Data Extraction & Form Filling",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 PDF Data Extraction & Form Filling Application")
    st.markdown("Extract data from PDFs and automatically fill the editable PDF template with support for and English text.")
    
    # Initialize session state
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    
    # Instructions
    with st.expander("📋 Instructions", expanded=True):
        st.markdown("""
        **How to use this application:**
        1. **Upload Source PDFs**: Upload one or multiple PDFs containing data to extract
        2. **Process Files**: Click the process button to extract data and fill the template
        3. **Download Results**: Download individual files or bulk download as ZIP
        
        **Template**: Uses EditablePdf.pdf as the default template
        **Supported Languages**: English text extraction
        **File Naming**: Output files will be named as `original_filename_filled.pdf`
        """)
    
    # Source PDFs Upload Section
    st.header("1️⃣ Upload Source PDFs")
    source_files = st.file_uploader(
        "Choose PDF files to extract data from",
        type=['pdf'],
        accept_multiple_files=True,
        key="source_uploader",
        help="Upload one or multiple PDF files containing data to extract"
    )
    
    if source_files:
        st.success(f"✅ {len(source_files)} source file(s) uploaded")
        for file in source_files:
            st.write(f"📄 {file.name}")
    
    # Processing Section
    if source_files:
        st.header("2️⃣ Process Files")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            process_button = st.button("🚀 Process All Files", type="primary")
        
        with col2:
            if st.session_state.processed_files:
                st.info(f"Previously processed {len(st.session_state.processed_files)} files")
        
        if process_button:
            # Clear previous results
            st.session_state.processed_files = []
            
            # Initialize processors
            pdf_processor = PDFProcessor()
            data_parser = DataParser()
            form_filler = FormFiller()
            
            # Process each source file
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, source_file in enumerate(source_files):
                try:
                    status_text.text(f"Processing {source_file.name}...")
                    
                    # Extract text from source PDF
                    extracted_text = pdf_processor.extract_text(source_file)
                    
                    if not extracted_text.strip():
                        st.error(f"❌ No text could be extracted from {source_file.name}")
                        continue
                    
                    # Parse extracted data
                    parsed_data = data_parser.parse_data(extracted_text)
                    
                    if not parsed_data:
                        st.error(f"❌ No relevant data could be parsed from {source_file.name}")
                        # Show extracted text for debugging
                        with st.expander(f"Debug: Extracted text from {source_file.name}"):
                            st.text(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
                        continue
                    else:
                        # Show parsed data for debugging
                        with st.expander(f"Debug: Parsed data from {source_file.name}"):
                            st.json(parsed_data)
                    
                    # Fill the template with parsed data (using default EditablePdf.pdf)
                    filled_pdf = form_filler.fill_template_with_default(parsed_data)
                    
                    if filled_pdf:
                        # Generate output filename
                        original_name = os.path.splitext(source_file.name)[0]
                        output_filename = f"{original_name}_filled.pdf"
                        
                        # Store processed file
                        st.session_state.processed_files.append({
                            'original_name': source_file.name,
                            'output_name': output_filename,
                            'pdf_data': filled_pdf,
                            'parsed_data': parsed_data
                        })
                        
                        st.success(f"✅ Successfully processed {source_file.name}")
                    else:
                        st.error(f"❌ Failed to fill template for {source_file.name}")
                
                except Exception as e:
                    st.error(f"❌ Error processing {source_file.name}: {str(e)}")
                
                # Update progress
                progress_bar.progress((i + 1) / len(source_files))
            
            status_text.text("✅ Processing complete!")
            
            if st.session_state.processed_files:
                st.success(f"🎉 Successfully processed {len(st.session_state.processed_files)} out of {len(source_files)} files")
            else:
                st.warning("⚠️ No files were successfully processed")
    
    # Results and Download Section
    if st.session_state.processed_files:
        st.header("3️⃣ Download Results")
        
        # Display processed files with preview
        st.subheader("📋 Processed Files")
        
        for i, file_info in enumerate(st.session_state.processed_files):
            with st.expander(f"📄 {file_info['output_name']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Extracted Data Preview:**")
                    for key, value in file_info['parsed_data'].items():
                        if value and str(value).strip():
                            st.write(f"• **{key}**: {value}")
                
                with col2:
                    st.download_button(
                        label="📥 Download PDF",
                        data=file_info['pdf_data'],
                        file_name=file_info['output_name'],
                        mime="application/pdf",
                        key=f"download_{i}"
                    )
        
        # Bulk download option
        if len(st.session_state.processed_files) > 1:
            st.subheader("📦 Bulk Download")
            
            if st.button("📥 Download All as ZIP"):
                # Create ZIP file in memory
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for file_info in st.session_state.processed_files:
                        zip_file.writestr(file_info['output_name'], file_info['pdf_data'])
                
                zip_buffer.seek(0)
                
                st.download_button(
                    label="📥 Download ZIP File",
                    data=zip_buffer.getvalue(),
                    file_name="filled_pdfs.zip",
                    mime="application/zip"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit | Supports Nepali and English text extraction")

if __name__ == "__main__":
    main()
