import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Hiển thị dòng thông tin giải thích số phiếu ở đầu trang
st.info("📌 **Thông tin:** Tổng số phiếu đánh giá tối đa mỗi tuần là 17 phiếu (6 phiếu Nhóm TT + 6 phiếu VPDA + 5 phiếu McK).")

file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

# THỨ TỰ TÊN CỐ ĐỊNH THEO YÊU CẦU CỦA SẾP (Nhóm TT trước -> Nhóm VP DA sau)
fixed_names = [
    "Nguyễn Tuấn Vinh", "Trần Trang Thảo", "Lưu Hoàng Minh", "Nguyễn Lê Huy", "Mai Việt Dũng",
    "Trần Quý Giáp", "Lê Danh Toàn", "Hoàng Ngọc Bích", "Đỗ Trung Hiếu", "Đỗ Thành Long"
]

try:
    all_sheets = load_data()
    sheet_options = ["Tổng hợp tất cả các tuần"] + list(all_sheets.keys())
    selected_option = st.sidebar.selectbox("Chu kỳ đánh giá:", sheet_options)
    
    if selected_option == "Tổng hợp tất cả các tuần":
        # Logic gộp dữ liệu
        df_list = []
        for name, sheet in all_sheets.items():
            clean_sheet = sheet.loc[:, ~sheet.columns.str.contains('^Unnamed')].dropna(how='all')
            df_list.append(clean_sheet)
        
        df_raw = pd.concat(df_list, ignore_index=True)
        col_tieu_chi = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        df_long = df_long.groupby([col_tieu_chi, 'Thành viên'], as_index=False)['Điểm'].sum()
        
        df_display = df_long.pivot_table(index=col_tieu_chi, columns='Thành viên', values='Điểm', aggfunc='sum').reset_index()
        cows = df_long[col_tieu_chi].unique().tolist()
        
        # Ở tab Tổng hợp, mức max của trục Y = 17 * tổng số tuần đang có
        max_y = 17 * len(all_sheets)
    else:
        # Chế độ xem từng tuần
        df_raw = all_sheets[selected_option]
        df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')].dropna(how='all')
        col_tieu_chi = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        df_display = df_raw.copy()
        cows = df_raw[col_tieu_chi].unique().tolist()
        
        # Mức max của trục Y cho từng tuần là 17
        max_y = 17

    # SẮP XẾP LẠI THỨ TỰ CỘT TRONG BẢNG SỐ LIỆU CHI TIẾT THEO FIXED_NAMES
    match_cols = [col for col in fixed_names if col in df_display.columns]
    other_cols = [col for col in df_display.columns if col != col_tieu_chi and col not in fixed_names]
    df_display = df_display[[col_tieu_chi] + match_cols + other_cols]

    def chart(tieu_chi_list, color):
        data = df_long[df_long[col_tieu_chi].isin(tieu_chi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        c = alt.Chart(data).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', scale=alt.Scale(domain=[0, max_y]), axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        st.altair_chart(c, use_container_width=True)

    if len(cows) > 0:
        st.subheader("1️⃣ Tiêu chí 01")
