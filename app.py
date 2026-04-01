import streamlit as st
import pandas as pd
import numpy as np
import warnings

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
    """Creates a chaotic, broken dataset to demonstrate the cleaner's power."""
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
# 3. THE SMART CLEANING ENGINE
# ==========================================
class SmartWeatherCleaner:
    def __init__(self, data_source, options=None):
        # Support both uploaded files and raw DataFrames (for the examples)
        if isinstance(data_source, pd.DataFrame):
            self.raw_df = data_source
        elif data_source.name.endswith('.csv'):
            self.raw_df = pd.read_csv(data_source, header=None, low_memory=False)
        else:
            self.raw_df = pd.read_excel(data_source, header=None)
        self.options = options or {}

    def smart_structural_parsing(self):
        parsed_data =[]
        col_map = {}
        for row in self.raw_df.itertuples(index=False):
            row_strs =[str(x).strip().lower() for x in row]
            
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

                hum9 =[i for i, s in enumerate(row_strs) if '0900' in s]
                hum15 =[i for i, s in enumerate(row_strs) if '1500' in s]
                col_map['hum9'] = hum9[0] if hum9 else -1
                col_map['hum15'] = hum15[-1] if hum15 else -1
                continue 
            
            if col_map.get('year', -1) != -1:
                try:
                    y_val = str(row[col_map['year']]).strip()
                    if not y_val.isdigit() or not (1900 <= int(y_val) <= 2100): continue 
                    def get_val(key):
                        idx = col_map.get(key, -1)
                        return row[idx] if (idx != -1 and idx < len(row)) else np.nan
                        
                    parsed_data.append({
                        'Year': y_val, 'Month': get_val('month'), 'Day': get_val('day'),
                        'Rainfall_mm': get_val('rain'), 'Temp_Max': get_val('tmax'), 'Temp_Min': get_val('tmin'),
                        'Sunshine_Hrs': get_val('sun'), 'Wind_Speed': get_val('wind_speed'),
                        'Wind_Dir': get_val('wind_dir'), 'Humidity_0900': get_val('hum9'), 'Humidity_1500': get_val('hum15')
                    })
                except Exception:
                    continue
        self.df = pd.DataFrame(parsed_data)

    def process_data(self):
        # 1. Text Fixes & Type Conversion
        self.df['Wind_Dir_Label'] = self.df['Wind_Dir'].astype(str).str.upper().str.strip()
        self.df.drop(columns=['Wind_Dir'], inplace=True)

        for col in self.df.columns:
            if col == 'Wind_Dir_Label': continue
            self.df[col] = self.df[col].astype(str).str.strip().str.lower()
            replace_map = {r'^(tr|t)$': 0.05, r'^(nil|none|false|missing)$': 0.0, r'^(x+|\-|overflow|o/f|#div/0!|#ref!|m|\.)$': np.nan, r'^\s*$': np.nan, r'^nan$': np.nan}
            self.df[col] = self.df[col].replace(replace_map, regex=True)
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # 2. Date Formatting
        self.df.dropna(subset=['Year', 'Month', 'Day'], inplace=True)
        dt_strings = self.df['Year'].astype(int).astype(str) + '-' + self.df['Month'].astype(int).astype(str) + '-' + self.df['Day'].astype(int).astype(str)
        self.df['Date'] = pd.to_datetime(dt_strings, errors='coerce')
        self.df.dropna(subset=['Date'], inplace=True)
        self.df.drop(columns=['Year', 'Month', 'Day'], inplace=True)
        self.df.set_index('Date', inplace=True)
        self.df = self.df[~self.df.index.duplicated(keep='first')].sort_index()

        # 3. Logical Corrections (e.g. Min Temp cannot be higher than Max Temp)
        mask = self.df['Temp_Min'] > self.df['Temp_Max']
        self.df.loc[mask, ['Temp_Min', 'Temp_Max']] = self.df.loc[mask, ['Temp_Max', 'Temp_Min']].values
        
        # 4. Outlier Removal
        outlier_method = self.options.get('outlier_method', 'Smart Bounds (IQR)')
        if outlier_method == "Smart Bounds (IQR)":
            for col in self.df.select_dtypes(include=[np.number]).columns:
                Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
                self.df.loc[(self.df[col] < lower) | (self.df[col] > upper), col] = np.nan
        elif outlier_method == "Strict (Z-Score)":
            for col in self.df.select_dtypes(include=[np.number]).columns:
                mean, std = self.df[col].mean(), self.df[col].std()
                if pd.notna(std) and std != 0:
                    z_scores = (self.df[col] - mean) / std
                    self.df.loc[z_scores.abs() > 3, col] = np.nan

        # 5. Fill Missing Values
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

    def execute(self):
        self.smart_structural_parsing()
        self.process_data()
        return self.df

# ==========================================
# 4. APP UI & LOGIC
# ==========================================
st.title("🌩️ Smart Weather Data Cleaner")
st.markdown("Easily fix messy weather datasets, fill missing values, and remove errors with one click.")

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
    st.info("Loaded a highly chaotic sample dataset with text errors, missing values, and massive outliers.")
elif uploaded_file is not None:
    data_to_process = uploaded_file

if data_to_process is not None:
    with st.spinner("Parsing messy structures & repairing data..."):
        cleaner = SmartWeatherCleaner(data_to_process, options=cleaner_options)
        clean_df = cleaner.execute()
        
    st.success("✅ Data Cleaned and Standardized Successfully!")

    st.markdown("### 🔹 Final Cleaned Dataset")
    st.dataframe(clean_df.head(50), use_container_width=True)
    
    st.download_button(
        label="📥 Download Clean CSV", 
        data=clean_df.to_csv().encode('utf-8'), 
        file_name="Cleaned_Weather_Ready.csv", 
        mime="text/csv"
    )
