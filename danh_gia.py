import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_all_sheets():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_all_sheets()
    sheet_names = list(all_sheets.keys())
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", sheet_names)
    
    df = all_sheets[selected_sheet]
    df.columns = df.columns.astype(str).str.strip()
    
    # Ép kiểu dữ liệu để tránh lỗi 'ArrowTypeError'
    # Chúng ta chuyển tất cả các cột điểm về dạng số, nếu lỗi thì biến thành 0
    for col in df.columns:
        if 'Điểm' in col or 'Câu' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Tìm cột Thành viên
    col_thanh_vien = next((c for c in df.columns if 'Thành viên' in c), df.columns[0])
    
    # Vẽ biểu đồ
    df_melted = df.melt(id_vars=[col_thanh_vien], var_name='Câu hỏi', value_name='Điểm')
    
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('Điểm:Q', title='Điểm số'),
        y=alt.Y(f'{col_thanh_vien}:N', title='Thành viên', sort='-x'),
        color='Câu hỏi:N',
        tooltip=[col_thanh_vien, 'Câu hỏi', 'Điểm']
    ).properties(height=500).configure_axis(grid=False)
    
    st.altair_chart(chart, width='stretch')
    
    with st.expander("Xem dữ liệu"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra lại cấu trúc file Excel.")
