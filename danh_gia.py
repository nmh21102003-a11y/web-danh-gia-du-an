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
    df = all_sheets[selected_sheet]

    # --- CHUẨN BỊ DỮ LIỆU ---
    # Bỏ cột rác do Excel tự sinh ra
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Lấy cột đầu tiên (Thành viên) làm trục ngang (Trục X) cho toàn bộ biểu đồ
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Rút gọn tên câu hỏi cho biểu đồ gọn gàng
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]
    
    # Ép dữ liệu về dạng số học chuẩn để không bị lỗi sập hệ thống (Segmentation fault)
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    cols = df_numeric.columns.tolist()

    # Kiểm tra đảm bảo có đủ 4 cột điểm để vẽ
    if len(cols) >= 4:
        c1, c2, c3, c4 = cols[0], cols[1], cols[2], cols[3]
        
        st.header(f"📌 Dữ liệu: {selected_sheet}")
        st.write("---")

        # ==========================================
        # CHART 1: CÂU 1 (Biểu đồ Cột hiển thị toàn bộ thành viên)
        # ==========================================
        st.subheader(f"1️⃣ Điểm tiêu chí: {c1}")
        st.bar_chart(df_numeric[[c1]]) 

        # ==========================================
        # CHART 2: CÂU 2 (Biểu đồ Đường hiển thị toàn bộ thành viên)
        # ==========================================
        st.subheader(f"2️⃣ Điểm tiêu chí: {c2}")
        st.line_chart(df_numeric[[c2]])

        # ==========================================
        # CHART 3: CÂU 3 & CÂU 4 (Gộp chung vào 1 biểu đồ)
        # ==========================================
        st.subheader(f"3️⃣ So sánh tiêu chí: {c3} & {c4}")
        # Truyền cả 2 cột vào, Streamlit sẽ tự động vẽ 2 màu khác nhau trên cùng 1 biểu đồ
        st.bar_chart(df_numeric[[c3, c4]])

    else:
        st.warning("File Excel cần ít nhất 4 cột tiêu chí đánh giá để hiển thị đủ các biểu đồ này.")
        
    # --- BẢNG DỮ LIỆU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
