# Proyek Analisis Data E-Commerce Public Dataset

Proyek ini merupakan analisis komprehensif dari *Olist Brazilian E-Commerce Dataset*. Analisis mencakup data wrangling, exploratory data analysis, visualisasi dengan folium dan matplotlib, hingga analisis lanjutan menggunakan *RFM (Recency, Frequency, Monetary)* dan *Clustering/Binning*.

## Setup Environment - Anaconda
```bash
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```bash
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App
Untuk menjalankan dashboard di lokal, pastikan berada di root directory dari proyek, lalu jalankan perintah berikut:
```bash
cd dashboard
streamlit run dashboard.py
```
> **Catatan**: Pastikan file `main_data.csv` sudah tersedia di dalam folder `dashboard`.
