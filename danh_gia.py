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
    
    # Làm sạch tên cột và tìm cột Thành viên
    df.columns = df.columns.str.strip()
    cols = df.columns.tolist()
    col_thanh_vien = [c for c in cols if 'Thành viên' in str(c)][0]
    
    # Chuyển đổi dữ liệu sang dạng dài để vẽ biểu đồ Altair
    df_melted = df.melt(id_vars=[col_thanh_vien], var_name='Câu hỏi', value_name='Điểm')
    
    st.header(f"Dữ liệu: {selected_sheet}")
    
    # Vẽ biểu đồ thanh ngang
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Điểm:Q', title='Điểm số'),
        y=alt.Y(f'{col_thanh_vien}:N', title='Thành viên', sort='-x'),
        color='Câu hỏi:N',
        tooltip=[col_thanh_vien, 'Câu hỏi', 'Điểm']
    ).properties(height=500)
    
    st.altair_chart(chart, use_container_width=True)
    
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Hãy đảm bảo Sheet của bạn có cột tên là 'Thành viên'.")
