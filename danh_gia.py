import streamlit as st
import pandas as pd
import altair as alt  # Thư viện vẽ biểu đồ chuyên sâu tích hợp sẵn của Streamlit

st.set_page_config(layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Chi Tiết")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # --- DỌN DẸP & ĐẢO CHIỀU DỮ LIỆU ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    df_raw = df_raw.set_index(col_cau_hoi)
    
    # Xoay bảng (Đưa Thành viên ra trục ngang)
    df = df_raw.T 
    df.index.name = "Thành viên"
    
    # Rút gọn tên câu hỏi
    def rut_gon_ten(ten):
        ten = str(ten)
        if '.' in ten:
            return f"Câu {ten.split('.')[0].strip()}"
        return ten[:20] + "..." if len(ten) > 20 else ten

    df.columns = [rut_gon_ten(col) for col in df.columns]
    
    # Ép dữ liệu về số học
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    cols = df_numeric.columns.tolist()

    if len(cols) >= 4:
        c1, c2, c3, c4 = cols[0], cols[1], cols[2], cols[3]
        
        st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
        st.write("---")

        # --- CHUẨN BỊ VẼ BIỂU ĐỒ CÓ THANH CUỘN ---
        df_chart = df_numeric.reset_index()
        ten_cot_tv = df_chart.columns[0]

        # Đặt chiều rộng cố định để ÉP TẠO THANH CUỘN (1200px)
        CHIEU_RONG = 1200

        # ==========================================
        # CHART 1: CÂU 1 (Biểu đồ Cột)
        # ==========================================
        st.subheader(f"1️⃣ Điểm tiêu chí: {c1}")
        chart1 = alt.Chart(df_chart).mark_bar(color='#3498db').encode(
            x=alt.X(f'{ten_cot_tv}:N', axis=alt.Axis(labelAngle=0, title='')), # labelAngle=0 ép tên nằm Ngang
            y=alt.Y(f'{c1}:Q', axis=alt.Axis(title='Điểm số')),
            tooltip=[ten_cot_tv, c1]
        ).properties(width=CHIEU_RONG, height=400)
        st.altair_chart(chart1, use_container_width=False) # False để nhả thanh cuộn

        # ==========================================
        # CHART 2: CÂU 2 (Biểu đồ Đường)
        # ==========================================
        st.subheader(f"2️⃣ Điểm tiêu chí: {c2}")
        chart2 = alt.Chart(df_chart).mark_line(point=alt.OverlayMarkDef(color="red", size=100), color='#e74c3c', strokeWidth=3).encode(
            x=alt.X(f'{ten_cot_tv}:N', axis=alt.Axis(labelAngle=0, title='')), # labelAngle=0 ép tên nằm Ngang
            y=alt.Y(f'{c2}:Q', axis=alt.Axis(title='Điểm số')),
            tooltip=[ten_cot_tv, c2]
        ).properties(width=CHIEU_RONG, height=400)
        st.altair_chart(chart2, use_container_width=False)

        # ==========================================
        # CHART 3: CÂU 3 & CÂU 4 (Gộp)
        # ==========================================
        st.subheader(f"3️⃣ So sánh tiêu chí: {c3} & {c4}")
        # Trộn cột 3 và 4 lại để Altair có thể vẽ chung 1 biểu đồ
        df_melt = df_chart[[ten_cot_tv, c3, c4]].melt(id_vars=[ten_cot_tv], var_name='Tiêu chí', value_name='Điểm')
        chart3 = alt.Chart(df_melt).mark_bar().encode(
            x=alt.X(f'{ten_cot_tv}:N', axis=alt.Axis(labelAngle=0, title='')), # labelAngle=0 ép tên nằm Ngang
            y=alt.Y('Điểm:Q', axis=alt.Axis(title='Tổng Điểm')),
            color='Tiêu chí:N',
            tooltip=[ten_cot_tv, 'Tiêu chí', 'Điểm']
        ).properties(width=CHIEU_RONG, height=400)
        st.altair_chart(chart3, use_container_width=False)

    else:
        st.warning("File Excel cần ít nhất 4 dòng câu hỏi đánh giá để hiển thị đủ biểu đồ.")
        
    # --- BẢNG DỮ LIỆU ĐÃ XOAY CHIỀU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        # Bảng hiển thị tự động có thanh cuộn nếu màn hình nhỏ
        st.dataframe(df_numeric, use_container_width=False)

except Exception as e:
    st.error(f"Lỗi: {e}")
