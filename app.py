"""
Patent Research Platform
AI-Powered Patent Analysis for Competitive Intelligence
Target Users: R&D Scientists, Competitive Intelligence Analysts, Business Development
"""

import streamlit as st
import os
import time
from datetime import datetime
from typing import List, Dict
from xml_parser_FIXED import parse_patent_xml
from ai_analysis import analyze_patent_with_claude


# ==============================================================================
# DISPLAY FUNCTION - CLEAN SCIENTIFIC RESULTS
# ==============================================================================

def display_results(patent_data, analysis):
    """Display analysis results in a clean, scientific layout"""
    
    st.markdown("---")
    
    # =============================
    # HEADER: Patent ID + Assignee
    # =============================
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### 📋 {patent_data['patent_id']}")
        st.caption(patent_data.get('title', 'Not available'))
    with col2:
        if patent_data.get('company'):
            st.markdown(f"**🏢 {patent_data['company']}**")
    
    st.markdown("---")
    
    # =============================
    # EXECUTIVE SUMMARY
    # =============================
    if 'summary' in analysis and analysis['summary']:
        st.markdown("### 📝 Executive Summary")
        st.info(analysis['summary'])
        st.markdown("")
    
    # =============================
    # KEY INSIGHTS
    # =============================
    if 'key_insights' in analysis and analysis['key_insights']:
        st.markdown("### 🔑 Key Research Findings")
        for i, insight in enumerate(analysis['key_insights'], 1):
            st.markdown(f"**{i}.** {insight}")
        st.markdown("")
    
    # =============================
    # SCIENTIFIC ANALYSIS
    # =============================
    with st.expander("🧬 **Biological Target & Mechanism**", expanded=False):
        if 'biology' in analysis:
            bio = analysis['biology']
            
            if bio.get('targets'):
                st.markdown(f"**🎯 Molecular Targets:** {bio['targets']}")
            
            if bio.get('mechanism'):
                st.markdown(f"**⚙️ Mechanism of Action:** {bio['mechanism']}")
            
            if bio.get('indications'):
                st.markdown(f"**🏥 Therapeutic Indications:** {bio['indications']}")
            
            confidence = bio.get('confidence', 'LOW')
            if confidence == 'HIGH':
                st.success(f"✓ Assessment Confidence: {confidence}")
            elif confidence == 'MEDIUM':
                st.warning(f"⚠ Assessment Confidence: {confidence}")
            else:
                st.info(f"ℹ Assessment Confidence: {confidence}")
    
    with st.expander("⚗️ **Chemical Structure & Novelty**", expanded=False):
        if 'medicinal_chemistry' in analysis:
            chem = analysis['medicinal_chemistry']
            
            if chem.get('series_description'):
                st.markdown(f"**📊 Chemical Series:** {chem['series_description']}")
            
            if chem.get('key_features'):
                st.markdown(f"**✨ Structural Features:** {chem['key_features']}")
            
            # Only show novelty if it's actually specified
            if chem.get('novelty') and 'not specified' not in chem.get('novelty', '').lower():
                st.markdown(f"**🆕 Novelty Assessment:** {chem['novelty']}")
            
            confidence = chem.get('confidence', 'LOW')
            if confidence == 'HIGH':
                st.success(f"✓ Assessment Confidence: {confidence}")
            elif confidence == 'MEDIUM':
                st.warning(f"⚠ Assessment Confidence: {confidence}")
            else:
                st.info(f"ℹ Assessment Confidence: {confidence}")
    
    # =============================
    # PATENT DETAILS
    # =============================
    with st.expander("📄 **Patent Disclosure Details**", expanded=False):
        st.markdown(f"**Patent Number:** `{patent_data['patent_id']}`")
        
        if patent_data.get('company'):
            st.markdown(f"**Assignee:** {patent_data['company']}")
        
        st.markdown(f"**Title:** {patent_data.get('title', 'Not available')}")
        
        if patent_data.get('abstract'):
            st.markdown("**Abstract:**")
            st.write(patent_data['abstract'])
    
    # =============================
    # STRATEGIC ASSESSMENT
    # =============================
    col1, col2 = st.columns(2)
    
    with col1:
        if 'therapeutic_area' in analysis:
            st.markdown(f"**🏥 Therapeutic Area**")
            st.markdown(f"{analysis['therapeutic_area']}")
    
    with col2:
        if 'innovation_level' in analysis:
            innovation = analysis['innovation_level']
            
            # Header with help tooltip
            col_title, col_help = st.columns([3, 1])
            with col_title:
                st.markdown(f"**💡 Innovation Assessment**")
            with col_help:
                st.markdown("ℹ️", help="BREAKTHROUGH: Novel mechanism/target, high commercial potential | INCREMENTAL: Improvement on existing, moderate novelty | DERIVATIVE: Minor variation, lifecycle management")
            
            # Display with color coding and explanation
            if innovation == 'BREAKTHROUGH':
                st.success(f"🚀 {innovation}")
                st.caption("Novel approach, high strategic value")
            elif innovation == 'INCREMENTAL':
                st.warning(f"⚠️ {innovation}")
                st.caption("Optimization of existing, moderate impact")
            else:
                st.info(f"📋 {innovation}")
                st.caption("Minor variation, follow-on patent")
    
    # =============================
    # HELP SECTION
    # =============================
    st.markdown("---")
    
    with st.expander("ℹ️ **Understanding Innovation Assessment**"):
        st.markdown("""
        **Innovation Assessment** evaluates the novelty and strategic significance of the patent technology:
        
        ### 🚀 BREAKTHROUGH
        - **Definition:** Fundamentally new approach or paradigm shift
        - **Examples:** First-in-class mechanism, novel target, completely new scaffold
        - **Strategic Impact:** High commercial potential, strong competitive advantage
        - **Action:** High priority for analysis and competitive response
        
        ### ⚠️ INCREMENTAL  
        - **Definition:** Improvement or optimization of existing technology
        - **Examples:** Me-too drug, improved formulation, modified scaffold, second-generation therapy
        - **Strategic Impact:** Moderate novelty, faster to market, lower differentiation
        - **Action:** Monitor and track, moderate priority
        
        ### 📋 DERIVATIVE
        - **Definition:** Minor variation or follow-on patent
        - **Examples:** Salt form, different dosage, combination therapy, minor structural tweak
        - **Strategic Impact:** Defensive patenting, lifecycle management
        - **Action:** Track for completeness, low competitive threat
        
        ---
        
        **How to Use This Information:**
        - **BREAKTHROUGH patents** from competitors → Assess FTO, consider partnerships, high alert
        - **INCREMENTAL patents** from competitors → Monitor trends, moderate concern
        - **DERIVATIVE patents** → Track but not urgent, likely lifecycle management
        """)


