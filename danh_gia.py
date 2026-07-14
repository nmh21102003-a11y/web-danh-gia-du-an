import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Dòng thông tin
st.info("📌 **Thông tin:** Tổng số phiếu đánh giá tối đa mỗi tuần là 17 phiếu (6 phiếu Nhóm thường trực dự án + 6 phiếu Văn phòng dự án + 5 phiếu McKinsey).")

file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

# THỨ TỰ TÊN CỐ ĐỊNH THEO YÊU CẦU CỦA SẾP
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
            clean_sheet.columns = clean_sheet.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
            df_list.append(clean_sheet)
        
        df_raw = pd.concat(df_list, ignore_index=True)
        col_tieu_chi = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
        df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        df_long = df_long.groupby([col_tieu_chi, 'Thành viên'], as_index=False)['Điểm'].sum()
        
        df_display = df_long.pivot_table(index=col_tieu_chi, columns='Thành viên', values='Điểm', aggfunc='sum').reset_index()
        cows = df_long[col_tieu_chi].unique().tolist()
        
        max_y = 17 * len(all_sheets)
    else:
        # Chế độ xem từng tuần
        df_raw = all_sheets[selected_option]
        df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')].dropna(how='all')
        df_raw.columns = df_raw.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
        col_tieu_chi = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
        df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        df_display = df_raw.copy()
        cows = df_raw[col_tieu_chi].unique().tolist()
        
        max_y = 17

    match_cols = [col for col in fixed_names if col in df_display.columns]
    other_cols = [col for col in df_display.columns if col != col_tieu_chi and col not in fixed_names]
    df_display = df_display[[col_tieu_chi] + match_cols + other_cols]

    def chart(tieu_chi_list, color):
        data = df_long[df_long[col_tieu_chi].isin(tieu_chi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        # Mở khóa zoom + Bật clip gọt viền + Ép chân gốc 0
        c = alt.Chart(data).mark_bar(size=40, clip=True).encode(
            x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', 
                    scale=alt.Scale(domainMin=0, domainMax=max_y, clamp=True), 
                    axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        
        st.altair_chart(c, use_container_width=True)

    if len(cows) > 0:
        st.subheader("1️⃣ Tiêu chí 01")
        st.caption(f"{cows[0]}")
        chart([cows[0]], '#3498db')
        
    if len(cows) > 1:
        st.subheader("2️⃣ Tiêu chí 02")
        st.caption(f"{cows[1]}")
        chart([cows[1]], '#3498db')
        
    if len(cows) > 2:
        st.subheader("3️⃣ Tiêu chí 03")
        st.caption(f"{cows[2]}")
        chart([cows[2]], '#e74c3c')

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df_display, use_container_width=True, height=300)

except Exception as e:
    st.error(f"Đang tải dữ liệu, vui lòng đợi hoặc kiểm tra file: {e}")
