import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp Theo Tuần")

# 1. Đọc file Excel (lưu ý: cần cài thư viện openpyxl)
file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_all_sheets():
    # Đọc tất cả các sheet trong file Excel
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_all_sheets()
    
    # 2. Tạo menu chọn tuần (dựa trên tên Sheet)
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", sheet_names)
    
    # 3. Lấy dữ liệu của sheet đã chọn
    df = all_sheets[selected_sheet]
    # Làm sạch dữ liệu: Bỏ 2 dòng đầu (nếu có tiêu đề thừa), lấy 4 câu hỏi
    df = df.iloc[2:6] 
    
    st.header(f"Dữ liệu: {selected_sheet}")
    
    # 4. Hiển thị biểu đồ
    df_t = df.set_index(df.columns[0]).T
    st.bar_chart(df_t)
    
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Bạn hãy đảm bảo đã upload file 'Du_Lieu_Danh_Gia.xlsx' lên GitHub nhé!")
