import streamlit as st
import pandas as pd

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
    # Bỏ cột rác do Excel tự sinh ra
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    df_raw = df_raw.set_index(col_cau_hoi)
    
    # Lật bảng: Đưa tên thành viên xuống làm trục X
    df = df_raw.T 
    df.index.name = "Thành viên"
    
    # Rút gọn tên câu hỏi (VD: "1. Ai là người..." -> "Câu 1")
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

        # ==========================================
        # CHART 1: CÂU 1
        # ==========================================
        st.subheader(f"1️⃣ Điểm tiêu chí: {c1}")
        st.bar_chart(df_numeric[[c1]]) 

        # ==========================================
        # CHART 2: CÂU 2
        # ==========================================
        st.subheader(f"2️⃣ Điểm tiêu chí: {c2}")
        st.bar_chart(df_numeric[[c2]])

        # ==========================================
        # CHART 3: CÂU 3 & CÂU 4 (Gộp chung màu)
        # ==========================================
        st.subheader(f"3️⃣ So sánh tiêu chí: {c3} & {c4}")
        st.bar_chart(df_numeric[[c3, c4]])

    else:
        st.warning("File Excel cần ít nhất 4 dòng câu hỏi đánh giá để hiển thị đủ biểu đồ.")
        
    # --- BẢNG DỮ LIỆU ĐÃ XOAY CHIỀU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
