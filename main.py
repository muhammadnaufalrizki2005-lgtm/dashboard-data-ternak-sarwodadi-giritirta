import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Konfigurasi Halaman (Minimalist & Clean)
st.set_page_config(page_title="Dashboard Pendataan Ternak", layout="wide")

# Fungsi Load & Clean Data (Otomatisasi Pembersihan Data)
@st.cache_data
def load_data():
    # 1. Membaca data (Bisa dari Excel maupun CSV)
    try:
        df = pd.read_excel('Data Ternak Sarwodadi, Giritirta.xlsx', sheet_name='SARWODADI', header=1)
    except:
        df = pd.read_csv('Data Ternak Sarwodadi, Giritirta.xlsx - SARWODADI.csv', header=1)
    
    # 2. Mengambil 10 kolom pertama dan merapikan namanya
    df_s = df.iloc[:, 0:10].copy()
    df_s.columns = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah Dewasa', 'Total', 'Ketersediaan', 'Anakan']
    
    # 3. FORWARD FILL: Menyalin Nama, RT, RW, Jenis Ternak ke baris di bawahnya yang kosong
    kolom_identitas = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak']
    df_s[kolom_identitas] = df_s[kolom_identitas].ffill()
    
    # 4. MISSING VALUES: Mengisi kolom jumlah yang kosong dengan angka 0
    df_s['Jumlah Dewasa'] = pd.to_numeric(df_s['Jumlah Dewasa'], errors='coerce').fillna(0)
    df_s['Anakan'] = pd.to_numeric(df_s['Anakan'], errors='coerce').fillna(0)
    df_s['Total'] = pd.to_numeric(df_s['Total'], errors='coerce').fillna(0)
    
    # 5. KETERSEDIAAN: Mengisi persetujuan yang kosong
    df_s['Ketersediaan'] = df_s['Ketersediaan'].fillna('Belum Konfirmasi')
    
    # 6. GABUNG ALAMAT: Memformat angka RT/RW menjadi teks (misal: "RT 01 / RW 01")
    df_s['Alamat'] = "RT 0" + df_s['RT'].astype(str).str.replace('.0', '', regex=False) + " / RW 0" + df_s['RW'].astype(str).str.replace('.0', '', regex=False)
    
    # 7. FILTERING: Membuang baris yang benar-benar tidak ada data (baris pemisah)
    df_s = df_s[df_s['Jenis kelamin'].notna() | (df_s['Jumlah Dewasa'] > 0) | (df_s['Anakan'] > 0)]
    
    return df_s

data_peternak = load_data()

# Palet warna Earth Tone (Estetika Minimalis)
earth_tones = ['#8D6E63', '#D7CCC8', '#A1887F', '#5D4037', '#BCAAA4']

# Sidebar Navigasi
with st.sidebar:
    menu = option_menu(
        "📌 Menu Navigasi",
        ["📖 Profil Wilayah", "📊 Dashboard Ternak", "📋 Rekapitulasi Total"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#5D4037", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#8D6E63"},
        }
    )

# ================= HALAMAN 1: PROFIL =================
if menu == "📖 Profil Wilayah":
    st.markdown("## 📖 Profil Desa Sarwodadi & Giritirta")
    st.write("---")
    
    st.markdown("""
    **Desa Sarwodadi dan Desa Giritirta** merupakan wilayah yang terletak di **Kecamatan Pejawaran, Kabupaten Banjarnegara**. 
    Berada di kawasan pegunungan utara Banjarnegara yang sejuk, wilayah ini dikaruniai kondisi alam yang sangat mendukung untuk sektor pertanian dan peternakan. 
    
    ### 👥 Potensi Peternakan Warga
    Berdasarkan data yang dihimpun, komoditas ternak yang paling banyak dibudidayakan oleh warga meliputi:
    * **Kambing**
    * **Domba**
    * **Sapi**
    """)

    st.markdown("### 🗺️ Peta Kecamatan Pejawaran")
    pejawaran_coords = [-7.2435, 109.8450]
    m = folium.Map(location=pejawaran_coords, zoom_start=12)
    folium.Marker(
        location=pejawaran_coords, popup="Kecamatan Pejawaran", tooltip="Lokasi", icon=folium.Icon(color="darkgreen", icon="leaf")
    ).add_to(m)
    st_folium(m, width=700, height=400)


