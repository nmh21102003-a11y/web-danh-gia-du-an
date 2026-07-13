import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Đánh giá dự án", layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp")

@st.cache_data
def load_data():
    # Đọc file với encoding utf-8-sig để hỗ trợ tiếng Việt có dấu
    df = pd.read_csv("data_tong_hop.csv", encoding='utf-8-sig')
    # Làm sạch tên cột: xóa khoảng trắng, đổi tên về chuẩn
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    
    # Tìm cột Tuần (chấp nhận cả 'Tuần' hoặc 'Tuan')
    tuan_col = [c for c in df.columns if 'Tuan' in c or 'Tuần' in c][0]
    
    tuan_list = df[tuan_col].unique()
    selected_tuan = st.sidebar.selectbox("Chọn tuần cần xem:", tuan_list)
    
    df_tuan = df[df[tuan_col] == selected_tuan]
    st.header(f"Dữ liệu: {selected_tuan}")
    
    # Biểu đồ
    st.subheader("So sánh kết quả các Thành viên")
    chart = alt.Chart(df_tuan).mark_bar().encode(
        x=alt.X('Câu 1: Ai là người giúp đỡ, hỗ trợ bạn nhiều nhất trong thời gian vừa qua?', title='Điểm số'),
        y=alt.Y('Thành viên', sort='-x', title=''),
        color='Thành viên',
        tooltip=['Thành viên', 'Câu 1: Ai là người giúp đỡ, hỗ trợ bạn nhiều nhất trong thời gian vừa qua?']
    ).properties(height=400)
    
    st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Hãy kiểm tra lại file CSV của bạn đã có cột 'Tuần' và 'Thành viên' chưa.")
