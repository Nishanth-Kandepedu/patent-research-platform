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
    
    # =============================
    # EXPORT FUNCTIONALITY - Direct download links
    # =============================
    st.markdown("---")
    
    st.markdown("### 📥 Export Analysis")
    st.caption("💡 Click to download file directly")
    
    # Generate all export formats
    export_md = generate_export_report_markdown(patent_data, analysis)
    export_html = generate_export_report_html(patent_data, analysis)
    export_csv = generate_export_data_csv(patent_data, analysis)
    
    # Create data URLs with download attribute
    import base64
    
    # Base64 encode for data URLs
    md_b64 = base64.b64encode(export_md.encode()).decode()
    html_b64 = base64.b64encode(export_html.encode()).decode()
    csv_b64 = base64.b64encode(export_csv.encode()).decode()
    
    patent_id = patent_data['patent_id']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <a href="data:text/markdown;base64,{md_b64}" 
           download="{patent_id}_report.md"
           style="display: inline-block; width: 100%; padding: 0.5rem 1rem; background-color: #FF4B4B; color: white; text-align: center; text-decoration: none; border-radius: 0.25rem; font-weight: 500;">
            📄 Markdown
        </a>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <a href="data:text/html;base64,{html_b64}" 
           download="{patent_id}_report.html"
           style="display: inline-block; width: 100%; padding: 0.5rem 1rem; background-color: #FF4B4B; color: white; text-align: center; text-decoration: none; border-radius: 0.25rem; font-weight: 500;">
            📄 HTML/PDF
        </a>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <a href="data:text/csv;base64,{csv_b64}" 
           download="{patent_id}_data.csv"
           style="display: inline-block; width: 100%; padding: 0.5rem 1rem; background-color: #FF4B4B; color: white; text-align: center; text-decoration: none; border-radius: 0.25rem; font-weight: 500;">
            📊 CSV Data
        </a>
        ''', unsafe_allow_html=True)
    
    st.caption("📌 **Files download directly** | Open HTML in browser, then Print → Save as PDF for professional reports")


def generate_export_report_markdown(patent_data: Dict, analysis: Dict) -> str:
    """Generate a comprehensive report for export"""
    
    report = f"""# Patent Analysis Report
# {patent_data['patent_id']}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Platform:** Patent Research Platform (AI-Powered by Claude)

---

## Patent Information

**Patent Number:** {patent_data['patent_id']}
**Title:** {patent_data.get('title', 'Not available')}
**Assignee:** {patent_data.get('company', 'Not available')}

**Abstract:**
{patent_data.get('abstract', 'Not available')}

---

## Executive Summary

{analysis.get('summary', 'Not available')}

---

## Key Research Findings

"""
    
    # Add key insights
    if 'key_insights' in analysis and analysis['key_insights']:
        for i, insight in enumerate(analysis['key_insights'], 1):
            report += f"{i}. {insight}\n"
    else:
        report += "Not available\n"
    
    report += "\n---\n\n## Biological Target & Mechanism Analysis\n\n"
    
    # Add biology section
    if 'biology' in analysis:
        bio = analysis['biology']
        if bio.get('targets'):
            report += f"**Molecular Targets:** {bio['targets']}\n\n"
        if bio.get('mechanism'):
            report += f"**Mechanism of Action:** {bio['mechanism']}\n\n"
        if bio.get('indications'):
            report += f"**Therapeutic Indications:** {bio['indications']}\n\n"
        report += f"**Assessment Confidence:** {bio.get('confidence', 'Not specified')}\n"
    else:
        report += "Not available\n"
    
    report += "\n---\n\n## Chemical Structure & Novelty Assessment\n\n"
    
    # Add chemistry section
    if 'medicinal_chemistry' in analysis:
        chem = analysis['medicinal_chemistry']
        if chem.get('series_description'):
            report += f"**Chemical Series:** {chem['series_description']}\n\n"
        if chem.get('key_features'):
            report += f"**Structural Features:** {chem['key_features']}\n\n"
        if chem.get('novelty') and 'not specified' not in chem.get('novelty', '').lower():
            report += f"**Novelty Assessment:** {chem['novelty']}\n\n"
        report += f"**Assessment Confidence:** {chem.get('confidence', 'Not specified')}\n"
    else:
        report += "Not available\n"
    
    report += "\n---\n\n## Strategic Assessment\n\n"
    
    # Add strategic info
    if 'therapeutic_area' in analysis:
        report += f"**Therapeutic Area:** {analysis['therapeutic_area']}\n\n"
    
    if 'innovation_level' in analysis:
        innovation = analysis['innovation_level']
        report += f"**Innovation Assessment:** {innovation}\n\n"
        
        # Add innovation explanation
        if innovation == 'BREAKTHROUGH':
            report += "*Novel approach with high strategic value. First-in-class mechanism or completely new scaffold. High commercial potential and strong competitive advantage.*\n\n"
        elif innovation == 'INCREMENTAL':
            report += "*Improvement or optimization of existing technology. Me-too drug or modified scaffold. Moderate novelty with faster time to market but lower differentiation.*\n\n"
        else:
            report += "*Minor variation or follow-on patent. Salt form, different dosage, or minor structural tweak. Defensive patenting for lifecycle management.*\n\n"
    
    report += "\n---\n\n## Competitive Intelligence Recommendations\n\n"
    
    # Add recommendations based on innovation level
    if 'innovation_level' in analysis:
        innovation = analysis['innovation_level']
        if innovation == 'BREAKTHROUGH':
            report += """**Recommended Actions:**
- Conduct immediate freedom-to-operate (FTO) analysis
- Assess potential licensing or partnership opportunities
- Monitor for subsequent filings in this series
- Evaluate impact on your development pipeline
- Consider competitive response strategies
- High priority for detailed claim analysis

**Strategic Priority:** HIGH ⚠️
"""
        elif innovation == 'INCREMENTAL':
            report += """**Recommended Actions:**
- Monitor for market entry timelines
- Track clinical development progress
- Assess differentiation vs. existing therapies
- Evaluate commercial threat level
- Review for potential workarounds
- Medium priority for detailed analysis

**Strategic Priority:** MEDIUM
"""
        else:
            report += """**Recommended Actions:**
- Track as part of routine surveillance
- Note for lifecycle management monitoring
- Low immediate competitive threat
- File for reference in patent landscape
- Review during periodic portfolio updates

**Strategic Priority:** LOW
"""
    
    report += f"""
---

## Document Information

**Analysis Date:** {datetime.now().strftime("%B %d, %Y")}
**Analysis Time:** {datetime.now().strftime("%H:%M:%S")}
**Platform:** Patent Research Platform
**AI Model:** Claude (Anthropic)
**Report Format:** Markdown

---

*This report was generated using AI analysis. Please verify critical details with the original patent document.*
"""
    
    return report


def generate_export_report_html(patent_data: Dict, analysis: Dict) -> str:
    """Generate a professional HTML report (can be printed to PDF)"""
    
    # Generate HTML version of report
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                color: #333;
            }}
            h1 {{
                color: #1f77b4;
                border-bottom: 3px solid #1f77b4;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #2c5aa0;
                margin-top: 30px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }}
            .header {{
                background-color: #f0f0f0;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
            }}
            .section {{
                margin: 20px 0;
                padding: 15px;
                background-color: #f9f9f9;
                border-left: 4px solid #1f77b4;
            }}
            .highlight {{
                background-color: #fff9e6;
                padding: 10px;
                border-radius: 3px;
            }}
            .priority-high {{
                color: #d32f2f;
                font-weight: bold;
            }}
            .priority-medium {{
                color: #f57c00;
                font-weight: bold;
            }}
            .priority-low {{
                color: #388e3c;
                font-weight: bold;
            }}
            ul {{
                line-height: 1.8;
            }}
        </style>
    </head>
    <body>
        <h1>Patent Analysis Report</h1>
        <div class="header">
            <h2>{patent_data['patent_id']}</h2>
            <p><strong>Generated:</strong> {datetime.now().strftime("%B %d, %Y at %H:%M")}</p>
            <p><strong>Platform:</strong> Patent Research Platform (AI-Powered by Claude)</p>
        </div>
        
        <h2>Patent Information</h2>
        <div class="section">
            <p><strong>Patent Number:</strong> {patent_data['patent_id']}</p>
            <p><strong>Title:</strong> {patent_data.get('title', 'Not available')}</p>
            <p><strong>Assignee:</strong> {patent_data.get('company', 'Not available')}</p>
            <p><strong>Abstract:</strong><br>{patent_data.get('abstract', 'Not available')}</p>
        </div>
        
        <h2>Executive Summary</h2>
        <div class="section highlight">
            <p>{analysis.get('summary', 'Not available')}</p>
        </div>
        
        <h2>Key Research Findings</h2>
        <div class="section">
            <ul>
"""
    
    # Add key insights
    if 'key_insights' in analysis and analysis['key_insights']:
        for insight in analysis['key_insights']:
            html_content += f"                <li>{insight}</li>\n"
    else:
        html_content += "                <li>Not available</li>\n"
    
    html_content += """            </ul>
        </div>
        
        <h2>Biological Target & Mechanism</h2>
        <div class="section">
"""
    
    # Add biology section
    if 'biology' in analysis:
        bio = analysis['biology']
        if bio.get('targets'):
            html_content += f"            <p><strong>Molecular Targets:</strong> {bio['targets']}</p>\n"
        if bio.get('mechanism'):
            html_content += f"            <p><strong>Mechanism of Action:</strong> {bio['mechanism']}</p>\n"
        if bio.get('indications'):
            html_content += f"            <p><strong>Therapeutic Indications:</strong> {bio['indications']}</p>\n"
        html_content += f"            <p><strong>Assessment Confidence:</strong> {bio.get('confidence', 'Not specified')}</p>\n"
    else:
        html_content += "            <p>Not available</p>\n"
    
    html_content += """        </div>
        
        <h2>Chemical Structure & Novelty</h2>
        <div class="section">
"""
    
    # Add chemistry section
    if 'medicinal_chemistry' in analysis:
        chem = analysis['medicinal_chemistry']
        if chem.get('series_description'):
            html_content += f"            <p><strong>Chemical Series:</strong> {chem['series_description']}</p>\n"
        if chem.get('key_features'):
            html_content += f"            <p><strong>Structural Features:</strong> {chem['key_features']}</p>\n"
        if chem.get('novelty') and 'not specified' not in chem.get('novelty', '').lower():
            html_content += f"            <p><strong>Novelty Assessment:</strong> {chem['novelty']}</p>\n"
        html_content += f"            <p><strong>Assessment Confidence:</strong> {chem.get('confidence', 'Not specified')}</p>\n"
    else:
        html_content += "            <p>Not available</p>\n"
    
    html_content += """        </div>
        
        <h2>Strategic Assessment</h2>
        <div class="section">
"""
    
    # Add strategic info
    if 'therapeutic_area' in analysis:
        html_content += f"            <p><strong>Therapeutic Area:</strong> {analysis['therapeutic_area']}</p>\n"
    
    if 'innovation_level' in analysis:
        innovation = analysis['innovation_level']
        priority_class = 'priority-high' if innovation == 'BREAKTHROUGH' else ('priority-medium' if innovation == 'INCREMENTAL' else 'priority-low')
        html_content += f"            <p><strong>Innovation Assessment:</strong> <span class='{priority_class}'>{innovation}</span></p>\n"
    
    html_content += """        </div>
        
        <div style="page-break-before: always;"></div>
        
        <h2>Competitive Intelligence Recommendations</h2>
        <div class="section highlight">
"""
    
    # Add recommendations
    if 'innovation_level' in analysis:
        innovation = analysis['innovation_level']
        if innovation == 'BREAKTHROUGH':
            html_content += """
            <p><strong>Recommended Actions:</strong></p>
            <ul>
                <li>Conduct immediate freedom-to-operate (FTO) analysis</li>
                <li>Assess potential licensing or partnership opportunities</li>
                <li>Monitor for subsequent filings in this series</li>
                <li>Evaluate impact on your development pipeline</li>
                <li>Consider competitive response strategies</li>
                <li>High priority for detailed claim analysis</li>
            </ul>
            <p class="priority-high">Strategic Priority: HIGH ⚠️</p>
"""
        elif innovation == 'INCREMENTAL':
            html_content += """
            <p><strong>Recommended Actions:</strong></p>
            <ul>
                <li>Monitor for market entry timelines</li>
                <li>Track clinical development progress</li>
                <li>Assess differentiation vs. existing therapies</li>
                <li>Evaluate commercial threat level</li>
                <li>Review for potential workarounds</li>
                <li>Medium priority for detailed analysis</li>
            </ul>
            <p class="priority-medium">Strategic Priority: MEDIUM</p>
"""
        else:
            html_content += """
            <p><strong>Recommended Actions:</strong></p>
            <ul>
                <li>Track as part of routine surveillance</li>
                <li>Note for lifecycle management monitoring</li>
                <li>Low immediate competitive threat</li>
                <li>File for reference in patent landscape</li>
                <li>Review during periodic portfolio updates</li>
            </ul>
            <p class="priority-low">Strategic Priority: LOW</p>
"""
    
    html_content += f"""        </div>
        
        <hr style="margin-top: 40px;">
        <p style="text-align: center; color: #666; font-size: 12px;">
            Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")} | 
            Patent Research Platform | 
            AI-Powered by Claude
        </p>
        <p style="text-align: center; color: #999; font-size: 11px; margin-top: 10px;">
            💡 To convert to PDF: Open this file in your browser → Print → Save as PDF
        </p>
    </body>
    </html>
    """
    
    return html_content


def generate_export_data_csv(patent_data: Dict, analysis: Dict) -> str:
    """Generate a CSV with structured data for spreadsheet analysis"""
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Patent Analysis Data Export'])
    writer.writerow(['Generated', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])
    
    # Patent Information Section
    writer.writerow(['PATENT INFORMATION'])
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Patent Number', patent_data['patent_id']])
    writer.writerow(['Title', patent_data.get('title', 'Not available')])
    writer.writerow(['Assignee', patent_data.get('company', 'Not available')])
    writer.writerow(['Abstract', patent_data.get('abstract', 'Not available')])
    writer.writerow([])
    
    # Executive Summary
    writer.writerow(['EXECUTIVE SUMMARY'])
    writer.writerow(['Summary', analysis.get('summary', 'Not available')])
    writer.writerow([])
    
    # Key Insights
    writer.writerow(['KEY RESEARCH FINDINGS'])
    writer.writerow(['#', 'Finding'])
    if 'key_insights' in analysis and analysis['key_insights']:
        for i, insight in enumerate(analysis['key_insights'], 1):
            writer.writerow([i, insight])
    else:
        writer.writerow([1, 'Not available'])
    writer.writerow([])
    
    # Biology Section
    writer.writerow(['BIOLOGICAL ANALYSIS'])
    writer.writerow(['Field', 'Value'])
    if 'biology' in analysis:
        bio = analysis['biology']
        writer.writerow(['Molecular Targets', bio.get('targets', 'Not specified')])
        writer.writerow(['Mechanism of Action', bio.get('mechanism', 'Not specified')])
        writer.writerow(['Therapeutic Indications', bio.get('indications', 'Not specified')])
        writer.writerow(['Assessment Confidence', bio.get('confidence', 'Not specified')])
    else:
        writer.writerow(['Status', 'Not available'])
    writer.writerow([])
    
    # Chemistry Section
    writer.writerow(['CHEMICAL ANALYSIS'])
    writer.writerow(['Field', 'Value'])
    if 'medicinal_chemistry' in analysis:
        chem = analysis['medicinal_chemistry']
        writer.writerow(['Chemical Series', chem.get('series_description', 'Not specified')])
        writer.writerow(['Structural Features', chem.get('key_features', 'Not specified')])
        if chem.get('novelty') and 'not specified' not in chem.get('novelty', '').lower():
            writer.writerow(['Novelty Assessment', chem.get('novelty', 'Not specified')])
        writer.writerow(['Assessment Confidence', chem.get('confidence', 'Not specified')])
    else:
        writer.writerow(['Status', 'Not available'])
    writer.writerow([])
    
    # Strategic Assessment
    writer.writerow(['STRATEGIC ASSESSMENT'])
    writer.writerow(['Field', 'Value'])
    writer.writerow(['Therapeutic Area', analysis.get('therapeutic_area', 'Not specified')])
    writer.writerow(['Innovation Assessment', analysis.get('innovation_level', 'Not specified')])
    
    # Map innovation level to priority
    innovation = analysis.get('innovation_level', '')
    if innovation == 'BREAKTHROUGH':
        writer.writerow(['Strategic Priority', 'HIGH'])
        writer.writerow(['Recommended Action', 'Immediate FTO analysis and partnership assessment'])
    elif innovation == 'INCREMENTAL':
        writer.writerow(['Strategic Priority', 'MEDIUM'])
        writer.writerow(['Recommended Action', 'Monitor market entry and track development'])
    else:
        writer.writerow(['Strategic Priority', 'LOW'])
        writer.writerow(['Recommended Action', 'Routine surveillance and tracking'])
    
    writer.writerow([])
    writer.writerow(['METADATA'])
    writer.writerow(['Analysis Date', datetime.now().strftime("%Y-%m-%d")])
    writer.writerow(['Analysis Time', datetime.now().strftime("%H:%M:%S")])
    writer.writerow(['Platform', 'Patent Research Platform'])
    writer.writerow(['AI Model', 'Claude (Anthropic)'])
    
    return output.getvalue()


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
    st.caption("Enter WO patent number for instant AI-powered analysis")
    st.caption("⚠️ **Note:** Direct analysis works best for WO patents from 2010 onwards. For other patent types (US, EP) or older patents, use 'Upload Document' tab.")
    
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
    
    # Check if we have cached results for this patent
    has_cached_results = False
    if patent_number and 'last_patent_data' in st.session_state and 'last_analysis' in st.session_state:
        if patent_number.upper() == st.session_state.last_patent_data.get('patent_id', '').upper():
            has_cached_results = True
    
    # Show cached results if available (prevents re-analysis on download button clicks)
    if has_cached_results and not analyze_button and not auto_analyze:
        display_results(st.session_state.last_patent_data, st.session_state.last_analysis)
    
    # Only run analysis if button clicked or auto-analyze triggered
    elif analyze_button or auto_analyze:
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
        
        # Store results in session state to persist across reruns (for export buttons)
        st.session_state.last_patent_data = patent_data
        st.session_state.last_analysis = analysis
        
        # Display results
        display_results(patent_data, analysis)

# =============================
# TAB 2: UPLOAD DOCUMENT
# =============================
with tab2:
    st.markdown("### Document Upload Analysis")
    st.caption("Upload patent XML file for comprehensive analysis - supports WO, US, EP, and all other patent types")

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
        
        # Check if we have cached results
        has_cached_results = 'last_patent_data' in st.session_state and 'last_analysis' in st.session_state
        
        # Show cached results if available (prevents re-analysis on download)
        if has_cached_results and not analyze_button:
            display_results(st.session_state.last_patent_data, st.session_state.last_analysis)
        
        # Only analyze if button clicked
        elif analyze_button:
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
            
            # Store in session state
            st.session_state.last_patent_data = patent_data
            st.session_state.last_analysis = analysis
            
            display_results(patent_data, analysis)
    else:
        st.info("👆 Upload a patent XML file to begin analysis")
        st.caption("Download XML files from [WIPO Patentscope](https://patentscope.wipo.int/)")

# Footer
st.markdown("---")
st.caption("🔬 Patent Research Platform | AI-Powered by Claude | Research & Competitive Intelligence")