# ================= HALAMAN 2: DASHBOARD =================
elif menu == "📊 Dashboard Ternak":
    st.title("📊 Dashboard Pendataan Peternak Warga")
    st.write("---")

    # Sidebar Filter
    st.sidebar.header("🔎 Filter Data")
    alamat_list = sorted(data_peternak["Alamat"].dropna().unique())
    selected_alamat = st.sidebar.multiselect("Pilih Wilayah", options=alamat_list, default=alamat_list)
    
    filtered_data = data_peternak[data_peternak["Alamat"].isin(selected_alamat)]

    # Metrik Utama (Menghitung Total Ternak = Dewasa + Anakan)
    total_populasi = filtered_data['Jumlah Dewasa'].sum() + filtered_data['Anakan'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Populasi Ternak Keseluruhan", value=f"{int(total_populasi)} Ekor")
    with col2:
        st.metric(label="Total Peternak", value=f"{filtered_data['Nama Pemilik'].nunique()} Orang")
    with col3:
        st.metric(label="Jenis Ternak Terbanyak", value=filtered_data.groupby('Jenis Ternak')['Jumlah Dewasa'].sum().idxmax())

    st.write("---")

    # Bar chart (Jantan vs Betina)
    st.subheader("📊 Distribusi Ternak Dewasa Berdasarkan Jenis Kelamin")
    # Hanya memfilter data yang ada jenis kelaminnya (mengabaikan baris anakan yang tidak jelas jenis kelaminnya)
    data_dewasa = filtered_data[filtered_data['Jenis kelamin'].notna()]
    total_ternak = data_dewasa.groupby(["Jenis Ternak", "Jenis kelamin"])["Jumlah Dewasa"].sum().reset_index()
    
    fig_ternak = px.bar(
        total_ternak, x="Jenis Ternak", y="Jumlah Dewasa", color="Jenis kelamin",
        barmode="group", color_discrete_sequence=earth_tones, text="Jumlah Dewasa"
    )
    st.plotly_chart(fig_ternak, use_container_width=True)

    # Pie chart total keseluruhan per jenis
    st.subheader("🥧 Proporsi Kepemilikan Ternak")
    total_per_jenis = filtered_data.groupby("Jenis Ternak")[["Jumlah Dewasa", "Anakan"]].sum().sum(axis=1).reset_index(name="Total Ekor")
    fig_pie = px.pie(total_per_jenis, names="Jenis Ternak", values="Total Ekor", color_discrete_sequence=earth_tones)
    st.plotly_chart(fig_pie, use_container_width=True)


# ================= HALAMAN 3: REKAPITULASI TABEL =================
elif menu == "📋 Rekapitulasi Total":
    st.title("📋 Rekapitulasi Data Peternak")
    st.write("Tabel ini merangkum total kepemilikan ternak dari masing-masing warga.")
    st.write("---")
    
    # Membuat pivot table untuk menggabungkan jantan, betina, dan anakan dalam satu baris per pemilik
    tabel_rekap = data_peternak.groupby(['Nama Pemilik', 'Alamat', 'Jenis Ternak', 'Ketersediaan']).agg({
        'Jumlah Dewasa': 'sum',
        'Anakan': 'sum',
        'Total': 'max' # Mengambil nilai total terbesar dari baris yang di-merge
    }).reset_index()
    
    # Mengganti nama kolom agar lebih enak dibaca
    tabel_rekap.columns = ['Nama Pemilik', 'Alamat', 'Jenis Ternak', 'Ketersediaan (Proker)', 'Total Dewasa', 'Total Anakan', 'Total Keseluruhan']
    
    st.dataframe(tabel_rekap, use_container_width=True)
