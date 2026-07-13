import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Đánh giá dự án", layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp Theo Tuần")

# 1. Đọc file dữ liệu tổng hợp
# Lưu ý: File CSV phải có các cột: [Tuần, Thành viên, Câu 1, Câu 2, Câu 3, Câu 4]
@st.cache_data
def load_data():
    return pd.read_csv("data_tong_hop.csv")

try:
    df = load_data()
    
    # 2. Tạo thanh chọn tuần ở sidebar
    tuan_list = df['Tuần'].unique()
    selected_tuan = st.sidebar.selectbox("Chọn tuần cần xem:", tuan_list)
    
    # Lọc dữ liệu theo tuần đã chọn
    df_tuan = df[df['Tuần'] == selected_tuan]
    
    st.header(f"Dữ liệu: {selected_tuan}")
    
    # 3. Vẽ biểu đồ so sánh các Thành viên trong tuần đó
    # Biểu đồ ngang giúp dễ đọc tên
    st.subheader("So sánh kết quả các Thành viên")
    
    chart = alt.Chart(df_tuan).mark_bar().encode(
        x=alt.X('Câu 1: Hỗ trợ', title='Điểm số'),
        y=alt.Y('Thành viên', sort='-x', title=''),
        color='Thành viên',
        tooltip=['Thành viên', 'Câu 1: Hỗ trợ', 'Câu 2: Hiệu quả']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)
    
    # 4. Hiển thị bảng dữ liệu chi tiết
    with st.expander("Xem bảng dữ liệu gốc"):
        st.dataframe(df_tuan)

except Exception as e:
    st.error(f"Lỗi: Hãy chắc chắn bạn đã tải file 'data_tong_hop.csv' lên GitHub. Chi tiết: {e}")
