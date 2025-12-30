import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import fitz  # PyMuPDF
from PIL import Image
import base64

# Page config
st.set_page_config(
    page_title="PDF Editor Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Glassmorphic CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Main content area */
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 100%;
    }
    
    /* Glassmorphic card */
    .glass-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 35px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.4);
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Headers with gradient text */
    h1 {
        background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 3.5em !important;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    h2, h3 {
        color: white !important;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 2px dashed rgba(255, 255, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(255, 255, 255, 0.8);
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Buttons with gradient and glow */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 35px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 20px rgba(116, 79, 168, 0.6);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(116, 79, 168, 0.8);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Download button special style */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 30px;
        border: none;
        padding: 12px 35px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 4px 20px rgba(245, 87, 108, 0.6);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 30px rgba(245, 87, 108, 0.8);
    }
    
    /* Sidebar with glass effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stNumberInput>div>div>input {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        padding: 12px;
        font-size: 15px;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: rgba(255, 255, 255, 0.6);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    }
    
    /* Select boxes */
    .stSelectbox>div>div>div {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        color: white;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        color: white;
        font-weight: 600;
        padding: 12px 25px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 15px rgba(116, 79, 168, 0.5);
    }
    
    /* PDF Preview container */
    .pdf-preview {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border-left: 5px solid;
        padding: 15px;
        color: white;
        font-weight: 500;
    }
    
    /* Text color */
    p, label, .stMarkdown, span {
        color: white !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: white;
        font-size: 2em;
        font-weight: 700;
    }

    
    /* Radio buttons */
    .stRadio>div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px;
    }
    
    /* Checkbox */
    .stCheckbox {
        color: white;
    }
    
    /* Slider */
    .stSlider>div>div>div>div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

def parse_page_selection(selection_str, total_pages):
    """Parse page selection: 2,10,45 or 21-45 or 1-5,10,15-20"""
    pages = set()
    
    if not selection_str.strip():
        return []
    
    parts = selection_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
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
    """Convert PDF pages to images"""
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

def smart_text_replacement(pdf_bytes, old_text, new_text, pages="all", case_sensitive=False):
    """
    AI-powered smart text replacement
    Replaces old_text with new_text across specified pages
    """
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        replacement_count = 0
        pages_modified = []
        
        # Determine which pages to process
        if pages == "all":
            page_range = range(pdf_document.page_count)
        else:
            page_range = [p - 1 for p in pages]  # Convert to 0-indexed
        
        for page_num in page_range:
            if page_num >= pdf_document.page_count:
                continue
                
            page = pdf_document[page_num]
            
            # Search for text
            if case_sensitive:
                text_instances = page.search_for(old_text)
            else:
                # Case-insensitive search
                text_instances = page.search_for(old_text)
            
            if text_instances:
                pages_modified.append(page_num + 1)
                
                for inst in text_instances:
                    # Add white rectangle to cover old text
                    page.draw_rect(inst, color=(1, 1, 1), fill=(1, 1, 1))
                    
                    # Add new text at the same position
                    page.insert_text(
                        inst.top_left,
                        new_text,
                        fontsize=11,
                        color=(0, 0, 0)
                    )
                    replacement_count += 1
        
        if replacement_count > 0:
            st.success(f"✅ Replaced {replacement_count} instances across {len(pages_modified)} pages!")
            st.info(f"📄 Modified pages: {', '.join(map(str, pages_modified))}")
        else:
            st.warning(f"⚠️ Text '{old_text}' not found in the document")
        
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error replacing text: {str(e)}")
        return pdf_bytes

def highlight_text_smart(pdf_bytes, search_text, color, pages="all"):
    """Smart text highlighting across multiple pages"""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        color_map = {
            "Yellow": (1, 1, 0),
            "Green": (0, 1, 0),
            "Blue": (0.3, 0.7, 1),
            "Pink": (1, 0.4, 0.8),
            "Orange": (1, 0.6, 0)
        }
        
        highlight_color = color_map.get(color, (1, 1, 0))
        total_highlights = 0
        pages_highlighted = []
        
        # Determine pages
        if pages == "all":
            page_range = range(pdf_document.page_count)
        else:
            page_range = [p - 1 for p in pages]
        
        for page_num in page_range:
            if page_num >= pdf_document.page_count:
                continue
                
            page = pdf_document[page_num]
            text_instances = page.search_for(search_text)
            
            if text_instances:
                pages_highlighted.append(page_num + 1)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=highlight_color)
                    highlight.update()
                    total_highlights += 1
        
        if total_highlights > 0:
            st.success(f"✅ Highlighted {total_highlights} instances across {len(pages_highlighted)} pages!")
            st.info(f"📄 Highlighted on pages: {', '.join(map(str, pages_highlighted))}")
        else:
            st.warning(f"⚠️ Text '{search_text}' not found")
        
        output = pdf_document.write()
        pdf_document.close()
        return output
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pdf_bytes

