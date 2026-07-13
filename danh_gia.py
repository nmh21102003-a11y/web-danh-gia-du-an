import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="Hệ thống đánh giá dự án", layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Dự Án Tổng Hợp")

# 1. Tự động lấy danh sách file CSV trong thư mục
# Giả sử các file của bạn đặt tên dạng: Tuan1.csv, Tuan2.csv...
files = [f for f in os.listdir('.') if f.endswith('.csv')]
files.sort() # Sắp xếp theo thứ tự tuần

if not files:
    st.warning("Chưa có dữ liệu. Vui lòng tải các file tuần lên!")
else:
    # 2. Tạo menu chọn tuần
    selected_file = st.sidebar.selectbox("Chọn tuần đánh giá:", files)
    st.header(f"Dữ liệu của: {selected_file}")

    @st.cache_data
    def load_data(file):
        # Đọc dữ liệu (bạn có thể điều chỉnh skiprows tùy theo file thực tế)
        df = pd.read_csv(file, encoding='utf-8')
        return df

    df = load_data(selected_file)

    # 3. Vẽ biểu đồ chuyên nghiệp với Altair
    # Giả định cột đầu tiên là tên nhân viên
    emp_col = df.columns[0]
    
    for i in range(1, len(df.columns)):
        col_name = df.columns[i]
        st.subheader(f"📈 {col_name}")
        
        chart = alt.Chart(df).mark_bar(color='#4c78a8').encode(
            x=alt.X(f'{col_name}:Q', title='Điểm số'),
            y=alt.Y(f'{emp_col}:N', sort='-x', title=''),
            tooltip=[emp_col, col_name]
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)
