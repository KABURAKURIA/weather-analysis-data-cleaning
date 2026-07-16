import streamlit as st
import pandas as pd
import numpy as np
import warnings
from io import BytesIO

# Try importing reportlab for PDF generation, fall back gracefully if missing
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

warnings.filterwarnings('ignore')

# ==========================================
# 1. PREMIUM GLASSMORPHIC UI SETTINGS
# ==========================================
st.set_page_config(page_title="Smart Weather Cleaner", layout="wide", page_icon="🌩️")

def local_css():
    st.markdown("""
    <style>
    /* 1. Animated Atmospheric Gradient Background */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(-45deg, #1e3c72, #2a5298, #2980b9, #6dd5fa) !important;
        background-size: 400% 400% !important;
        animation: gradientBG 15s ease infinite !important;
        background-attachment: fixed !important;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Make Streamlit Header Transparent */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 2. Glassmorphic Containers (Sidebar, DataFrames, Uploaders) */
    [data-testid="stSidebar"], [data-testid="stFileUploaderDropzone"], [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
    }

    /* 3. Universal Text Readability */
    h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid="stMetricValue"], .stMarkdown {
        color: #ffffff !important;
        text-shadow: 0px 1px 3px rgba(0,0,0,0.4) !important;
    }

    /* Dropdown text fix (so options are readable when clicked) */
    ul[data-testid="stSelectboxVirtualDropdown"] li {
        color: #000000 !important;
        text-shadow: none !important;
    }

    /* 4. Beautiful Glowing Buttons */
    div.stButton > button, div.stDownloadButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease-in-out !important;
    }
    
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(109, 213, 250, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==========================================
# 2. DYNAMIC SAMPLE DATA GENERATOR
# ==========================================
def generate_messy_sample():
    """Creates a dataset with errors to demonstrate the cleaner's capability."""
    data = [
        ["Station ID", "BGM-01", "Info", "Ignore this row", "", "", "", "", "", "", ""],
        ["Year", "Month", "Date", "Rainfall", "Tmax", "Tmin", "Sun Hrs", "WindSpeed", "WindDir", "Hum 0900", "Hum 1500"],
        ["2023", "5", "1", "12.5", "30.1", "15.2", "6.5", "5.2", "NE", "85", "45"],
        ["2023", "5", "2", "tr", "29.5", "31.0", "x", "overflow", "N", "nan", "50"], # Tmin > Tmax, trace rain, text in numbers
        ["2023", "5", "3", "0", "28.0", "14.5", "8.0", "4.1", "E", "80", "40"],
        ["Some", "random", "junk", "text", "in", "the", "middle", "of", "file", "", ""],
        ["2023", "5", "5", "45.0", "110.0", "12.0", "2.0", "12.5", "SW", "95", "80"], # 110.0 Temp Max is a massive outlier
        ["2023", "5", "6", "nil", "27.5", "14.0", "7.5", "-", "W", "78", "missing"], # Dashes and 'missing' text
        ["2023", "5", "7", "5.0", "28.2", "15.0", "6.0", "4.5", "NW", "82", "42"],
    ]
    return pd.DataFrame(data)

# ==========================================
# PDF REPORT GENERATOR WITH REPORTLAB
# ==========================================
def generate_pdf_report(audit_log_df, summary_metrics):
    """Generates a structured, wrapped PDF report from the audit dataframe."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e3c72'),
        spaceAfter=10
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#444444'),
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=4
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    
    tb_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#222222')
    )

    story.append(Paragraph("Smart Weather Cleaner - Data Cleaning Report", title_style))
    story.append(Paragraph("Below is the record of structural corrections, value modifications, outlier removals, and data imputation steps.", subtitle_style))
    
    # Render structural row counts in the PDF
    story.append(Paragraph(f"<b>Dataset Row Summary:</b>", meta_style))
    story.append(Paragraph(f"• Total Rows in Raw Dataset: {summary_metrics['raw_rows']}", subtitle_style))
    story.append(Paragraph(f"• Total Rows in Cleaned Dataset: {summary_metrics['clean_rows']}", subtitle_style))
    story.append(Paragraph(f"• Total Rows Excluded/Removed: {summary_metrics['removed_rows']}", subtitle_style))
    story.append(Spacer(1, 10))

    headers = ["Row/Date", "Column", "Original Value", "Action Taken", "Reason why removed/changed"]
    table_data = [[Paragraph(h, th_style) for h in headers]]
    
    for _, row in audit_log_df.iterrows():
        row_cells = [
            Paragraph(str(row['Row/Date']), tb_style),
            Paragraph(str(row['Column']), tb_style),
            Paragraph(str(row['Original Value']), tb_style),
            Paragraph(str(row['Action']), tb_style),
            Paragraph(str(row['Reason']), tb_style)
        ]
        table_data.append(row_cells)

    # Calculate column widths to fit Letter size page width (540 pt available printable area)
    col_widths = [75, 75, 80, 100, 210]
    
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ])
    
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            t_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fbfd'))
            
    t.setStyle(t_style)
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# 3. THE SMART CLEANING ENGINE
# ==========================================
class SmartWeatherCleaner:
    def __init__(self, data_source, options=None):
        if isinstance(data_source, pd.DataFrame):
            self.raw_df = data_source
        elif data_source.name.endswith('.csv'):
            self.raw_df = pd.read_csv(data_source, header=None, low_memory=False)
        else:
            self.raw_df = pd.read_excel(data_source, header=None)
        
        self.options = options or {}
        self.raw_rows_count = len(self.raw_df)  # Track raw dataset row count
        self.cleaned_rows_count = 0
        self.rows_removed_count = 0
        self.structural_skipped_rows = []
        self.audit_log = []

    def smart_structural_parsing(self):
        parsed_data = []
        col_map = {}
        for row_idx, row in enumerate(self.raw_df.itertuples(index=False)):
            row_strs = [str(x).strip().lower() for x in row]
            
            # Auto-detect headers regardless of where they are located
            if 'year' in row_strs and ('date' in row_strs or 'month' in row_strs):
                col_map = {
                    'year': row_strs.index('year'),
                    'month': next((i for i, s in enumerate(row_strs) if 'month' in s), -1),
                    'day': next((i for i, s in enumerate(row_strs) if s in ['date', 'day']), -1),
                    'tmax': next((i for i, s in enumerate(row_strs) if 'max' in s), -1),
                    'tmin': next((i for i, s in enumerate(row_strs) if 'min' in s), -1),
                    'sun': next((i for i, s in enumerate(row_strs) if 'hrs' in s or 'sunshine' in s), -1),
                    'wind_speed': next((i for i, s in enumerate(row_strs) if 'windspeed' in s or 'windrun' in s), -1),
                    'wind_dir': next((i for i, s in enumerate(row_strs) if 'winddir' in s or 'windir' in s), -1),
                }
                rain_idx = next((i for i, s in enumerate(row_strs) if 'cms' in s or 'rainfall' in s), -1)
                if rain_idx == -1 and col_map['day'] != -1: rain_idx = col_map['day'] + 1
                col_map['rain'] = rain_idx

                hum9 = [i for i, s in enumerate(row_strs) if '0900' in s]
                hum15 = [i for i, s in enumerate(row_strs) if '1500' in s]
                col_map['hum9'] = hum9[0] if hum9 else -1
                col_map['hum15'] = hum15[-1] if hum15 else -1
                continue 
            
            if col_map.get('year', -1) != -1:
                try:
                    y_val = str(row[col_map['year']]).strip()
                    if not y_val.isdigit() or not (1900 <= int(y_val) <= 2100):
                        content_str = ", ".join([str(x) for x in row if pd.notna(x) and str(x) != ""])
                        self.structural_skipped_rows.append({
                            'Row': row_idx + 1,
                            'Content': content_str if content_str else "Empty Row",
                            'Reason': 'Failed date format or out-of-bounds year constraint'
                        })
                        continue 
                    def get_val(key):
                        idx = col_map.get(key, -1)
                        return row[idx] if (idx != -1 and idx < len(row)) else np.nan
                        
                    parsed_data.append({
                        'Year': y_val, 'Month': get_val('month'), 'Day': get_val('day'),
                        'Rainfall_mm': get_val('rain'), 'Temp_Max': get_val('tmax'), 'Temp_Min': get_val('tmin'),
                        'Sunshine_Hrs': get_val('sun'), 'Wind_Speed': get_val('wind_speed'),
                        'Wind_Dir': get_val('wind_dir'), 'Humidity_0900': get_val('hum9'), 'Humidity_1500': get_val('hum15')
                    })
                except Exception as e:
                    content_str = ", ".join([str(x) for x in row if pd.notna(x) and str(x) != ""])
                    self.structural_skipped_rows.append({
                        'Row': row_idx + 1,
                        'Content': content_str if content_str else "Corrupted Row",
                        'Reason': f'Exception during parsing: {str(e)}'
                    })
                    continue
        self.df = pd.DataFrame(parsed_data)

    def process_data(self):
        self.audit_log = []
        
        # 1. Log pre-parsed structural skipped rows
        for item in self.structural_skipped_rows:
            self.audit_log.append({
                'Row/Date': f"Row {item['Row']}",
                'Column': 'All Columns',
                'Original Value': item['Content'][:35] + "..." if len(item['Content']) > 35 else item['Content'],
                'Action': 'Row Removed',
                'Reason': item['Reason']
            })

        if self.df.empty:
            return

        # 2. Date Formatting & Validation
        valid_dates = []
        for idx, row in self.df.iterrows():
            y_val, m_val, d_val = row['Year'], row['Month'], row['Day']
            try:
                dt_str = f"{int(float(y_val))}-{int(float(m_val))}-{int(float(d_val))}"
                dt = pd.to_datetime(dt_str, errors='coerce')
                if pd.isna(dt):
                    self.audit_log.append({
                        'Row/Date': f"Y:{y_val} M:{m_val} D:{d_val}",
                        'Column': 'Date',
                        'Original Value': f"{y_val}-{m_val}-{d_val}",
                        'Action': 'Row Removed',
                        'Reason': 'Invalid or non-existent date structure'
                    })
                    valid_dates.append(pd.NaT)
                else:
                    valid_dates.append(dt)
            except Exception:
                self.audit_log.append({
                    'Row/Date': f"Y:{y_val} M:{m_val} D:{d_val}",
                    'Column': 'Date',
                    'Original Value': 'Incomplete Date Components',
                    'Action': 'Row Removed',
                    'Reason': 'Missing or non-numeric date parameters'
                })
                valid_dates.append(pd.NaT)
                
        self.df['Date'] = valid_dates
        self.df.dropna(subset=['Date'], inplace=True)
        self.df.set_index('Date', inplace=True)
        
        # Handle duplicates
        dup_mask = self.df.index.duplicated(keep='first')
        if dup_mask.any():
            dups = self.df[dup_mask]
            for dt, row in dups.iterrows():
                self.audit_log.append({
                    'Row/Date': str(dt.date()),
                    'Column': 'All Columns',
                    'Original Value': 'Duplicate Entry',
                    'Action': 'Row Removed',
                    'Reason': 'Duplicate date instance found in dataset'
                })
            self.df = self.df[~dup_mask]
            
        self.df.sort_index(inplace=True)
        self.df.drop(columns=['Year', 'Month', 'Day'], inplace=True, errors='ignore')

        # 3. Text Fixes & Standardizations
        self.df['Wind_Dir_Label'] = self.df['Wind_Dir'].astype(str).str.upper().str.strip()
        self.df.drop(columns=['Wind_Dir'], inplace=True, errors='ignore')

        for col in self.df.columns:
            if col == 'Wind_Dir_Label': continue
            
            # Temporary cast to object to allow string standardisation and floats coexisting
            self.df[col] = self.df[col].astype(object)
            
            for dt, val in self.df[col].items():
                if pd.isna(val):
                    continue
                val_str = str(val).strip().lower()
                
                # Check for replacements
                if val_str in ['tr', 't']:
                    self.df.at[dt, col] = 0.05
                    self.audit_log.append({
                        'Row/Date': str(dt.date()),
                        'Column': col,
                        'Original Value': val,
                        'Action': 'Value Standardized',
                        'Reason': 'Trace amount converted to 0.05'
                    })
                elif val_str in ['nil', 'none', 'false', 'missing']:
                    self.df.at[dt, col] = 0.0
                    self.audit_log.append({
                        'Row/Date': str(dt.date()),
                        'Column': col,
                        'Original Value': val,
                        'Action': 'Value Standardized',
                        'Reason': 'Null-equivalent phrase replaced with 0.0'
                    })
                elif val_str in ['x', '-', 'overflow', 'o/f', '#div/0!', '#ref!', 'm', '.', 'nan', '']:
                    self.df.at[dt, col] = np.nan
                    self.audit_log.append({
                        'Row/Date': str(dt.date()),
                        'Column': col,
                        'Original Value': val,
                        'Action': 'Value Removed',
                        'Reason': 'Invalid placeholder or text characters set to empty'
                    })
                else:
                    try:
                        self.df.at[dt, col] = float(val_str)
                    except ValueError:
                        self.df.at[dt, col] = np.nan
                        self.audit_log.append({
                            'Row/Date': str(dt.date()),
                            'Column': col,
                            'Original Value': val,
                            'Action': 'Value Removed',
                            'Reason': 'Could not parse unreadable text as numeric data'
                        })

            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # 4. Logical Corrections (e.g. Min Temp cannot be higher than Max Temp)
        if 'Temp_Min' in self.df.columns and 'Temp_Max' in self.df.columns:
            mask = self.df['Temp_Min'] > self.df['Temp_Max']
            for dt, row in self.df[mask].iterrows():
                self.audit_log.append({
                    'Row/Date': str(dt.date()),
                    'Column': 'Temp_Min & Temp_Max',
                    'Original Value': f"Min: {row['Temp_Min']} / Max: {row['Temp_Max']}",
                    'Action': 'Values Swapped',
                    'Reason': 'Logical conflict: Minimum temp was higher than Maximum temp'
                })
            self.df.loc[mask, ['Temp_Min', 'Temp_Max']] = self.df.loc[mask, ['Temp_Max', 'Temp_Min']].values
        
        # 5. Outlier Removal
        outlier_method = self.options.get('outlier_method', 'Smart Bounds (IQR)')
        if outlier_method == "Smart Bounds (IQR)":
            for col in self.df.select_dtypes(include=[np.number]).columns:
                Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
                
                outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]
                for dt, val in outliers[col].items():
                    if pd.notna(val):
                        self.audit_log.append({
                            'Row/Date': str(dt.date()),
                            'Column': col,
                            'Original Value': val,
                            'Action': 'Value Removed',
                            'Reason': f'Outlier detected (IQR bounds: {lower:.1f} to {upper:.1f})'
                        })
                self.df.loc[(self.df[col] < lower) | (self.df[col] > upper), col] = np.nan
                
        elif outlier_method == "Strict (Z-Score)":
            for col in self.df.select_dtypes(include=[np.number]).columns:
                mean, std = self.df[col].mean(), self.df[col].std()
                if pd.notna(std) and std != 0:
                    z_scores = (self.df[col] - mean) / std
                    outliers = self.df[z_scores.abs() > 3]
                    for dt, val in outliers[col].items():
                        if pd.notna(val):
                            self.audit_log.append({
                                'Row/Date': str(dt.date()),
                                'Column': col,
                                'Original Value': val,
                                'Action': 'Value Removed',
                                'Reason': f'Outlier detected (Z-Score: {z_scores.loc[dt]:.2f} exceeds threshold of 3)'
                            })
                    self.df.loc[z_scores.abs() > 3, col] = np.nan

        # 6. Fill Missing Values (Imputation tracking)
        pre_impute_df = self.df.copy()
        self.df = self.df.assign(Wind_Dir_Label=self.df['Wind_Dir_Label'].ffill().bfill())
        imputation_method = self.options.get('imputation_method', 'Smooth Time Interpolation')
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns

        if imputation_method == "Smooth Time Interpolation":
            self.df[numeric_cols] = self.df[numeric_cols].interpolate(method='time', limit_direction='both').ffill().bfill()
        elif imputation_method == "Carry Forward / Backward":
            self.df = self.df.ffill().bfill()
        elif imputation_method == "Average (Mean)":
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean()).ffill().bfill()
        elif imputation_method == "Set to Zero":
            self.df[numeric_cols] = self.df[numeric_cols].fillna(0)

        # Track imputed values
        for col in numeric_cols:
            missing_mask = pre_impute_df[col].isna() & self.df[col].notna()
            for dt, val in self.df[missing_mask][col].items():
                self.audit_log.append({
                    'Row/Date': str(dt.date()),
                    'Column': col,
                    'Original Value': 'NaN (Missing)',
                    'Action': 'Value Imputed',
                    'Reason': f'Value filled with {val:.2f} using {imputation_method}'
                })

    def execute(self):
        self.smart_structural_parsing()
        self.process_data()
        self.cleaned_rows_count = len(self.df)
        self.rows_removed_count = self.raw_rows_count - self.cleaned_rows_count
        return self.df

# ==========================================
# 4. APP UI & LOGIC
# ==========================================
st.title("🌩️ Smart Weather Data Cleaner")
st.markdown("Identify structural inconsistencies, clean values, filter anomalies, and record removals automatically.")

# Sidebar Settings
st.sidebar.header("⚙️ Cleaning Settings")
outlier_method = st.sidebar.selectbox("Outlier Handling", ["Smart Bounds (IQR)", "Strict (Z-Score)", "Do not remove outliers"])
imputation_method = st.sidebar.selectbox("Fix Missing Values", ["Smooth Time Interpolation", "Carry Forward / Backward", "Average (Mean)", "Set to Zero"])

cleaner_options = {
    'outlier_method': outlier_method,
    'imputation_method': imputation_method
}

# Layout: Split screen into Upload vs Example
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("📂 Drop your raw messy CSV or Excel file here", type=['csv', 'xlsx'])

with col2:
    st.write("")
    st.write("")
    st.markdown("### Or try it out first!")
    use_sample = st.button("🧪 Try with Messy Sample Data")

# Processing Logic
data_to_process = None

if use_sample:
    data_to_process = generate_messy_sample()
    st.info("Loaded a messy sample dataset with parsing issues, missing fields, and temperature anomalies.")
elif uploaded_file is not None:
    data_to_process = uploaded_file

if data_to_process is not None:
    with st.spinner("Processing structural parsing & cleaning rules..."):
        cleaner = SmartWeatherCleaner(data_to_process, options=cleaner_options)
        clean_df = cleaner.execute()
        
    st.success("✅ Data Processing Complete!")

    # Tabs for separation of Cleaned Data vs Removed Data / Audit Logs
    tab1, tab2 = st.tabs(["📊 Final Cleaned Dataset", "📋 Audit Log: Removals & Corrections"])

    with tab1:
        st.dataframe(clean_df.head(100), use_container_width=True)
        st.download_button(
            label="📥 Download Cleaned CSV", 
            data=clean_df.to_csv().encode('utf-8'), 
            file_name="Cleaned_Weather_Dataset.csv", 
            mime="text/csv"
        )

    with tab2:
        audit_log = getattr(cleaner, 'audit_log', [])
        if audit_log:
            # 1. Structural Metric Highlights
            st.markdown("### 📊 Dataset Volume Metrics")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Raw Dataset Rows", cleaner.raw_rows_count)
            m_col2.metric("Cleaned Dataset Rows", cleaner.cleaned_rows_count)
            m_col3.metric("Rows Excluded / Removed", cleaner.rows_removed_count)
            
            st.markdown("---")
            
            # 2. Detailed Audit Table
            st.markdown("### Record of Corrections and Removals")
            st.markdown("The following table details every piece of data that was changed, removed, or structure-filtered, along with the reasoning behind the action.")
            
            audit_df = pd.DataFrame(audit_log)
            st.dataframe(audit_df, use_container_width=True)
            
            # Pack summary parameters for the PDF report
            pdf_summary = {
                'raw_rows': cleaner.raw_rows_count,
                'clean_rows': cleaner.cleaned_rows_count,
                'removed_rows': cleaner.rows_removed_count
            }
            
            # Action Buttons: CSV Audit download & PDF Audit download
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.download_button(
                    label="📥 Download Audit Log as CSV",
                    data=audit_df.to_csv(index=False).encode('utf-8'),
                    file_name="Data_Cleaning_Audit_Log.csv",
                    mime="text/csv"
                )
            with col_b2:
                if REPORTLAB_AVAILABLE:
                    try:
                        pdf_data = generate_pdf_report(audit_df, pdf_summary)
                        st.download_button(
                            label="📄 Download Audit Log as PDF",
                            data=pdf_data,
                            file_name="Data_Cleaning_Audit_Report.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Could not generate PDF: {str(e)}")
                else:
                    st.warning("To enable PDF reports, please ensure `reportlab` is installed in your python environment.")
        else:
            st.info("No modifications, corrections, or structural removals were needed. The source structure matches requirements.")
