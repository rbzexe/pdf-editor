import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import fitz  # PyMuPDF
from PIL import Image
import base64

# Page config
st.set_page_config(
    page_title="SYSNET PDF Editor",
    
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
    
    /* Preview box */
    .preview-box {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Text styling */
    p, label, .stMarkdown {
        color: white !important;
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

def parse_page_selection(selection_str, total_pages):
    """
    Parse page selection string
    Examples:
    - "1,3,5" -> [1,3,5]
    - "1-5" -> [1,2,3,4,5]
    - "1-5,10,15-20" -> [1,2,3,4,5,10,15,16,17,18,19,20]
    """
    pages = set()
    
    if not selection_str.strip():
        return []
    
    parts = selection_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                
                if start < 1 or end > total_pages or start > end:
                    st.error(f"❌ Invalid range: {part}")
                    continue
                    
                pages.update(range(start, end + 1))
            except:
                st.error(f"❌ Invalid range format: {part}")
        else:
            # Single page
            try:
                page = int(part)
                if 1 <= page <= total_pages:
                    pages.add(page)
                else:
                    st.error(f"❌ Page {page} out of range (1-{total_pages})")
            except:
                st.error(f"❌ Invalid page number: {part}")
    
    return sorted(list(pages))

def pdf_to_images(pdf_bytes, page_numbers=None):
    """Convert specific PDF pages to images"""
    try:
        images = []
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_numbers is None:
            page_numbers = range(pdf_document.page_count)
        
        for page_num in page_numbers:
            if page_num < pdf_document.page_count:
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append((page_num + 1, img))
        
        pdf_document.close()
        return images
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def extract_pages_by_numbers(pdf_bytes, page_numbers):
    """Extract specific pages from PDF"""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    for page_num in page_numbers:
        if 1 <= page_num <= len(reader.pages):
            writer.add_page(reader.pages[page_num - 1])
    
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()

def highlight_text_in_pdf(pdf_bytes, page_num, search_text, color):
    """Highlight specific text in PDF"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_num < 1 or page_num > pdf_document.page_count:
            st.error(f"❌ Invalid page number: {page_num}")
            return pdf_bytes
        
        page = pdf_document[page_num - 1]
        
        # Color mapping
        color_map = {
            "Yellow": (1, 1, 0),
            "Green": (0, 1, 0),
            "Blue": (0, 0.5, 1),
            "Pink": (1, 0.5, 0.8),
            "Orange": (1, 0.5, 0)
        }
        
        highlight_color = color_map.get(color, (1, 1, 0))
        
        # Search and highlight text
        text_instances = page.search_for(search_text)
        
        for inst in text_instances:
            highlight = page.add_highlight_annot(inst)
            highlight.set_colors(stroke=highlight_color)
            highlight.update()
        
        if len(text_instances) > 0:
            st.success(f"✅ Highlighted {len(text_instances)} instances on page {page_num}")
        else:
            st.warning(f"⚠️ Text '{search_text}' not found on page {page_num}")
        
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error highlighting text: {str(e)}")
        return pdf_bytes

def add_text_to_pdf(pdf_bytes, page_num, text, x, y, font_size, color):
    """Add text to specific position in PDF"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_num < 1 or page_num > pdf_document.page_count:
            st.error(f"❌ Invalid page number: {page_num}")
            return pdf_bytes
        
        page = pdf_document[page_num - 1]
        
        # Color mapping
        color_map = {
            "Black": (0, 0, 0),
            "Red": (1, 0, 0),
            "Blue": (0, 0, 1),
            "Green": (0, 0.5, 0),
            "Purple": (0.5, 0, 0.5)
        }
        
        text_color = color_map.get(color, (0, 0, 0))
        
        # Add text
        page.insert_text(
            (x, y),
            text,
            fontsize=font_size,
            color=text_color
        )
        
        st.success(f"✅ Text added to page {page_num}")
        
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error adding text: {str(e)}")
        return pdf_bytes

def redact_area(pdf_bytes, page_num, x1, y1, x2, y2):
    """Redact/remove text from specific area"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_num < 1 or page_num > pdf_document.page_count:
            st.error(f"❌ Invalid page number: {page_num}")
            return pdf_bytes
        
        page = pdf_document[page_num - 1]
        
        # Create redaction rectangle
        rect = fitz.Rect(x1, y1, x2, y2)
        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        
        st.success(f"✅ Area redacted on page {page_num}")
        
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error redacting area: {str(e)}")
        return pdf_bytes

def show_pdf_preview(pdf_bytes, pages_to_show=None):
    """Show PDF preview inline with better height"""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" style="border-radius: 10px; border: 2px solid rgba(255,255,255,0.3);"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize session state
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'modified_pdf' not in st.session_state:
    st.session_state.modified_pdf = None

def main():
    # Header
    st.markdown("<h1 style='text-align: center; font-size: 3em;'>📄 Advanced PDF Editor Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em; margin-bottom: 30px;'>Complete PDF Editing with Live Preview</p>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎨 Features")
        st.markdown("""
        - ✂️ **Specific Pages** - Select individual pages
        - 📊 **Page Ranges** - Select page ranges
        - 🔀 **Multiple Ranges** - Mix pages and ranges
        - 🎨 **Highlight Text** - Color highlight
        - ✏️ **Add Text** - Write on PDF
        - 🔒 **Redact Area** - Remove sensitive info
        - 👁️ **Live Preview** - See before download
        - 💾 **Instant Download**
        """)
        
        st.markdown("---")
        st.markdown("### 📝 Selection Examples")
        st.markdown("""
        **Specific Pages:**
        - `2,10,45` = Pages 2, 10, 45
        
        **Page Ranges:**
        - `21-45` = Pages 21 to 45
        - `1-5` = Pages 1 to 5
        
        **Mixed Selection:**
        - `1-5,10,15-20` 
        - `2,5-10,25,30-35`
        """)
    
    # Main content
    uploaded_file = st.file_uploader("📁 Upload PDF File", type=['pdf'])
    
    if uploaded_file:
        pdf_bytes = uploaded_file.read()
        st.session_state.pdf_bytes = pdf_bytes
        
        if st.session_state.modified_pdf is None:
            st.session_state.modified_pdf = pdf_bytes
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        st.markdown(f"<h3>📄 Total Pages: {total_pages}</h3>", unsafe_allow_html=True)
        
        # Create tabs for different operations
        tab1, tab2, tab3, tab4 = st.tabs(["📑 Select Pages", "🎨 Highlight Text", "✏️ Edit Text", "👁️ Preview & Download"])
        
        with tab1:
            st.markdown("### 🎯 Page Selection")
            
            # Left side: Controls, Right side: PDF Preview
            left_col, right_col = st.columns([1, 1])
            
            with left_col:
                st.markdown("#### Method 1: Specific Pages")
                st.info("Enter page numbers separated by commas")
                specific_pages = st.text_input(
                    "Example: 2,10,45",
                    placeholder="2,10,45",
                    key="specific"
                )
                
                st.markdown("#### Method 2: Page Ranges")
                st.info("Enter ranges using dash (-)")
                page_ranges = st.text_input(
                    "Example: 21-45 or 1-5,10-15",
                    placeholder="21-45",
                    key="ranges"
                )
            
            with right_col:
                st.markdown("#### 👁️ PDF Preview")
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                show_pdf_preview(st.session_state.modified_pdf)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Combine both inputs
            combined_input = ""
            if specific_pages and page_ranges:
                combined_input = f"{specific_pages},{page_ranges}"
            elif specific_pages:
                combined_input = specific_pages
            elif page_ranges:
                combined_input = page_ranges
            
            if combined_input:
                selected_pages = parse_page_selection(combined_input, total_pages)
                
                if selected_pages:
                    st.success(f"✅ Selected {len(selected_pages)} pages: {', '.join(map(str, selected_pages))}")
                    
                    # Show thumbnails of selected pages
                    st.markdown("### 📸 Selected Pages Preview:")
                    images = pdf_to_images(pdf_bytes, [p-1 for p in selected_pages])
                    
                    cols_per_row = 4
                    for i in range(0, len(images), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, col in enumerate(cols):
                            if i + j < len(images):
                                page_num, img = images[i + j]
                                with col:
                                    st.image(img, caption=f"Page {page_num}", use_container_width=True)
                    
                    if st.button("✂️ Extract Selected Pages", type="primary", key="extract_btn"):
                        extracted_pdf = extract_pages_by_numbers(pdf_bytes, selected_pages)
                        st.session_state.modified_pdf = extracted_pdf
                        st.success(f"✅ Extracted {len(selected_pages)} pages successfully!")
                        st.balloons()
        
        with tab2:
            st.markdown("### 🎨 Highlight Text in PDF")
            
            # Left side: Controls, Right side: PDF Preview
            left_col, right_col = st.columns([1, 1])
            
            with left_col:
                highlight_page = st.number_input(
                    "Page Number",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    key="hl_page"
                )
                
                highlight_text = st.text_input(
                    "Text to Highlight",
                    placeholder="Enter text to find and highlight",
                    key="hl_text"
                )
                
                highlight_color = st.selectbox(
                    "Highlight Color",
                    ["Yellow", "Green", "Blue", "Pink", "Orange"],
                    key="hl_color"
                )
                
                st.markdown("#### Color Preview:")
                color_preview = {
                    "Yellow": "🟨",
                    "Green": "🟩",
                    "Blue": "🟦",
                    "Pink": "🌸",
                    "Orange": "🟧"
                }
                st.markdown(f"### {color_preview[highlight_color]} {highlight_color}")
                
                if st.button("🎨 Apply Highlight", type="primary", key="hl_btn"):
                    if highlight_text:
                        highlighted_pdf = highlight_text_in_pdf(
                            st.session_state.modified_pdf,
                            highlight_page,
                            highlight_text,
                            highlight_color
                        )
                        st.session_state.modified_pdf = highlighted_pdf
                        st.rerun()
                    else:
                        st.error("❌ Please enter text to highlight!")
            
            with right_col:
                st.markdown("#### 👁️ PDF Preview")
                st.info(f"📄 Currently viewing Page {highlight_page}")
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                show_pdf_preview(st.session_state.modified_pdf)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown("### ✏️ Edit PDF Text")
            
            edit_option = st.radio(
                "Choose Action:",
                ["Add New Text", "Redact/Remove Area"],
                key="edit_option",
                horizontal=True
            )
            
            # Left side: Controls, Right side: PDF Preview
            left_col, right_col = st.columns([1, 1])
            
            with left_col:
                if edit_option == "Add New Text":
                    add_page = st.number_input(
                        "Page Number",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key="add_page"
                    )
                    
                    add_text = st.text_area(
                        "Text to Add",
                        placeholder="Enter your text here...",
                        key="add_text",
                        height=100
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        add_x = st.number_input("X Position", value=100, key="add_x")
                        add_font_size = st.slider("Font Size", 8, 48, 12, key="add_font")
                    
                    with col_b:
                        add_y = st.number_input("Y Position", value=100, key="add_y")
                        add_color = st.selectbox(
                            "Text Color",
                            ["Black", "Red", "Blue", "Green", "Purple"],
                            key="add_color"
                        )
                    
                    st.info("💡 Tip: See the PDF preview on right to find the right position")
                    
                    if st.button("✏️ Add Text", type="primary", key="add_btn"):
                        if add_text:
                            modified_pdf = add_text_to_pdf(
                                st.session_state.modified_pdf,
                                add_page,
                                add_text,
                                add_x,
                                add_y,
                                add_font_size,
                                add_color
                            )
                            st.session_state.modified_pdf = modified_pdf
                            st.rerun()
                        else:
                            st.error("❌ Please enter text to add!")
                
                else:  # Redact Area
                    st.markdown("#### 🔒 Redact/Remove Sensitive Information")
                    
                    redact_page = st.number_input(
                        "Page Number",
                        min_value=1,
                        max_value=total_pages,
                        value=1,
                        key="redact_page"
                    )
                    
                    st.markdown("**Top-Left Corner:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        redact_x1 = st.number_input("X1", value=100, key="redact_x1")
                    with col_b:
                        redact_y1 = st.number_input("Y1", value=100, key="redact_y1")
                    
                    st.markdown("**Bottom-Right Corner:**")
                    col_c, col_d = st.columns(2)
                    with col_c:
                        redact_x2 = st.number_input("X2", value=300, key="redact_x2")
                    with col_d:
                        redact_y2 = st.number_input("Y2", value=150, key="redact_y2")
                    
                    st.warning("⚠️ This will permanently remove text in the selected area")
                    st.info("💡 Tip: See the PDF preview to identify coordinates")
                    
                    if st.button("🔒 Redact Area", type="primary", key="redact_btn"):
                        redacted_pdf = redact_area(
                            st.session_state.modified_pdf,
                            redact_page,
                            redact_x1,
                            redact_y1,
                            redact_x2,
                            redact_y2
                        )
                        st.session_state.modified_pdf = redacted_pdf
                        st.rerun()
            
            with right_col:
                st.markdown("#### 👁️ PDF Preview")
                current_page = add_page if edit_option == "Add New Text" else redact_page
                st.info(f"📄 Currently viewing Page {current_page}")
                st.markdown('<div class="preview-box">', unsafe_allow_html=True)
                show_pdf_preview(st.session_state.modified_pdf)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown("### 👁️ Live Preview")
            
            if st.session_state.modified_pdf:
                st.markdown("#### 📄 Current PDF Preview:")
                show_pdf_preview(st.session_state.modified_pdf)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="💾 Download Edited PDF",
                        data=st.session_state.modified_pdf,
                        file_name="edited_" + uploaded_file.name,
                        mime="application/pdf",
                        type="primary"
                    )
                
                with col2:
                    if st.button("🔄 Reset to Original", key="reset_btn"):
                        st.session_state.modified_pdf = st.session_state.pdf_bytes
                        st.success("✅ Reset to original PDF!")
                        st.rerun()
                
                with col3:
                    pdf_size = len(st.session_state.modified_pdf) / 1024
                    st.metric("File Size", f"{pdf_size:.1f} KB")
            else:
                st.info("ℹ️ Make some changes to see the preview")

if __name__ == "__main__":
    main()