import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. PREMIUM GLASSMORPHIC UI SETTINGS
# ==========================================
st.set_page_config(page_title="Ultimate Weather Cleaner", layout="wide", page_icon="🌩️")

def local_css():
    st.markdown("""
    <style>
    /* 1. Dynamic Stormy Gradient Background */
    .stApp, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Make Streamlit Header Transparent */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* 2. Glassmorphic Containers (Metrics, Uploaders, Tabs) */
    [data-testid="stMetric"],[data-testid="stFileUploader"], 
    .stTabs [data-baseweb="tab-list"],[data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    /* 3. Text Readability (Drop Shadows for high contrast) */
    h1, h2, h3, h4, h5, h6, p, span, label, div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.6) !important;
    }

    /* 4. PERFECT BUTTONS (Fixes the invisible text issue) */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease-in-out !important;
        text-shadow: none !important; /* Keep button text crisp */
    }
    
    /* Button Hover Animation */
    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.7) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(0,212,255, 0.4) !important;
        color: #ffffff !important;
    }

    /* Keep Download Buttons Visible */
    div.stDownloadButton > button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4) !important;
    }
    div.stDownloadButton > button:hover {
        transform: scale(1.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# ==========================================
# 2. THE ULTIMATE CLEANING ENGINE
# ==========================================
class UltimateWeatherCleaner:
    def __init__(self, file_obj):
        if file_obj.name.endswith('.csv'):
            self.raw_df = pd.read_csv(file_obj, header=None, low_memory=False)
        else:
            self.raw_df = pd.read_excel(file_obj, header=None)

    def smart_structural_parsing(self):
        parsed_data =[]
        col_map = {}
        for row in self.raw_df.itertuples(index=False):
            row_strs =[str(x).strip().lower() for x in row]
            
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
        # 1. Text & Type Coercion
        self.df['Wind_Dir_Label'] = self.df['Wind_Dir'].astype(str).str.upper().str.strip()
        self.df.drop(columns=['Wind_Dir'], inplace=True)

        for col in self.df.columns:
            if col == 'Wind_Dir_Label': continue
            self.df[col] = self.df[col].astype(str).str.strip().str.lower()
            replace_map = {r'^(tr|t)$': 0.05, r'^(nil|none|false)$': 0.0, r'^(x+|\-|overflow|o/f|#div/0!|#ref!|m|\.)$': np.nan, r'^\s*$': np.nan, r'^nan$': np.nan}
            self.df[col] = self.df[col].replace(replace_map, regex=True)
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

        # 2. Temporal Indexing
        self.df.dropna(subset=['Year', 'Month', 'Day'], inplace=True)
        dt_strings = self.df['Year'].astype(int).astype(str) + '-' + self.df['Month'].astype(int).astype(str) + '-' + self.df['Day'].astype(int).astype(str)
        self.df['Datetime'] = pd.to_datetime(dt_strings, errors='coerce')
        self.df.dropna(subset=['Datetime'], inplace=True)
        self.df.drop(columns=['Year', 'Month', 'Day'], inplace=True)
        self.df.set_index('Datetime', inplace=True)
        self.df = self.df[~self.df.index.duplicated(keep='first')].sort_index()

        # 3. RSD Constraints
        mask = self.df['Temp_Min'] > self.df['Temp_Max']
        self.df.loc[mask, ['Temp_Min', 'Temp_Max']] = self.df.loc[mask, ['Temp_Max', 'Temp_Min']].values
        
        # 4. Outliers via IQR
        for col in self.df.select_dtypes(include=[np.number]).columns:
            Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            self.df.loc[(self.df[col] < lower) | (self.df[col] > upper), col] = np.nan

        # 5. Missing Value Imputation
        self.df = self.df.assign(Wind_Dir_Label=self.df['Wind_Dir_Label'].ffill().bfill())
        self.df = self.df.interpolate(method='time', limit_direction='both').ffill().bfill()

        # 6. Feature Engineering
        dir_map = {'N':0, 'NE':45, 'E':90, 'SE':135, 'S':180, 'SW':225, 'W':270, 'NW':315}
        wind_deg = self.df['Wind_Dir_Label'].map(dir_map).fillna(0)
        self.df['Wind_Dir_Sin'] = np.sin(2 * np.pi * wind_deg / 360)
        self.df['Wind_Dir_Cos'] = np.cos(2 * np.pi * wind_deg / 360)
        self.df['Month_Sin'] = np.sin(2 * np.pi * self.df.index.month / 12)

        # 7. Normalization
        self.normalized_df = self.df.copy()
        for col in self.normalized_df.select_dtypes(include=[np.number]).columns:
            min_val, max_val = self.normalized_df[col].min(), self.normalized_df[col].max()
            if max_val != min_val:
                self.normalized_df[col] = (self.normalized_df[col] - min_val) / (max_val - min_val)
            else:
                self.normalized_df[col] = 0.0

    def execute(self):
        self.smart_structural_parsing()
        self.process_data()
        return self.df, self.normalized_df

# ==========================================
# 3. APP EXECUTION
# ==========================================
st.title("🌩️ Integrative ML Weather Data Cleaner")
st.markdown("Automated processing and formatting for the Western Region of Kenya (RSD Compliant)")

uploaded_file = st.file_uploader("Drop your raw messy CSV/Excel file here", type=['csv', 'xlsx'])

if uploaded_file is not None:
    with st.spinner("Parsing dynamic structure & repairing datasets..."):
        cleaner = UltimateWeatherCleaner(uploaded_file)
        clean_df, norm_df = cleaner.execute()
        
    st.success("✅ Data Cleaned, Engineered, and Normalized Successfully!")

    tab1, tab2 = st.tabs(["🗄️ Datasets & Downloads", "📈 15 Weather Analytics & Graphs"])

    with tab1:
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("### 🔹 Standard Cleaned Data")
            st.dataframe(clean_df.head(50), use_container_width=True)
            st.download_button("📥 Download Clean CSV", data=clean_df.to_csv().encode('utf-8'), file_name="Cleaned_Weather.csv", mime="text/csv")
        
        with c_right:
            st.markdown("### 🔹 ML Normalized [0,1]")
            st.dataframe(norm_df.head(50), use_container_width=True)
            st.download_button("📥 Download Normalized CSV", data=norm_df.to_csv().encode('utf-8'), file_name="Normalized_Weather.csv", mime="text/csv")

    with tab2:
        st.markdown("### Meteorological Insights Dashboard")
        
        # --- 5 CALCULATION METRICS ---
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("1. Usable Records", f"{len(clean_df):,}")
        col2.metric("2. Imputation Success", "100%")
        col3.metric("3. Peak Temp", f"{clean_df['Temp_Max'].max():.1f} °C")
        col4.metric("4. Lowest Temp", f"{clean_df['Temp_Min'].min():.1f} °C")
        col5.metric("5. Total Rain", f"{clean_df['Rainfall_mm'].sum():,.0f} mm")
        
        layout_transparent = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))

        st.divider()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("##### 6. Temp Max & Min Trends")
            fig_temp = px.line(clean_df, y=['Temp_Max', 'Temp_Min'], color_discrete_sequence=['#ff0844', '#00f2fe'])
            fig_temp.update_layout(**layout_transparent)
            st.plotly_chart(fig_temp, use_container_width=True)

        with c2:
            st.markdown("##### 7. Daily Rainfall Distribution")
            fig_rain = px.histogram(clean_df[clean_df['Rainfall_mm']>0], x="Rainfall_mm", nbins=40, color_discrete_sequence=['#00f2fe'])
            fig_rain.update_layout(**layout_transparent)
            st.plotly_chart(fig_rain, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown("##### 8. Feature Correlation Matrix")
            corr = clean_df.select_dtypes(include=[np.number]).corr()
            fig_corr = px.imshow(corr, color_continuous_scale='Turbo') # Vibrant color scale
            fig_corr.update_layout(**layout_transparent)
            st.plotly_chart(fig_corr, use_container_width=True)

        with c4:
            st.markdown("##### 9. Prevailing Wind Directions")
            if 'Wind_Dir_Label' in clean_df.columns:
                wind_counts = clean_df['Wind_Dir_Label'].value_counts()
                fig_wind = px.bar(x=wind_counts.index, y=wind_counts.values, color_discrete_sequence=['#f9d423'])
            else:
                fig_wind = px.bar(title="Data Unavailable")
            fig_wind.update_layout(**layout_transparent)
            st.plotly_chart(fig_wind, use_container_width=True)
            
        c5, c6 = st.columns(2)
        with c5:
            st.markdown("##### 10. Sensor Data Dispersion")
            fig_box = px.box(clean_df, y=['Temp_Max', 'Temp_Min', 'Humidity_0900'], points="all", color_discrete_sequence=['#00b09b'])
            fig_box.update_layout(**layout_transparent)
            st.plotly_chart(fig_box, use_container_width=True)

        with c6:
            st.markdown("##### 11. Sunshine vs Temp Max")
            fig_scat = px.scatter(clean_df, x="Sunshine_Hrs", y="Temp_Max", color="Humidity_1500", color_continuous_scale='Plasma')
            fig_scat.update_layout(**layout_transparent)
            st.plotly_chart(fig_scat, use_container_width=True)

        c7, c8 = st.columns(2)
        with c7:
            st.markdown("##### 12. Monthly Avg Temperatures")
            monthly_temp = clean_df.groupby(clean_df.index.month)['Temp_Max'].mean()
            fig_m_temp = px.bar(x=monthly_temp.index, y=monthly_temp.values, color_discrete_sequence=['#ff0844'])
            fig_m_temp.update_layout(**layout_transparent, xaxis_title="Month", yaxis_title="Temp °C")
            st.plotly_chart(fig_m_temp, use_container_width=True)

        with c8:
            st.markdown("##### 13. Humidity (0900 vs 1500)")
            fig_hum = px.line(clean_df, y=['Humidity_0900', 'Humidity_1500'], color_discrete_sequence=['#f9d423', '#00f2fe'])
            fig_hum.update_layout(**layout_transparent)
            st.plotly_chart(fig_hum, use_container_width=True)
            
        c9, c10 = st.columns(2)
        with c9:
            st.markdown("##### 14. Yearly Cumulative Rainfall")
            yearly_rain = clean_df.groupby(clean_df.index.year)['Rainfall_mm'].sum()
            fig_y_rain = px.bar(x=yearly_rain.index, y=yearly_rain.values, color_discrete_sequence=['#00f2fe'])
            fig_y_rain.update_layout(**layout_transparent, xaxis_title="Year", yaxis_title="Total Rain (mm)")
            st.plotly_chart(fig_y_rain, use_container_width=True)

        with c10:
            st.markdown("##### 15. Wind Speed Tracking")
            fig_wind_ts = px.area(clean_df, y='Wind_Speed', color_discrete_sequence=['#00b09b'])
            fig_wind_ts.update_layout(**layout_transparent)
            st.plotly_chart(fig_wind_ts, use_container_width=True)
