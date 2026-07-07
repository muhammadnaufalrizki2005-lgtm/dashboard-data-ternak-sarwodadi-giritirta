import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Pendataan Ternak", layout="wide")

# Fungsi Load Data
@st.cache_data
def load_data():
    file_path = 'Data Ternak Sarwodadi, Giritirta.xlsx'
    try:
        df = pd.read_excel(file_path, sheet_name='SARWODADI', header=1)
    except:
        file_path_csv = 'Data Ternak Sarwodadi, Giritirta.xlsx - SARWODADI.csv'
        df = pd.read_csv(file_path_csv, header=1)
    
    df_s = df.iloc[:, 0:10].copy()
    df_s.columns = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah', 'Total', 'Ketersediaan', 'Keterangan']
    
    df_s[['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak']] = df_s[['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak']].ffill()
    
    df_s = df_s.dropna(subset=['Jenis kelamin', 'Jumlah']).copy()
    df_s['Jumlah'] = pd.to_numeric(df_s['Jumlah'], errors='coerce')
    
    df_s['Alamat'] = "RT 0" + df_s['RT'].astype(str).str.replace('.0', '', regex=False) + " / RW 0" + df_s['RW'].astype(str).str.replace('.0', '', regex=False)
    
    return df_s

data_peternak = load_data()

# Palet warna Earth Tone
earth_tones = ['#8D6E63', '#D7CCC8', '#A1887F', '#5D4037', '#BCAAA4']

# Sidebar Navigasi
with st.sidebar:
    menu = option_menu(
        "📌 Menu Navigasi",
        ["📖 Profil Wilayah", "📊 Dashboard Ternak"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#5D4037", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#8D6E63"},
        }
    )

# Halaman Profil
if menu == "📖 Profil Wilayah":
    st.markdown("## 📖 Profil Desa Sarwodadi & Giritirta")
    st.write("---")
    
    st.markdown("""
    **Desa Sarwodadi dan Desa Giritirta** merupakan desa yang terletak di **Kecamatan Pejawaran, Kabupaten Banjarnegara, Provinsi Jawa Tengah**. 
    
    Berada di kawasan pegunungan utara Banjarnegara yang sejuk, wilayah ini dikaruniai kondisi alam yang sangat mendukung untuk sektor pertanian dan peternakan. 
    
    ### 👥 Potensi Peternakan Warga
    Sektor peternakan menjadi salah satu pilar ekonomi utama bagi warga di wilayah ini. Berdasarkan pendataan mandiri, komoditas ternak yang paling banyak dibudidayakan oleh warga meliputi:
    * **Kambing**
    * **Domba**
    * **Sapi**
    
    Tingginya antusiasme warga dalam beternak menjadikan desa ini sangat potensial untuk menjadi desa percontohan dalam hal optimalisasi pakan dan kemandirian pangan.
    """)

    # Peta Pejawaran, Banjarnegara
    st.markdown("### 🗺️ Lokasi Kecamatan Pejawaran")
    pejawaran_coords = [-7.2435, 109.8450] # Titik tengah area Banjarnegara utara
    m = folium.Map(location=pejawaran_coords, zoom_start=12)

    folium.Marker(
        location=pejawaran_coords,
        popup="Kecamatan Pejawaran",
        tooltip="Lokasi Pejawaran, Banjarnegara",
        icon=folium.Icon(color="darkgreen", icon="leaf")
    ).add_to(m)

    st_folium(m, width=700, height=400)


# Halaman Dashboard
elif menu == "📊 Dashboard Ternak":
    st.title("📊 Dashboard Pendataan Peternak Warga")
    st.write("---")

    # === Sidebar Filter ===
    st.sidebar.header("🔎 Filter Data")
    
    alamat_list = sorted(data_peternak["Alamat"].dropna().unique())
    selected_alamat = st.sidebar.multiselect(
        "Pilih Wilayah (RT/RW)", 
        options=alamat_list,
        default=alamat_list
    )
    
    filtered_data = data_peternak[data_peternak["Alamat"].isin(selected_alamat)]

    # === Metrik Utama ===
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Populasi Ternak", value=f"{int(filtered_data['Jumlah'].sum())} Ekor")
    with col2:
        st.metric(label="Total Peternak", value=f"{filtered_data['Nama Pemilik'].nunique()} Orang")
    with col3:
        st.metric(label="Jenis Ternak Terbanyak", value=filtered_data.groupby('Jenis Ternak')['Jumlah'].sum().idxmax())

    st.write("---")

    # === Dataframe ===
    st.subheader("📄 Rincian Data Peternak")
    st.dataframe(filtered_data[['Nama Pemilik', 'Alamat', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah']], use_container_width=True)

    # === Bar chart per Jenis Ternak & Kelamin ===
    st.subheader("📊 Distribusi Jenis Ternak")
    total_ternak = filtered_data.groupby(["Jenis Ternak", "Jenis kelamin"])["Jumlah"].sum().reset_index()
    fig_ternak = px.bar(
        total_ternak,
        x="Jenis Ternak", y="Jumlah", color="Jenis kelamin",
        barmode="group",
        color_discrete_sequence=earth_tones
    )
    st.plotly_chart(fig_ternak, use_container_width=True)

    # === Pie chart total ===
    st.subheader("🥧 Proporsi Ternak Keseluruhan")
    total_all = filtered_data.groupby("Jenis Ternak")["Jumlah"].sum().reset_index()
    fig_pie = px.pie(
        total_all,
        names="Jenis Ternak",
        values="Jumlah",
        color_discrete_sequence=earth_tones
    )
    st.plotly_chart(fig_pie, use_container_width=True)
