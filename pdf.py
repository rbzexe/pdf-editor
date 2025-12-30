import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import fitz  # PyMuPDF
from PIL import Image

# Page config
st.set_page_config(
    page_title="PDF Editor Pro",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for glassmorphic design
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Glassmorphic container */
    .glass-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin: 20px 0;
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 2px dashed rgba(255, 255, 255, 0.3);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        border: none;
        padding: 10px 30px;
        font-weight: bold;
        box-shadow: 0 4px 15px 0 rgba(116, 79, 168, 0.75);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(116, 79, 168, 0.9);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        backdrop-filter: blur(10px);
    }
    
    /* Info box */
    .stInfo {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border-left: 5px solid rgba(255, 255, 255, 0.5);
    }
    
    /* Page thumbnail container */
    .page-thumbnail {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
        margin: 10px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        transition: all 0.3s ease;
    }
    
    .page-thumbnail:hover {
        transform: scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    /* Text styling */
    p, label, .stMarkdown {
        color: white !important;
    }
    
    /* Checkbox styling */
    .stCheckbox {
        color: white !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError {
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
    
    /* Select box styling */
    .stSelectbox {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def pdf_to_images(pdf_bytes):
    """Convert PDF pages to images using PyMuPDF"""
    try:
        images = []
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            # Render page to image with reasonable resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        
        pdf_document.close()
        return images
    except Exception as e:
        st.error(f"Error converting PDF to images: {str(e)}")
        return []

def remove_pages(pdf_bytes, pages_to_keep):
    """Remove pages from PDF"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for page_num in pages_to_keep:
        writer.add_page(reader.pages[page_num])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def rotate_pages(pdf_bytes, page_rotations):
    """Rotate specific pages"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for i, page in enumerate(reader.pages):
        if i in page_rotations:
            page.rotate(page_rotations[i])
        writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def merge_pdfs(pdf_files):
    """Merge multiple PDFs"""
    writer = PdfWriter()
    
    for pdf_file in pdf_files:
        reader = PdfReader(io.BytesIO(pdf_file))
        for page in reader.pages:
            writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def split_pdf(pdf_bytes, split_points):
    """Split PDF into multiple files"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pdfs = []
    
    split_points = [0] + sorted(split_points) + [len(reader.pages)]
    
    for i in range(len(split_points) - 1):
        writer = PdfWriter()
        for page_num in range(split_points[i], split_points[i + 1]):
            writer.add_page(reader.pages[page_num])
        
        output = io.BytesIO()
        writer.write(output)
        output.seek(0)
        pdfs.append(output.getvalue())
    
    return pdfs

def extract_pages(pdf_bytes, pages_to_extract):
    """Extract specific pages into a new PDF"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for page_num in pages_to_extract:
        writer.add_page(reader.pages[page_num])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def reorder_pages(pdf_bytes, new_order):
    """Reorder pages based on new order list"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for page_num in new_order:
        writer.add_page(reader.pages[page_num])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def add_watermark(pdf_bytes, watermark_text):
    """Add watermark to PDF pages"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # Get page dimensions
            rect = page.rect
            
            # Add watermark text
            text_rect = fitz.Rect(50, rect.height - 50, rect.width - 50, rect.height - 20)
            page.insert_textbox(
                text_rect,
                watermark_text,
                fontsize=12,
                color=(0.7, 0.7, 0.7),
                align=fitz.TEXT_ALIGN_CENTER
            )
        
        # Save to bytes
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error adding watermark: {str(e)}")
        return pdf_bytes

# Main app
def main():
    # Header
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>📄 PDF Editor Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; margin-bottom: 30px;'>Your Complete PDF Editing Solution</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎨 Features")
        st.markdown("""
        - ✂️ Remove Pages
        - 🔄 Rotate Pages
        - 🔗 Merge PDFs
        - ✨ Split PDF
        - 📤 Extract Pages
        - 🔀 Reorder Pages
        - 💧 Add Watermark
        - 💾 Download Edited PDF
        """)
        
        st.markdown("---")
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. Upload your PDF file
        2. Select operation
        3. Choose pages
        4. Download result
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Tips")
        st.markdown("""
        - All operations are instant
        - No file size limits
        - Works offline
        - Privacy protected
        """)
    
    # Operation selection
    operation = st.selectbox(
        "🛠️ Select Operation",
        ["Remove Pages", "Rotate Pages", "Merge PDFs", "Split PDF", "Extract Pages", "Reorder Pages", "Add Watermark"]
    )
    
    # File upload
    if operation == "Merge PDFs":
        uploaded_files = st.file_uploader(
            "📁 Upload PDF Files to Merge",
            type=['pdf'],
            accept_multiple_files=True
        )
    else:
        uploaded_file = st.file_uploader(
            "📁 Upload PDF File",
            type=['pdf']
        )
    
    # Process based on operation
    if operation == "Remove Pages" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        
        # Display thumbnails
        images = pdf_to_images(pdf_bytes)
        
        if images:
            st.markdown("### Select Pages to KEEP:")
            
            cols_per_row = 4
            selected_pages = []
            
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        with col:
                            st.image(images[i + j], use_container_width=True)
                            if st.checkbox(f"Page {i + j + 1}", key=f"keep_{i+j}", value=True):
                                selected_pages.append(i + j)
            
            if st.button("🗑️ Remove Unselected Pages", type="primary"):
                if selected_pages:
                    edited_pdf = remove_pages(pdf_bytes, selected_pages)
                    st.success(f"✅ Removed {total_pages - len(selected_pages)} pages!")
                    
                    st.download_button(
                        label="💾 Download Edited PDF",
                        data=edited_pdf,
                        file_name="edited_" + uploaded_file.name,
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ Please select at least one page to keep!")
    
    elif operation == "Rotate Pages" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        
        images = pdf_to_images(pdf_bytes)
        
        if images:
            st.markdown("### Select Pages and Rotation:")
            
            page_rotations = {}
            cols_per_row = 3
            
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        with col:
                            st.image(images[i + j], use_container_width=True)
                            rotation = st.selectbox(
                                f"Page {i + j + 1}",
                                [0, 90, 180, 270],
                                key=f"rotate_{i+j}"
                            )
                            if rotation != 0:
                                page_rotations[i + j] = rotation
            
            if st.button("🔄 Apply Rotations", type="primary"):
                if page_rotations:
                    edited_pdf = rotate_pages(pdf_bytes, page_rotations)
                    st.success(f"✅ Rotated {len(page_rotations)} pages!")
                    
                    st.download_button(
                        label="💾 Download Rotated PDF",
                        data=edited_pdf,
                        file_name="rotated_" + uploaded_file.name,
                        mime="application/pdf"
                    )
                else:
                    st.info("ℹ️ No rotations selected")
    
    elif operation == "Merge PDFs" and uploaded_files:
        if len(uploaded_files) < 2:
            st.warning("⚠️ Please upload at least 2 PDF files to merge")
        else:
            st.markdown(f"<h3>📚 Files to Merge: {len(uploaded_files)}</h3>", unsafe_allow_html=True)
            
            for idx, file in enumerate(uploaded_files):
                st.markdown(f"**{idx + 1}.** {file.name}")
            
            if st.button("🔗 Merge PDFs", type="primary"):
                pdf_files = [file.read() for file in uploaded_files]
                merged_pdf = merge_pdfs(pdf_files)
                
                st.success(f"✅ Merged {len(uploaded_files)} PDFs successfully!")
                
                st.download_button(
                    label="💾 Download Merged PDF",
                    data=merged_pdf,
                    file_name="merged_document.pdf",
                    mime="application/pdf"
                )
    
    elif operation == "Split PDF" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        st.markdown("### Enter page numbers where you want to split (comma-separated):")
        st.info("Example: 3,7,12 will create 4 PDFs (pages 1-3, 4-7, 8-12, 13-end)")
        
        split_input = st.text_input("Split points:", "")
        
        if st.button("✂️ Split PDF", type="primary"):
            if split_input:
                try:
                    split_points = [int(x.strip()) for x in split_input.split(",")]
                    split_points = [p for p in split_points if 0 < p < total_pages]
                    
                    if split_points:
                        pdfs = split_pdf(pdf_bytes, split_points)
                        st.success(f"✅ Split into {len(pdfs)} PDFs!")
                        
                        for idx, pdf_data in enumerate(pdfs):
                            st.download_button(
                                label=f"💾 Download Part {idx + 1}",
                                data=pdf_data,
                                file_name=f"split_{idx + 1}_{uploaded_file.name}",
                                mime="application/pdf",
                                key=f"download_{idx}"
                            )
                    else:
                        st.error("❌ Invalid split points!")
                except:
                    st.error("❌ Invalid input! Use comma-separated numbers.")
            else:
                st.error("❌ Please enter split points!")
    
    elif operation == "Extract Pages" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        
        images = pdf_to_images(pdf_bytes)
        
        if images:
            st.markdown("### Select Pages to Extract:")
            
            cols_per_row = 4
            pages_to_extract = []
            
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        with col:
                            st.image(images[i + j], use_container_width=True)
                            if st.checkbox(f"Page {i + j + 1}", key=f"extract_{i+j}"):
                                pages_to_extract.append(i + j)
            
            if st.button("📤 Extract Selected Pages", type="primary"):
                if pages_to_extract:
                    extracted_pdf = extract_pages(pdf_bytes, pages_to_extract)
                    st.success(f"✅ Extracted {len(pages_to_extract)} pages!")
                    
                    st.download_button(
                        label="💾 Download Extracted Pages",
                        data=extracted_pdf,
                        file_name="extracted_" + uploaded_file.name,
                        mime="application/pdf"
                    )
                else:
                    st.error("❌ Please select at least one page to extract!")
    
    elif operation == "Reorder Pages" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        
        images = pdf_to_images(pdf_bytes)
        
        if images:
            st.markdown("### Drag to Reorder (or enter custom order):")
            st.info("Enter page numbers in desired order (comma-separated). Example: 3,1,2 will reorder to page 3, then 1, then 2")
            
            default_order = ",".join(str(i+1) for i in range(total_pages))
            order_input = st.text_input("New order:", default_order)
            
            # Display current order preview
            cols_per_row = 4
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        with col:
                            st.image(images[i + j], use_container_width=True)
                            st.caption(f"Page {i + j + 1}")
            
            if st.button("🔀 Reorder Pages", type="primary"):
                try:
                    new_order = [int(x.strip())-1 for x in order_input.split(",")]
                    
                    if len(new_order) != total_pages:
                        st.error(f"❌ Please specify all {total_pages} pages!")
                    elif set(new_order) != set(range(total_pages)):
                        st.error("❌ Invalid page numbers!")
                    else:
                        reordered_pdf = reorder_pages(pdf_bytes, new_order)
                        st.success("✅ Pages reordered successfully!")
                        
                        st.download_button(
                            label="💾 Download Reordered PDF",
                            data=reordered_pdf,
                            file_name="reordered_" + uploaded_file.name,
                            mime="application/pdf"
                        )
                except:
                    st.error("❌ Invalid input! Use comma-separated page numbers.")
    
    elif operation == "Add Watermark" and uploaded_file:
        pdf_bytes = uploaded_file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        st.markdown("### Enter Watermark Text:")
        
        watermark_text = st.text_input("Watermark:", "CONFIDENTIAL")
        
        if st.button("💧 Add Watermark", type="primary"):
            if watermark_text:
                watermarked_pdf = add_watermark(pdf_bytes, watermark_text)
                st.success("✅ Watermark added successfully!")
                
                st.download_button(
                    label="💾 Download Watermarked PDF",
                    data=watermarked_pdf,
                    file_name="watermarked_" + uploaded_file.name,
                    mime="application/pdf"
                )
            else:
                st.error("❌ Please enter watermark text!")

if __name__ == "__main__":
    main()