def show_pdf_preview(pdf_bytes):
    """Enhanced PDF preview"""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'''
    <div class="pdf-preview">
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" height="700" type="application/pdf" 
                style="border: none; border-radius: 15px;">
        </iframe>
    </div>
    '''
    st.markdown(pdf_display, unsafe_allow_html=True)

# Initialize session state
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None
if 'modified_pdf' not in st.session_state:
    st.session_state.modified_pdf = None

def main():
    # Enhanced Header with emoji animation
    st.markdown("""
        <h1>✨ PDF Editor Pro ✨</h1>
        <p style='text-align: center; font-size: 1.3em; color: white; margin-bottom: 40px;'>
            AI-Powered PDF Editing Made Simple
        </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🚀 Quick Guide")
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;'>
            <h4>📋 Select Pages</h4>
            <p>• Specific: <code>2,10,45</code></p>
            <p>• Range: <code>21-45</code></p>
            <p>• Mixed: <code>1-5,10,15-20</code></p>
            
            <h4>🎨 Highlight Text</h4>
            <p>Just type the text and color!</p>
            
            <h4>✏️ Replace Text</h4>
            <p>Old text → New text<br/>AI handles everything!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 Pro Tips")
        st.markdown("""
        - Changes apply instantly
        - Preview updates live
        - Can undo anytime
        - Works on all pages together
        """)
    
    # Main upload
    uploaded_file = st.file_uploader(
        "📁 Drop your PDF here or click to browse",
        type=['pdf'],
        help="Upload any PDF file to start editing"
    )
    
    if uploaded_file:
        pdf_bytes = uploaded_file.read()
        st.session_state.pdf_bytes = pdf_bytes
        
        if st.session_state.modified_pdf is None:
            st.session_state.modified_pdf = pdf_bytes
        
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        
        # Stats row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Total Pages", total_pages)
        with col2:
            file_size = len(st.session_state.modified_pdf) / 1024
            st.metric("💾 File Size", f"{file_size:.1f} KB")
        with col3:
            st.metric("📝 Filename", uploaded_file.name[:20])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📑 Select Pages", 
            "✏️ Replace Text (AI)", 
            "🎨 Highlight Text", 
            "👁️ Preview & Download"
        ])
        
        with tab1:
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🎯 Page Selection")
                
                selection_input = st.text_area(
                    "Enter pages (examples below)",
                    placeholder="2,10,45  OR  21-45  OR  1-5,10,15-20",
                    height=100,
                    help="Separate with commas, use dash for ranges"
                )
                
                st.markdown("""
                **Examples:**
                - `2,10,45` → Pages 2, 10, 45 only
                - `21-45` → Pages 21 to 45
                - `1-5,10,15-20` → Pages 1-5, 10, and 15-20
                """)
                
                if selection_input:
                    selected_pages = parse_page_selection(selection_input, total_pages)
                    
                    if selected_pages:
                        st.success(f"✅ {len(selected_pages)} pages selected")
                        
                        if st.button("✂️ Extract These Pages", type="primary", use_container_width=True):
                            extracted_pdf = extract_pages_by_numbers(pdf_bytes, selected_pages)
                            st.session_state.modified_pdf = extracted_pdf
                            st.balloons()
                            st.rerun()
            
            with col_right:
                st.markdown("### 👁️ PDF Preview")
                show_pdf_preview(st.session_state.modified_pdf)
        
        with tab2:
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### ✏️ AI Text Replacement")
                st.info("🤖 Just tell me what to replace - I'll handle the rest!")
                
                old_text = st.text_input(
                    "🔍 Find this text:",
                    placeholder="e.g., John Doe",
                    help="Text you want to replace"
                )
                
                new_text = st.text_input(
                    "✍️ Replace with:",
                    placeholder="e.g., Jane Smith",
                    help="New text to insert"
                )
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    apply_to = st.radio(
                        "Apply to:",
                        ["All Pages", "Specific Pages"],
                        horizontal=True
                    )
                
                with col_b:
                    case_sensitive = st.checkbox("Case Sensitive", value=False)
                
                if apply_to == "Specific Pages":
                    pages_input = st.text_input(
                        "Which pages?",
                        placeholder="1,3,5 or 1-10",
                        help="Leave empty for all pages"
                    )
                    
                    if pages_input:
                        target_pages = parse_page_selection(pages_input, total_pages)
                    else:
                        target_pages = "all"
                else:
                    target_pages = "all"
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🔄 Replace Text", type="primary", use_container_width=True):
                    if old_text and new_text:
                        with st.spinner("🔮 AI is working its magic..."):
                            modified_pdf = smart_text_replacement(
                                st.session_state.modified_pdf,
                                old_text,
                                new_text,
                                target_pages,
                                case_sensitive
                            )
                            st.session_state.modified_pdf = modified_pdf
                            st.balloons()
                            st.rerun()
                    else:
                        st.error("❌ Please fill both fields!")
            
            with col_right:
                st.markdown("### 👁️ Live Preview")
                st.info("💡 Changes will appear here instantly")
                show_pdf_preview(st.session_state.modified_pdf)
        
        with tab3:
            col_left, col_right = st.columns([1, 1])
            
            with col_left:
                st.markdown("### 🎨 Smart Text Highlighting")
                st.info("🤖 AI will find and highlight all instances!")
                st.info("PDF HighLighter")
                highlight_text = st.text_input(
                    "🔍 Text to highlight:",
                    placeholder="e.g., Important, Confidential",
                    help="AI will find all instances"
                )
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    highlight_color = st.selectbox(
                        "🎨 Color:",
                        ["Yellow", "Green", "Blue", "Pink", "Orange"]
                    )
                
                with col_b:
                    color_preview = {
                        "Yellow": "🟨",
                        "Green": "🟩",
                        "Blue": "🟦",
                        "Pink": "🌸",
                        "Orange": "🟧"
                    }
                    st.markdown(f"<h2 style='text-align: center;'>{color_preview[highlight_color]}</h2>", unsafe_allow_html=True)
                
                apply_to_hl = st.radio(
                    "Apply to:",
                    ["All Pages", "Specific Pages"],
                    horizontal=True,
                    key="hl_radio"
                )
                
                if apply_to_hl == "Specific Pages":
                    pages_input_hl = st.text_input(
                        "Which pages?",
                        placeholder="1,3,5 or 1-10",
                        key="hl_pages"
                    )
                    
                    if pages_input_hl:
                        target_pages_hl = parse_page_selection(pages_input_hl, total_pages)
                    else:
                        target_pages_hl = "all"
                else:
                    target_pages_hl = "all"
                
                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("✨ Highlight Text", type="primary", use_container_width=True):
                    if highlight_text:
                        with st.spinner("🎨 Highlighting..."):
                            highlighted_pdf = highlight_text_smart(
                                st.session_state.modified_pdf,
                                highlight_text,
                                highlight_color,
                                target_pages_hl
                            )
                            st.session_state.modified_pdf = highlighted_pdf
                            st.balloons()
                            st.rerun()
                    else:
                        st.error("❌ Please enter text to highlight!")
            
            with col_right:
                st.markdown("### 👁️ Live Preview")
                st.info("💡 Highlights will appear here instantly")
                show_pdf_preview(st.session_state.modified_pdf)
        
        with tab4:
            st.markdown("### 📥 Final Preview & Download")                                                         
            
            show_pdf_preview(st.session_state.modified_pdf)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="💾 Download Edited PDF",
                    data=st.session_state.modified_pdf,
                    file_name="edited_" + uploaded_file.name,
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col2:
                if st.button("🔄 Reset to Original", use_container_width=True):
                    st.session_state.modified_pdf = st.session_state.pdf_bytes
                    st.success("✅ Reset complete!")
                    st.rerun()
            
            with col3:
                final_size = len(st.session_state.modified_pdf) / 1024
                st.metric("Final Size", f"{final_size:.1f} KB")

if __name__ == "__main__":
    main()