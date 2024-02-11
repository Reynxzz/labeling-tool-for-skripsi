import streamlit as st
import pandas as pd
from datetime import datetime
from deta import Deta

db = Deta(st.secrets["data_key"])
labeled_data_db = db.Base("labeling-tool-data")

st.set_page_config(
    page_title="Labeling Tool by Rey",
    page_icon="🥵",
    menu_items={
        'Get Help': 'https://api.whatsapp.com/send/?phone=6282114931994&text&type=phone_number&app_absent=0',
        'Report a bug': "https://api.whatsapp.com/send/?phone=6282114931994&text&type=phone_number&app_absent=0",
        'About': "# This is a labeling tool for skripsi"
    }
)

@st.cache_data
def load_data():
    # Load data from Deta database
    data = pd.read_csv('dataset/df_all_keywords_no_duplicates.csv')
    data['label'] = None
    return data

def save_labeled_data(labeled_data):  
    labeled_data = labeled_data.fillna(0)
    labeled_data.rename(columns={"link": "key"}, inplace=True)
    labeled_data_db.put_many(list(labeled_data.to_dict(orient="index").values()))

def fetch_data():
    db_labeled = labeled_data_db.fetch().items
    labeled_data = [{'key': item['key'], 'label': item['label']} for item in db_labeled]
    return labeled_data

def titles():
    st.title('Pangan Olahan Ilegal Labeling Tool')
    st.caption('Dibuat untuk penelitian **PENERAPAN TEXT MINING PADA E-COMMERCE ANALYTICS TOOL UNTUK DETEKSI PENJUALAN PANGAN OLAHAN ILEGAL** oleh **Muhamad Luthfi Reynaldi**. Data yang digunakan berasal dari situs **shopee.co.id** [Diakses pada **9 Februari 2024**].')

    st.caption("📄 **Petunjuk penggunaaan:**")
    st.caption("\
    1. Lakukan pelabelan **per halaman**. Satu halaman terdiri dari **20 produk** (total: 3425 produk).\n \
    2. Pada setiap halaman ditampilkan judul, harga, lokasi, dan banyak produk terjual.\n \
    3. Untuk melihat lebih detail pada sumber situs, Anda dapat **menekan tautan** pada setiap produk.\n \
    4. Silakan simpan data yang sudah terlabeli (20 produk) dengan menekan tombol **Simpan data terlabeli** pada bagian bawah halaman.\n \
    5. Jika sudah tersimpan, silakan **berpindah ke halaman selanjutnya** menggunakan tombol (+) atau (-) di bagian atas halaman.\n\
    6. Jika ingin memperbarui label produk yang sudah dilabeli sebelumnya, pindah ke halaman produk tersebut dan simpan kembali label terbaru dengan menekan tombol **Simpan data terlabeli**.")

def labeling_tool():
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    titles()
    page_number = st.number_input('Halaman', min_value=1, max_value=(len(st.session_state.data) - 1) // 20 + 1, value=1)
    st.caption("Ketik atau gunakan (+) dan (-) untuk berpindah halaman.")

    start_index = (page_number - 1) * 20
    end_index = min(len(st.session_state.data), page_number * 20)

    labeled_rows = []
    
    df_labeled = fetch_data()
    st.caption(f":blue[{len(df_labeled)} data] telah dilabeli.")

    with st.form(key="submit-20-data"):
        for index, row in st.session_state.data.iloc[start_index:end_index].iterrows():
            st.write(f"<h1 style='font-size: 24px;'>{index + 1}. {row['title']}</h1>", unsafe_allow_html=True)
            st.caption(f"Rp{row['price']} - " f"{row['location']} - " f"{row['sold']}")
            st.markdown(f"👁 Lihat lebih detail pada situs [Shopee]({row['link']}).")
            
            if row['link'] in [item['key'] for item in df_labeled]:
                labeled_item = next((item for item in df_labeled if item['key'] == row['link']), None)
                label_text = "Ilegal" if labeled_item['label'] == 1 else "Legal"
                st.caption(f"Produk ini sudah Anda labeli sebelumnya: **{label_text}**. Ganti dan simpan kembali untuk memperbarui.")
            
            label = st.radio("Pilih label yang sesuai:", options=["Legal", "Ilegal"], key=index)
            
            if label == "Legal":
                row['label'] = 0
            elif label == "Ilegal":
                row['label'] = 1
                
            labeled_rows.append(row)

        # Save labeled data
        st.caption("Silakan simpan data yang sudah dilabeli dengan menekan tombol berikut.")
        submit = st.form_submit_button(label="💾 Simpan data terlabeli", type="primary")
        if submit:
            label_df = pd.DataFrame(labeled_rows)
            label_df['timestamp'] = str(datetime.now())
            save_labeled_data(label_df)
            st.write("🥳 Data berhasil disimpan... Silakan ke halaman selanjutnya!")
            st.balloons()

def main():
    labeling_tool()

if __name__ == "__main__":
    main()