# ==============================================================================
# UNIFIED WATCHLIST MANAGER
# ==============================================================================

from watchlist_manager import WatchlistManager

# Initialize watchlist manager
if 'watchlist_manager' not in st.session_state:
    st.session_state.watchlist_manager = WatchlistManager()


def get_all_patents() -> List[Dict]:
    """Get all tracked patents from both C07 and A61 lists"""
    c07_patents = st.session_state.watchlist_manager.get_watchlist("C07")
    a61_patents = st.session_state.watchlist_manager.get_watchlist("A61")
    
    # Combine and add metadata
    all_patents = []
    for patent in c07_patents:
        patent['category'] = 'Chemistry'
        all_patents.append(patent)
    for patent in a61_patents:
        patent['category'] = 'Medical'
        all_patents.append(patent)
    
    # Sort by added date (newest first)
    all_patents.sort(key=lambda x: x.get('added_date', ''), reverse=True)
    
    return all_patents


# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Patent Research Platform",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    h1 {
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    h3 {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🔬 Patent Research Platform")
st.caption("AI-Powered Analysis for Competitive Intelligence & R&D")
st.markdown("---")

# ==============================================================================
# SIDEBAR: UNIFIED TRACKED PATENTS
# ==============================================================================

with st.sidebar:
    st.markdown("## 📊 Patent Intelligence")
    
    st.markdown("")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Track Patent", use_container_width=True, help="Add patent to tracking list"):
            st.session_state.show_add_patent = True
    with col2:
        if st.button("📤 Bulk Upload", use_container_width=True, help="Upload multiple patents"):
            st.session_state.show_bulk_upload = True
    
    st.markdown("---")
    
    # Add patent dialog
    if st.session_state.get('show_add_patent', False):
        with st.expander("➕ Track New Patent", expanded=True):
            new_patent = st.text_input("Patent Number", key="new_patent", placeholder="WO2024033280")
            category = st.selectbox("Category", options=["Chemistry", "Medical"], key="new_category")
            notes = st.text_input("Notes (optional)", key="new_notes", placeholder="Competitor filing, priority review, etc.")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Add", key="confirm_add", use_container_width=True):
                    if new_patent:
                        # Map category to class
                        patent_class = "C07" if category == "Chemistry" else "A61"
                        
                        success, msg = st.session_state.watchlist_manager.add_patent(
                            patent_class,
                            new_patent.strip(),
                            notes=notes
                        )
                        if success:
                            st.success("✓ Patent tracked!")
                            st.session_state.show_add_patent = False
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(msg)
            with col_b:
                if st.button("Cancel", key="cancel_add", use_container_width=True):
                    st.session_state.show_add_patent = False
                    st.rerun()
    
    # Bulk upload dialog
    if st.session_state.get('show_bulk_upload', False):
        with st.expander("📤 Bulk Upload Patents", expanded=True):
            category = st.selectbox("Category", options=["Chemistry", "Medical"], key="bulk_category")
            csv_file = st.file_uploader("Upload CSV", type=['csv', 'txt'], key="bulk_csv")
            
            st.caption("Format: WO2024033280, Notes (one per line)")
            
            if csv_file:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Import", key="confirm_import", use_container_width=True):
                        csv_content = csv_file.read().decode('utf-8')
                        patent_class = "C07" if category == "Chemistry" else "A61"
                        added, failed = st.session_state.watchlist_manager.add_patents_from_csv(patent_class, csv_content)
                        st.success(f"✓ Imported {added} patents" + (f", {failed} failed" if failed > 0 else ""))
                        st.session_state.show_bulk_upload = False
                        time.sleep(1)
                        st.rerun()
                with col_b:
                    if st.button("Cancel", key="cancel_import", use_container_width=True):
                        st.session_state.show_bulk_upload = False
                        st.rerun()
    
    # Display tracked patents
    st.markdown("### 🔖 Tracked Patents")
    
    all_patents = get_all_patents()
    
    if all_patents:
        st.caption(f"**{len(all_patents)} patents** under surveillance")
        st.markdown("")
        
        for patent in all_patents:
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # Patent button
                    if st.button(
                        f"📄 {patent['id']}", 
                        key=f"patent_{patent['id']}", 
                        use_container_width=True,
                        help="Click to analyze"
                    ):
                        st.session_state.patent_to_analyze = patent['id']
                        st.session_state.auto_analyze = True
                        st.rerun()
                    
                    # Details
                    st.caption(f"🏷️ {patent['category']} | {patent['title'][:40]}...")
                    if patent.get('notes'):
                        st.caption(f"📝 {patent['notes'][:35]}...")
                
                with col2:
                    if st.button("×", key=f"del_{patent['id']}", help="Remove from tracking"):
                        # Determine which list to remove from
                        patent_class = "C07" if patent['category'] == 'Chemistry' else "A61"
                        st.session_state.watchlist_manager.remove_patent(patent_class, patent['id'])
                        st.rerun()
                
                st.markdown("")
    else:
        st.info("No patents tracked yet.\n\nClick **➕ Track Patent** to add your first patent.")
    
    st.markdown("---")
    st.caption("💡 **Cost:** ~$0.02-0.05 per analysis")

# ==============================================================================
# MAIN CONTENT: ANALYSIS TABS
# ==============================================================================

tab1, tab2 = st.tabs(["🔍 Analyze Patent", "📤 Upload Document"])

# =============================
# TAB 1: ANALYZE PATENT
# =============================
with tab1:
    st.markdown("### Patent Analysis")
    st.caption("Enter any WO patent number for instant AI-powered analysis")
    st.caption("⚠️ **Note:** Works best with patents from 2010 onwards. For older patents, use 'Upload Document' tab.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        default_value = st.session_state.get('patent_to_analyze', '')
        
        patent_number = st.text_input(
            "Patent Number",
            value=default_value,
            placeholder="e.g., WO2024033280, WO2025128873",
            help="Enter WO patent publication number",
            key="patent_input",
            label_visibility="collapsed"
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True, key="fetch_btn")
    
    # Auto-analyze if triggered from sidebar
    auto_analyze = st.session_state.get('auto_analyze', False)
    
    if analyze_button or auto_analyze:
        # Clear auto-analyze flag
        if auto_analyze:
            st.session_state.auto_analyze = False
        
        if not patent_number:
            st.error("⚠️ Please enter a patent number")
            st.stop()
        
        if not patent_number.upper().startswith('WO'):
            st.error("⚠️ Please enter a **WO patent number** (e.g., WO2024033280)")
            st.stop()
        
        # Get API key from environment only
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        if not api_key:
            st.error("⚠️ **API Key Required**")
            st.info("**For deployment:** Set `ANTHROPIC_API_KEY` in Streamlit Cloud secrets.\n\n**For local use:** Set environment variable:\n```bash\nexport ANTHROPIC_API_KEY='your-key-here'\n```")
            st.stop()
        
        # Fetch patent
        from google_patents_fetcher import fetch_patent_from_google
        
        with st.spinner(f"🌐 Retrieving patent data for {patent_number}..."):
            patent_data = fetch_patent_from_google(patent_number)
        
        # Error handling AFTER spinner
        if not patent_data:
            st.error(f"❌ Unable to retrieve patent {patent_number}")
            
            # Extract year from patent number to give better guidance
            try:
                year = int(patent_number[2:6])  # WO2006... -> 2006
                if year < 2010:
                    st.warning(f"⚠️ **Older Patent Detected (Year: {year})**\n\nPatents before 2010 may have limited data availability on Google Patents. Try the 'Upload Document' tab instead.")
                else:
                    st.info("💡 **Troubleshooting:**\n- Check patent number format (e.g., WO2024033280)\n- Try the 'Upload Document' tab to upload XML from WIPO\n- Some patents may have restricted access")
            except:
                st.info("💡 **Alternative:** Use the 'Upload Document' tab to upload patent XML file from WIPO")
            
            # Add link to WIPO
            st.markdown(f"🔗 **Search on WIPO:** [Open {patent_number} on WIPO Patentscope](https://patentscope.wipo.int/search/en/detail.jsf?docId={patent_number})")
            st.stop()
        
        st.success(f"✅ Patent data retrieved successfully")
        
        # Analyze with AI
        with st.spinner("🤖 Performing AI analysis..."):
            analysis = analyze_patent_with_claude(patent_data, api_key)
        
        st.success("✅ Analysis complete")
        
        # Display results
        display_results(patent_data, analysis)

# =============================
# TAB 2: UPLOAD DOCUMENT
# =============================
with tab2:
    st.markdown("### Document Upload Analysis")
    st.caption("Upload patent XML file from WIPO for comprehensive analysis")

    uploaded_file = st.file_uploader(
        "Select Patent XML File",
        type=['xml'],
        help="Download XML from WIPO Patentscope"
    )

    if uploaded_file is not None:
        st.success(f"✅ File loaded: {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        
        # Get API key from environment only
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        if not api_key:
            st.error("⚠️ **API Key Required**")
            st.info("**For deployment:** Set `ANTHROPIC_API_KEY` in Streamlit Cloud secrets.\n\n**For local use:** Set environment variable:\n```bash\nexport ANTHROPIC_API_KEY='your-key-here'\n```")
            st.stop()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button("🤖 Analyze Document", type="primary", use_container_width=True, key="upload_btn")
        
        if analyze_button:
            xml_bytes = uploaded_file.read()
            
            with st.spinner("🔍 Parsing document..."):
                patent_data = parse_patent_xml(xml_bytes)
                
                if patent_data.get('patent_id') == 'Not available':
                    st.error("❌ Unable to parse XML file")
                    st.stop()
            
            st.success("✅ Document parsed successfully")
            
            with st.spinner("🤖 Performing AI analysis..."):
                analysis = analyze_patent_with_claude(patent_data, api_key)
            
            st.success("✅ Analysis complete")
            
            display_results(patent_data, analysis)
    else:
        st.info("👆 Upload a patent XML file to begin analysis")
        st.caption("Download XML files from [WIPO Patentscope](https://patentscope.wipo.int/)")

# Footer
st.markdown("---")
st.caption("🔬 Patent Research Platform | AI-Powered by Claude | Research & Competitive Intelligence")
