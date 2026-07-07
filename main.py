import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Konfigurasi Halaman (Minimalist & Clean)
st.set_page_config(page_title="Dashboard Pendataan Ternak", layout="wide")

# Fungsi Load & Clean Data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Data Ternak Sarwodadi, Giritirta.xlsx', sheet_name='SARWODADI', header=1)
    except:
        df = pd.read_csv('Data Ternak Sarwodadi, Giritirta.xlsx - SARWODADI.csv', header=1)
    
    df_s = df.iloc[:, 0:10].copy()
    df_s.columns = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah Dewasa', 'Total', 'Ketersediaan', 'Anakan']
    
    kolom_identitas = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak']
    df_s[kolom_identitas] = df_s[kolom_identitas].ffill()
    
    df_s['Jumlah Dewasa'] = pd.to_numeric(df_s['Jumlah Dewasa'], errors='coerce').fillna(0)
    df_s['Anakan'] = pd.to_numeric(df_s['Anakan'], errors='coerce').fillna(0)
    df_s['Total'] = pd.to_numeric(df_s['Total'], errors='coerce').fillna(0)
    
    df_s['Ketersediaan'] = df_s['Ketersediaan'].fillna('Belum Konfirmasi')
    
    # Membersihkan format RT/RW agar tampil rapi di grafik
    df_s['RT'] = "RT 0" + df_s['RT'].astype(str).str.replace('.0', '', regex=False)
    df_s['RW'] = "RW 0" + df_s['RW'].astype(str).str.replace('.0', '', regex=False)
    
    df_s = df_s[df_s['Jenis kelamin'].notna() | (df_s['Jumlah Dewasa'] > 0) | (df_s['Anakan'] > 0)]
    
    # Menghitung Total Ekor (Dewasa + Anakan) untuk grafik
    df_s['Total Ekor'] = df_s['Jumlah Dewasa'] + df_s['Anakan']
    
    return df_s

data_peternak = load_data()
earth_tones = ['#8D6E63', '#D7CCC8', '#A1887F', '#5D4037', '#BCAAA4']

# Sidebar Navigasi
with st.sidebar:
    menu = option_menu(
        "📌 Menu Navigasi",
        ["📖 Profil Wilayah", "📊 Dashboard Data Pertanian"],
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

# ================= HALAMAN 2: DASHBOARD (SEPERTI KATING) =================
elif menu == "📊 Dashboard Data Pertanian":
    st.title("📊 Dashboard Pendataan Peternak Warga")
    st.write("---")

    # === Sidebar Filter (Radio Button seperti kating) ===
    st.sidebar.header("🔎 Filter Data")
    filter_mode = st.sidebar.radio("Filter berdasarkan:", ["RW", "RT"])

    if filter_mode == "RW":
        pilihan_unik = sorted(data_peternak["RW"].unique())
        selected_lokasi = st.sidebar.multiselect("Pilih RW", options=pilihan_unik, default=pilihan_unik)
        filtered_data = data_peternak[data_peternak["RW"].isin(selected_lokasi)]
        kolom_sumbu_x = "RW"
    else:
        pilihan_unik = sorted(data_peternak["RT"].unique())
        selected_lokasi = st.sidebar.multiselect("Pilih RT", options=pilihan_unik, default=pilihan_unik)
        filtered_data = data_peternak[data_peternak["RT"].isin(selected_lokasi)]
        kolom_sumbu_x = "RT"

    # === Dataframe di Atas ===
    st.subheader("📄 Data Peternak")
    tabel_tampil = filtered_data[['Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah Dewasa', 'Anakan', 'Ketersediaan']]
    st.dataframe(tabel_tampil, use_container_width=True)
    st.write("---")

    # === Bar chart per RT/RW ===
    st.subheader(f"📊 Total Ternak per {kolom_sumbu_x}")
    total_per_wilayah = filtered_data.groupby([kolom_sumbu_x, "Jenis Ternak"])["Total Ekor"].sum().reset_index()
    
    fig_bar = px.bar(
        total_per_wilayah,
        x=kolom_sumbu_x, y="Total Ekor", color="Jenis Ternak",
        barmode="group",
        color_discrete_sequence=earth_tones,
        text_auto=True
    )
    # Memaksa agar sumbu X rapi berjejer
    fig_bar.update_xaxes(type='category')
    st.plotly_chart(fig_bar, use_container_width=True)

    # === Pie chart total ===
    st.subheader("🥧 Distribusi Ternak Keseluruhan")
    total_all = filtered_data.groupby("Jenis Ternak")["Total Ekor"].sum().reset_index()
    fig_pie = px.pie(
        total_all,
        names="Jenis Ternak",
        values="Total Ekor",
        color_discrete_sequence=earth_tones
    )
    st.plotly_chart(fig_pie, use_container_width=True)
