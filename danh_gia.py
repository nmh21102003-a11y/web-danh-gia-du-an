import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp Theo Tuần")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_all_sheets():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_all_sheets()
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", sheet_names)
    
    df = all_sheets[selected_sheet]
    
    # Làm sạch tên cột
    df.columns = df.columns.astype(str).str.strip()
    
    # --- ĐOẠN SỬA ĐỂ KHÔNG BAO GIỜ LỖI ---
    # Tự tìm cột có chữ "Thành viên", nếu không thấy thì lấy cột đầu tiên
    col_thanh_vien = next((c for c in df.columns if 'Thành viên' in c), df.columns[0])
    
    # Chuyển dữ liệu (Melt) để vẽ biểu đồ
    df_melted = df.melt(id_vars=[col_thanh_vien], var_name='Câu hỏi', value_name='Điểm')
    
    st.header(f"Dữ liệu: {selected_sheet}")
    
    # Vẽ biểu đồ thanh ngang
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Điểm:Q', title='Điểm số'),
        y=alt.Y(f'{col_thanh_vien}:N', title='Thành viên', sort='-x'),
        color='Câu hỏi:N',
        tooltip=[col_thanh_vien, 'Câu hỏi', 'Điểm']
    ).properties(height=500)
    
    # Hiển thị biểu đồ với width='stretch' để sửa cảnh báo
    st.altair_chart(chart, use_container_width=True)
    
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra lại file Excel của bạn đã được tải lên đúng chưa.")
    st.write("Gợi ý: Đảm bảo dòng đầu tiên trong Sheet là tên các cột.")
