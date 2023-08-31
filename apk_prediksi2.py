import pickle
import streamlit as st
import pandas as pd
import numpy as np
import xlwt
from sklearn.linear_model import Ridge
from sklearn.preprocessing import LabelEncoder
from io import BytesIO


# Mengganti judul dan ikon
st.set_page_config(page_title="Aplikasi Prediksi Lama Studi", page_icon=":bar_chart:", layout="wide")

# Load model dari file pickle
model = pickle.load(open('data apk2.sav', 'rb'))

# Load label encoder dari file pickle jika sudah dilatih pada data pelatihan sebelumnya
with open('label_encoder.pkl', 'rb') as file:
    labelencoder = pickle.load(file)


# Kolom-kolom yang digunakan saat melatih model
kolom_model = ['JENIS KELAMIN', 'IP_S1', 'IP_S2', 'IP_S3', 'IP_S4', 'IP_S5', 'IPK']


def prediksi_file(file):
    # Baca data dari file (misalnya file dalam format Excel)
    data_prediksi = pd.read_excel(file)

    # Lakukan pra-pemrosesan jika diperlukan
    print(data_prediksi.columns)
    data_prediksi['JENIS KELAMIN'] = labelencoder.transform(data_prediksi['JENIS KELAMIN'])
    # Lakukan prediksi menggunakan model yang telah dilatih
    hasil_prediksi = model.predict(data_prediksi)

    # Buat DataFrame untuk menyimpan hasil prediksi dan tambahkan kolom 'Hasil Prediksi'
    hasil_prediksi_df = pd.DataFrame(data_prediksi)
    hasil_prediksi_df['Hasil Prediksi'] = hasil_prediksi

    return hasil_prediksi_df
          

def konversi_ke_teks(nilai_prediksi):
    hasil_teks = []
    for pred in nilai_prediksi:
        if isinstance(pred, (int, float)):
            tahun = int(pred)
            bulan = int((pred - tahun) * 12)

            if tahun == 1:
                teks_tahun = "1 tahun"
            else:
                teks_tahun = f"{tahun} tahun"

            if bulan == 1:
                teks_bulan = "1 bulan"
            else:
                teks_bulan = f"{bulan} bulan"

            if tahun == 0:
                hasil_teks.append(teks_bulan)
            elif bulan == 0:
                hasil_teks.append(teks_tahun)
            else:
                hasil_teks.append(f"{teks_tahun} {teks_bulan}")
        else:
            hasil_teks.append("Nilai prediksi tidak valid.")
    
    return hasil_teks
def konversi_ke_teks2(nilai_prediksi):
        if isinstance(nilai_prediksi, (int, float)):
            tahun = int(nilai_prediksi)
            bulan = int((nilai_prediksi - tahun) * 12)
            
            if tahun == 1:
                teks_tahun = "1 tahun"
            else:
                teks_tahun = f"{tahun} tahun"

            if bulan == 1:
                teks_bulan = "1 bulan"
            else:
                teks_bulan = f"{bulan} bulan"

            if tahun == 0:
                hasil_teks = teks_bulan
            elif bulan == 0:
                hasil_teks = teks_tahun
            else:
                hasil_teks = f"{teks_tahun} {teks_bulan}"

            return hasil_teks
            
def save_to_excel(dataframe):
    output = BytesIO()
    workbook = xlwt.Workbook()
    worksheet = workbook.add_sheet('Hasil Prediksi')

    for row_num, row_data in enumerate(dataframe.values):
        for col_num, cell_value in enumerate(row_data):
            worksheet.write(row_num, col_num, cell_value)

    workbook.save(output)
    output.seek(0)
    return output

def main():
    st.title('Aplikasi Prediksi Lama Kelulusan Mahasiswa')

    # Tambahkan checkbox untuk memilih metode prediksi
    prediksi_dari_file = st.checkbox('Prediksi dari File')

    if prediksi_dari_file:
        # Upload file dari pengguna jika checkbox dicentang
        file = st.file_uploader('Upload file dalam format excel', type=['xlsx'])

        if file is not None:
            hasil_prediksi = prediksi_file(file)

             # Konversi hasil prediksi angka menjadi teks
            hasil_prediksi['Hasil Prediksi'] = konversi_ke_teks(hasil_prediksi['Hasil Prediksi'])

            # Tampilkan hasil prediksi ke pengguna dalam bentuk tabel
            st.header('Hasil Prediksi dari File')
            st.write(hasil_prediksi)
            # Tombol untuk menyimpan hasil prediksi ke dalam file Excel
            st.write('' f"<b>*Jenis Kelamin 1(laki-laki), 2(Perempuan)</b>", unsafe_allow_html=True)
        if st.button('Simpan Hasil Prediksi'):
            if not hasil_prediksi['Hasil Prediksi'].isnull().any():
                excel_output = save_to_excel(hasil_prediksi)
                st.download_button('Download Hasil Prediksi', excel_output.getvalue(), file_name='hasil_prediksi.xls', mime='application/vnd.ms-excel')
            else:
                st.warning('Hasil prediksi kosong. Pastikan file yang diunggah sesuai format dan telah diproses dengan benar.')
        
                

    else:
        # Tambahkan input manual jika checkbox tidak dicentang
        # Fungsi untuk mengkonversi jenis kelamin menjadi nilai 1 (laki-laki) atau 2 (wanita)
        JENIS_KELAMIN = st.selectbox('Pilih Jenis Kelamin', ["Laki-laki", "Perempuan"])

        def konversi_ke_nilai(jenis_kelamin):
            if jenis_kelamin == "Laki-laki":
                return 1
            elif jenis_kelamin == "Perempuan":
                return 2
            else:
                return None

        IP_S1 = st.number_input('Inputkan Nilai IP Semester 1')
        IP_S2 = st.number_input('Inputkan Nilai IP Semester 2')
        IP_S3 = st.number_input('Inputkan Nilai IP Semester 3')
        IP_S4 = st.number_input('Inputkan Nilai IP Semester 4')
        IP_S5 = st.number_input('Inputkan Nilai IP Semester 5')
        IPK = st.number_input('Inputkan Nilai IPK')

        if st.button('ESTIMASI LAMA STUDI'):
            nilai_jenis_kelamin = konversi_ke_nilai(JENIS_KELAMIN)

            # Pastikan nilai jenis kelamin tidak None sebelum melakukan prediksi
            if nilai_jenis_kelamin is not None:
                predict = model.predict([[nilai_jenis_kelamin, IP_S1, IP_S2, IP_S3, IP_S4, IP_S5, IPK]])
                predicted_value = predict[0]

                hasil_teks = konversi_ke_teks2(predicted_value)
                st.write('ESTIMASI LAMA STUDI ANDA :', f"<b>{hasil_teks}</b>", unsafe_allow_html=True)
if __name__ == '__main__':
    main()
   
