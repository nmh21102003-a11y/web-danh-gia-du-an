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
    # 1. Bỏ cột rác do Excel tự sinh ra
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    
    # 2. Xoay bảng (Transpose): Vì file Excel của bạn có Câu hỏi nằm ở Cột 1 và Tên ở Dòng 1.
    col_cau_hoi = df_raw.columns[0]
    df_raw = df_raw.set_index(col_cau_hoi)
    
    # LỆNH XOAY BẢNG MA THUẬT: Đổi Hàng thành Cột, Cột thành Hàng
    df = df_raw.T 
    df.index.name = "Thành viên"
    
    # 3. Rút gọn tên câu hỏi cho biểu đồ đẹp hơn
    # Ví dụ: "1. Ai là người..." sẽ biến thành "Câu 1"
    def rut_gon_ten(ten):
        ten = str(ten)
        if '.' in ten:
            return f"Câu {ten.split('.')[0].strip()}"
        return ten[:20] + "..." if len(ten) > 20 else ten

    df.columns = [rut_gon_ten(col) for col in df.columns]
    
    # Ép dữ liệu về số học
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    cols = df_numeric.columns.tolist()

    # --- TIẾN HÀNH VẼ BIỂU ĐỒ ---
    if len(cols) >= 4:
        c1, c2, c3, c4 = cols[0], cols[1], cols[2], cols[3]
        
        st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
        st.write("---")

        # CHART 1: CÂU 1 (Biểu đồ Cột hiển thị toàn bộ thành viên)
        st.subheader(f"1️⃣ Điểm tiêu chí: {c1}")
        st.bar_chart(df_numeric[[c1]]) 

        # CHART 2: CÂU 2 (Biểu đồ Đường hiển thị toàn bộ thành viên)
        st.subheader(f"2️⃣ Điểm tiêu chí: {c2}")
        st.line_chart(df_numeric[[c2]])

        # CHART 3: CÂU 3 & CÂU 4 (Gộp chung vào 1 biểu đồ)
        st.subheader(f"3️⃣ So sánh tiêu chí: {c3} & {c4}")
        st.bar_chart(df_numeric[[c3, c4]])

    else:
        st.warning("File Excel cần ít nhất 4 dòng câu hỏi đánh giá để hiển thị đủ biểu đồ.")
        
    # --- BẢNG DỮ LIỆU ĐÃ XOAY CHIỀU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết (Đã được chuẩn hóa)"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
