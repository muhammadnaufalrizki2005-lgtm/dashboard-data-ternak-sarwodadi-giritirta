#!/usr/bin/env python3
"""
Text to Python Conversion
Generated: 2026-07-07T10:13:49.578Z
Total Lines: 110
"""

def process_text():
    """
    Process and analyze text data
    Returns: dictionary with text data and metadata
    """
    text_lines = [
    "import streamlit as st",
    "import pandas as pd",
    "import plotly.express as px",
    "import folium",
    "from streamlit_folium import st_folium",
    "from streamlit_option_menu import option_menu",
    "# Konfigurasi Halaman (Minimalist & Clean)",
    "st.set_page_config(page_title=\"Dashboard Pendataan Ternak\", layout=\"wide\")",
    "# Fungsi Load & Clean Data",
    "@st.cache_data",
    "def load_data():",
    "    # Membaca file excel, header ada di baris ke-2 (index 1)",
    "    file_path = 'Data Ternak Sarwodadi, Giritirta.xlsx'",
    "    df = pd.read_excel(file_path, sheet_name='SARWODADI', header=1)",
    "    # Mengambil kolom khusus Dusun Sarwodadi saja (kolom 0 sampai 9)",
    "    df_s = df.iloc[:, 0:10].copy()",
    "    df_s.columns = ['No', 'Nama Pemilik', 'NIK', 'Alamat', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah', 'Total', 'Ketersediaan', 'Keterangan']",
    "    # Forward fill untuk mengisi sel yang di-merge",
    "    df_s[['No', 'Nama Pemilik', 'NIK', 'Alamat', 'Jenis Ternak']] = df_s[['No', 'Nama Pemilik', 'NIK', 'Alamat', 'Jenis Ternak']].ffill()",
    "    # Membuang baris yang kosong pada kolom Jumlah dan Jenis kelamin",
    "    df_s = df_s.dropna(subset=['Jenis kelamin', 'Jumlah']).copy()",
    "    df_s['Jumlah'] = pd.to_numeric(df_s['Jumlah'], errors='coerce')",
    "    return df_s",
    "data_peternak = load_data()",
    "# Palet warna Earth Tone",
    "earth_tones = ['#8D6E63', '#D7CCC8', '#A1887F', '#5D4037', '#BCAAA4']",
    "# Sidebar Navigasi",
    "with st.sidebar:",
    "    menu = option_menu(",
    "        \"📌 Menu Navigasi\",",
    "        [\"📖 Profil Dusun\", \"📊 Dashboard Ternak\"],",
    "        menu_icon=\"list\",",
    "        default_index=0,",
    "        styles={",
    "            \"container\": {\"padding\": \"5!important\", \"background-color\": \"#fafafa\"},",
    "            \"icon\": {\"color\": \"#5D4037\", \"font-size\": \"20px\"}, ",
    "            \"nav-link\": {\"font-size\": \"15px\", \"text-align\": \"left\", \"margin\":\"0px\", \"--hover-color\": \"#eee\"},",
    "            \"nav-link-selected\": {\"background-color\": \"#8D6E63\"},",
    "        }",
    "    )",
    "# Halaman Profil",
    "if menu == \"📖 Profil Dusun\":",
    "    st.markdown(\"## 📖 Profil Dusun Sarwodadi, Giritirta\")",
    "    st.write(\"---\")",
    "    st.markdown(\"\"\"",
    "    **Dusun Sarwodadi** merupakan salah satu wilayah di Desa Giritirta. Wilayah ini memiliki potensi besar di sektor peternakan yang menjadi salah satu pilar ekonomi warganya.",
    "    ### 👥 Potensi Peternakan",
    "    Sebagian besar warga Dusun Sarwodadi menggantungkan hidupnya sebagai peternak. Berdasarkan pendataan terbaru, komoditas ternak utama di wilayah ini meliputi:",
    "    * **Kambing**",
    "    * **Domba**",
    "    * **Sapi**",
    "    Sektor ini sangat potensial untuk dikembangkan lebih lanjut melalui program-program optimalisasi pakan dan manajemen kesehatan ternak.",
    "    \"\"\")",
    "    # Peta Dummy (Silakan sesuaikan koordinatnya)",
    "    st.markdown(\"### 🗺️ Lokasi Giritirta\")",
    "    giritirta_coords = [-8.0333, 110.3667] # Koordinat ilustrasi",
    "    m = folium.Map(location=giritirta_coords, zoom_start=13)",
    "    folium.Marker(",
    "        location=giritirta_coords,",
    "        popup=\"Giritirta\",",
    "        tooltip=\"Lokasi Desa Giritirta\",",
    "        icon=folium.Icon(color=\"darkred\", icon=\"home\")",
    "    ).add_to(m)",
    "    st_folium(m, width=700, height=400)",
    "# Halaman Dashboard",
    "elif menu == \"📊 Dashboard Ternak\":",
    "    st.title(\"📊 Dashboard Pendataan Peternak Warga\")",
    "    st.write(\"---\")",
    "    # === Sidebar Filter ===",
    "    st.sidebar.header(\"🔎 Filter Data\")",
    "    # Filter RT/Alamat",
    "    alamat_list = sorted(data_peternak[\"Alamat\"].dropna().unique())",
    "    selected_alamat = st.sidebar.multiselect(",
    "        \"Pilih Wilayah (RT/RW)\", ",
    "        options=alamat_list,",
    "        default=alamat_list",
    "    )",
    "    filtered_data = data_peternak[data_peternak[\"Alamat\"].isin(selected_alamat)]",
    "    # === Metrik Utama ===",
    "    col1, col2, col3 = st.columns(3)",
    "    with col1:",
    "        st.metric(label=\"Total Populasi Ternak\", value=f\"{int(filtered_data['Jumlah'].sum())} Ekor\")",
    "    with col2:",
    "        st.metric(label=\"Total Peternak\", value=f\"{filtered_data['Nama Pemilik'].nunique()} Orang\")",
    "    with col3:",
    "        st.metric(label=\"Jenis Ternak Terbanyak\", value=filtered_data.groupby('Jenis Ternak')['Jumlah'].sum().idxmax())",
    "    st.write(\"---\")",
    "    # === Dataframe ===",
    "    st.subheader(\"📄 Rincian Data Peternak\")",
    "    st.dataframe(filtered_data[['Nama Pemilik', 'Alamat', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah']], use_container_width=True)",
    "    # === Bar chart per Jenis Ternak & Kelamin ===",
    "    st.subheader(\"📊 Distribusi Jenis Ternak\")",
    "    total_ternak = filtered_data.groupby([\"Jenis Ternak\", \"Jenis kelamin\"])[\"Jumlah\"].sum().reset_index()",
    "    fig_ternak = px.bar(",
    "        total_ternak,",
    "        x=\"Jenis Ternak\", y=\"Jumlah\", color=\"Jenis kelamin\",",
    "        barmode=\"group\",",
    "        color_discrete_sequence=earth_tones",
    "    )",
    "    st.plotly_chart(fig_ternak, use_container_width=True)",
    "    # === Pie chart total ===",
    "    st.subheader(\"🥧 Proporsi Ternak Keseluruhan\")",
    "    total_all = filtered_data.groupby(\"Jenis Ternak\")[\"Jumlah\"].sum().reset_index()",
    "    fig_pie = px.pie(",
    "        total_all,",
    "        names=\"Jenis Ternak\",",
    "        values=\"Jumlah\",",
    "        color_discrete_sequence=earth_tones",
    "    )",
    "    st.plotly_chart(fig_pie, use_container_width=True)"
    ]
    
    # Calculate metadata
    metadata = {
        'total_lines': 110,
        'total_characters': 5054,
        'total_words': 465,
        'created_at': '2026-07-07T10:13:49.578Z',
        'version': '1.0'
    }
    
    # Calculate statistics
    line_lengths = [len(line) for line in text_lines]
    statistics = {
        'average_line_length': sum(line_lengths) // len(line_lengths) if line_lengths else 0,
        'longest_line': max(line_lengths) if line_lengths else 0,
        'shortest_line': min(line_lengths) if line_lengths else 0,
        'empty_lines': 26
    }
    
    return {
        'lines': text_lines,
        'metadata': metadata,
        'statistics': statistics
    }

def display_text(data):
    """Display text data with metadata"""
    print("Metadata:")
    for key, value in data['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\nStatistics:")
    for key, value in data['statistics'].items():
        print(f"  {key}: {value}")
    
    print("\nText Lines:")
    for i, line in enumerate(data['lines'], 1):
        print(f"Line {i}: {line}")

if __name__ == "__main__":
    data = process_text()
    display_text(data)