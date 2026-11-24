# 🌩️ Smart Weather Analytics & Data Cleaning Platform

[![Streamlit](https://img.shields.io/badge/Streamlit-Glassmorphic%20UI-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Analytics](https://img.shields.io/badge/Field-Meteorological%20Analytics-blue.svg)](https://github.com/KABURAKURIA/weather-analysis-data-cleaning)

A modern meteorological data analytics, telemetry cleaning, and automated anomaly detection platform featuring an interactive animated glassmorphic Streamlit web interface and automated executive PDF reporting.

---

## ☀️ Features & Analytical Capabilities

- **Sensor Telemetry Cleaning**: Automated cleaning of temperature, humidity, atmospheric pressure, wind speed, and precipitation logs.
- **Statistical Anomaly Detection**: Z-score and IQR-based filtering for weather sensor transmission spikes and hardware dropout.
- **Temporal Alignment**: Resampling, time-gap interpolation, and timestamp harmonization across multi-station sensor networks.
- **Glassmorphic Interactive UI**: Dynamic weather-inspired animated gradient UI designed for executive presentation and monitoring.
- **Automated PDF Export**: Full PDF audit reports via ReportLab detailing statistical summaries, missingness indices, and cleaned datasets.

---

## 📊 Telemetry Cleaning Rules

| Meteorological Metric | Physiological/Physical Boundaries | Remediation Method |
| :--- | :--- | :--- |
| **Temperature (°C)** | -60°C to +60°C | Physical boundary clamping & median imputation |
| **Relative Humidity (%)** | 0% to 100% | Saturation boundary clipping |
| **Barometric Pressure (hPa)** | 870 hPa to 1085 hPa | Rolling average spline interpolation |
| **Wind Speed (m/s)** | 0 m/s to 120 m/s | Non-negative constraint enforcement & spike filter |
| **Precipitation (mm)** | ≥ 0 mm | Zero-floor clipping & sensor noise filtering |

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/KABURAKURIA/weather-analysis-data-cleaning.git
cd weather-analysis-data-cleaning

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py
```

---

## 🛠️ Stack

- **Language**: Python 3.9+
- **Data Analytics**: Pandas, NumPy
- **Reporting**: ReportLab
- **UI Framework**: Streamlit (Glassmorphic CSS3 styling)

---

## 📄 License

MIT License.
