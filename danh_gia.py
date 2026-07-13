import streamlit as st
import pandas as pd

st.title("📊 Biểu Đồ Đánh Giá")

try:
    # 1. Đọc file
    # Nếu file là .csv thì dùng pd.read_csv, nếu .xlsx thì dùng pd.read_excel
    df = pd.read_excel("Du_Lieu_Danh_Gia.xlsx")
    
    # 2. Xử lý dữ liệu: Bỏ cột chữ, chỉ lấy cột số để vẽ
    # Chúng ta lấy cột đầu tiên làm tên (trục dọc)
    df = df.set_index(df.columns[0])
    
    # 3. Vẽ biểu đồ ngay lập tức
    st.bar_chart(df)
    
except Exception as e:
    st.error(f"Lỗi: {e}")
