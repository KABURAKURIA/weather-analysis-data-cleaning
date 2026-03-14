import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# ==========================================
# 1. GLASSMORPHIC UI SETTINGS
# ==========================================
st.set_page_config(page_title="Ultimate Weather Cleaner", layout="wide")

def local_css():
    st.markdown("""
    <style>
    /* Glassmorphic Background */
    .stApp {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    /* Glassmorphic Containers */
    .css-1r6slb0, .css-18e3th9, .css-1d391kg {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    /* Text Colors */
    h1, h2, h3, p, label, .st-emotion-cache-10trblm {
        color: white !important;
    }
    
    /* DataFrame styling */
    [data-testid="stDataFrame"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
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
            row_strs = [str(x).strip().lower() for x in row]
            
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

        # 3. RSD Constraints (FR-09)
        mask = self.df['Temp_Min'] > self.df['Temp_Max']
        self.df.loc[mask, ['Temp_Min', 'Temp_Max']] = self.df.loc[mask, ['Temp_Max', 'Temp_Min']].values
        
        # 4. Outliers via IQR
        for col in self.df.select_dtypes(include=[np.number]).columns:
            Q1, Q3 = self.df[col].quantile(0.25), self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
            self.df.loc[(self.df[col] < lower) | (self.df[col] > upper), col] = np.nan

        # 5. Missing Value Imputation (FR-08)
        self.df = self.df.assign(Wind_Dir_Label=self.df['Wind_Dir_Label'].ffill().bfill())
        self.df = self.df.interpolate(method='time', limit_direction='both').ffill().bfill()

        # 6. Feature Engineering (Cyclical Encoding)
        dir_map = {'N':0, 'NE':45, 'E':90, 'SE':135, 'S':180, 'SW':225, 'W':270, 'NW':315}
        wind_deg = self.df['Wind_Dir_Label'].map(dir_map).fillna(0)
        self.df['Wind_Dir_Sin'] = np.sin(2 * np.pi * wind_deg / 360)
        self.df['Wind_Dir_Cos'] = np.cos(2 * np.pi * wind_deg / 360)
        self.df['Month_Sin'] = np.sin(2 * np.pi * self.df.index.month / 12)

        # 7. Normalization (FR-10)
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
# 3. STREAMLIT APP LAYOUT & LOGIC
# ==========================================
st.title("🌩️ Integrative ML & IoT Weather Data Cleaner")
st.markdown("Developed for Western Region of Kenya (RSD Compliant)")

uploaded_file = st.file_uploader("Upload Messy Weather CSV/Excel", type=['csv', 'xlsx'])

if uploaded_file is not None:
    with st.spinner("Executing Smart Structural Parsing & Pipeline..."):
        cleaner = UltimateWeatherCleaner(uploaded_file)
        clean_df, norm_df = cleaner.execute()
    st.success("✅ Data Cleaned, Engineered, and Normalized Successfully!")

    tab1, tab2 = st.tabs(["🗄️ Cleaned Datasets", "📈 15 Weather Analytics & Graphs"])

    with tab1:
        st.subheader("Standard Cleaned Data")
        st.dataframe(clean_df.head(100))
        st.download_button("Download Clean CSV", data=clean_df.to_csv().encode('utf-8'), file_name="Cleaned_Weather.csv", mime="text/csv")
        
        st.subheader("ML Normalized Data[0,1] (FR-10)")
        st.dataframe(norm_df.head(100))
        st.download_button("Download Normalized CSV", data=norm_df.to_csv().encode('utf-8'), file_name="Normalized_Weather.csv", mime="text/csv")

    with tab2:
        st.markdown("### Meteorological Data Quality & Insights")
        
        # --- 5 CALCULATION METRICS ---
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("1. Clean Records", f"{len(clean_df):,}")
        col2.metric("2. Imputation Rate", "100%")
        col3.metric("3. Max Temp Peak", f"{clean_df['Temp_Max'].max():.1f} °C")
        col4.metric("4. Min Temp Base", f"{clean_df['Temp_Min'].min():.1f} °C")
        col5.metric("5. Total Rainfall", f"{clean_df['Rainfall_mm'].sum():,.0f} mm")
        
        # Transparency layout config for Plotly
        layout_transparent = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))

        st.divider()

        c1, c2 = st.columns(2)
        
        # 6. Time Series - Temperature
        with c1:
            st.markdown("##### 6. Temp Max & Min Trends")
            fig_temp = px.line(clean_df, y=['Temp_Max', 'Temp_Min'], color_discrete_sequence=['#ff4b4b', '#00d4ff'])
            fig_temp.update_layout(**layout_transparent)
            st.plotly_chart(fig_temp, use_container_width=True)

        # 7. Rainfall Distribution
        with c2:
            st.markdown("##### 7. Daily Rainfall Distribution")
            fig_rain = px.histogram(clean_df[clean_df['Rainfall_mm']>0], x="Rainfall_mm", nbins=40, color_discrete_sequence=['#00d4ff'])
            fig_rain.update_layout(**layout_transparent)
            st.plotly_chart(fig_rain, use_container_width=True)

        c3, c4 = st.columns(2)
        
        # 8. Correlation Heatmap (FR-12 Feature Selection Context)
        with c3:
            st.markdown("##### 8. Feature Correlation Matrix")
            corr = clean_df.select_dtypes(include=[np.number]).corr()
            fig_corr = px.imshow(corr, color_continuous_scale='RdBu_r')
            fig_corr.update_layout(**layout_transparent)
            st.plotly_chart(fig_corr, use_container_width=True)

        # 9. Wind Direction Frequencies (Fixed Bug)
        with c4:
            st.markdown("##### 9. Prevailing Wind Directions")
            if 'Wind_Dir_Label' in clean_df.columns:
                wind_counts = clean_df['Wind_Dir_Label'].value_counts()
                fig_wind = px.bar(x=wind_counts.index, y=wind_counts.values, color_discrete_sequence=['#a29bfe'])
            else:
                fig_wind = px.bar(title="Data Unavailable")
            fig_wind.update_layout(**layout_transparent)
            st.plotly_chart(fig_wind, use_container_width=True)
            
        c5, c6 = st.columns(2)
        
        # 10. Outlier Detection Boxplots
        with c5:
            st.markdown("##### 10. Sensor Data Dispersion (Outlier Bounds)")
            fig_box = px.box(clean_df, y=['Temp_Max', 'Temp_Min', 'Humidity_0900'], points="all")
            fig_box.update_layout(**layout_transparent)
            st.plotly_chart(fig_box, use_container_width=True)

        # 11. Sunshine vs Temperature Scatter
        with c6:
            st.markdown("##### 11. Sunshine Hrs vs Temp Max")
            fig_scat = px.scatter(clean_df, x="Sunshine_Hrs", y="Temp_Max", opacity=0.5, color="Humidity_1500")
            fig_scat.update_layout(**layout_transparent)
            st.plotly_chart(fig_scat, use_container_width=True)

        c7, c8 = st.columns(2)
        
        # 12. Monthly Average Temperatures
        with c7:
            st.markdown("##### 12. Avg Monthly Temps")
            monthly_temp = clean_df.groupby(clean_df.index.month)['Temp_Max'].mean()
            fig_m_temp = px.bar(x=monthly_temp.index, y=monthly_temp.values, labels={'x':'Month', 'y':'Avg Temp Max'})
            fig_m_temp.update_layout(**layout_transparent)
            st.plotly_chart(fig_m_temp, use_container_width=True)

        # 13. Humidity Fluctuations
        with c8:
            st.markdown("##### 13. Humidity (0900 vs 1500)")
            fig_hum = px.line(clean_df, y=['Humidity_0900', 'Humidity_1500'])
            fig_hum.update_layout(**layout_transparent)
            st.plotly_chart(fig_hum, use_container_width=True)
            
        c9, c10 = st.columns(2)
        
        # 14. Yearly Cumulative Rainfall
        with c9:
            st.markdown("##### 14. Yearly Cumulative Rainfall")
            yearly_rain = clean_df.groupby(clean_df.index.year)['Rainfall_mm'].sum()
            fig_y_rain = px.bar(x=yearly_rain.index, y=yearly_rain.values, labels={'x':'Year', 'y':'Total Rain (mm)'})
            fig_y_rain.update_layout(**layout_transparent)
            st.plotly_chart(fig_y_rain, use_container_width=True)

        # 15. Wind Speed Trend
        with c10:
            st.markdown("##### 15. Wind Speed Tracking")
            fig_wind_ts = px.area(clean_df, y='Wind_Speed', color_discrete_sequence=['#55efc4'])
            fig_wind_ts.update_layout(**layout_transparent)
            st.plotly_chart(fig_wind_ts, use_container_width=True)
