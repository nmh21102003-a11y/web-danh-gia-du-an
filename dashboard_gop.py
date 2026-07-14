import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Thông tin tổng số phiếu
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

# Hàm hỗ trợ làm sạch dữ liệu
def clean_sheet(sheet):
    df = sheet.loc[:, ~sheet.columns.str.contains('^Unnamed')].dropna(how='all')
    df.columns = df.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
    return df

# Hàm hỗ trợ vẽ biểu đồ cột chồng (Âm - Dương)
def plot_stacked_chart(df_long, list_cows, col_tieu_chi, is_tong_hop=False):
    df_chart = df_long.copy()
    
    # Tạo một cột điểm riêng cho biểu đồ (để chứa giá trị âm)
    df_chart['Điểm Biểu Đồ'] = df_chart['Điểm']
    
    # Từ tiêu chí thứ 3 trở đi sẽ bị nhân với -1 (biến thành thanh âm lộn xuống dưới)
    if len(list_cows) > 2:
        tieu_cuc = list_cows[2:]
        df_chart.loc[df_chart[col_tieu_chi].isin(tieu_cuc), 'Điểm Biểu Đồ'] *= -1
    
    # 4 Màu quy định: Xanh dương (TC1), Xanh lá (TC2) | Đỏ (TC3), Cam (TC4)
    range_colors = ['#3498db', '#2ecc71', '#e74c3c', '#e67e22'][:len(list_cows)]
    
    title_y = "Tổng Điểm Tích Lũy" if is_tong_hop else "Điểm Đánh Giá (Tuần)"

    c = alt.Chart(df_chart).mark_bar(size=45).encode(
        x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0, title="Thành viên")),
        # Trục Y tự động co giãn theo giá trị thực tế của cột chồng
        y=alt.Y('Điểm Biểu Đồ:Q', axis=alt.Axis(format="d", tickMinStep=1, title=title_y)),
        color=alt.Color(f'{col_tieu_chi}:N', 
                        scale=alt.Scale(domain=list_cows, range=range_colors), 
                        legend=alt.Legend(title="Các Tiêu Chí", orient='bottom', direction='vertical', labelLimit=800)),
        # Tooltip: Dù biểu đồ hiện số âm, khi di chuột vào vẫn hiện ĐIỂM THỰC TẾ (số dương) để sếp dễ đọc
        tooltip=[
            alt.Tooltip('Thành viên:N', title='Tên'),
            alt.Tooltip(f'{col_tieu_chi}:N', title='Tiêu chí'),
            alt.Tooltip('Điểm:Q', title='Số phiếu thực tế')
        ]
    ).properties(height=500).interactive()
    
    return c

try:
    all_sheets = load_data()
    
    # --- LOGIC TỰ ĐỘNG THÊM TAB KHI CÓ TỪ 2 TUẦN TRỞ LÊN ---
    if len(all_sheets) > 1:
        # Nếu có từ 2 sheet trở lên, hệ thống tự động chẻ làm 2 Tab đúng ý sếp
        tab1, tab2 = st.tabs(["📅 Bảng Đánh Giá Từng Tuần", "📈 Bảng Tổng Hợp Cả Quá Trình"])
        
        # TAB 1: XEM TỪNG TUẦN
        with tab1:
            selected_week = st.selectbox("📌 Chọn Tuần cần xem:", list(all_sheets.keys()))
            df_raw = clean_sheet(all_sheets[selected_week])
            col_tc = df_raw.columns[0]
            
            df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
            df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
            df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
            
            cows = df_raw[col_tc].unique().tolist()
            
            st.altair_chart(plot_stacked_chart(df_long, cows, col_tc), use_container_width=True)
            
            df_display = df_raw.copy()
            match_cols = [c for c in fixed_names if c in df_display.columns]
            other_cols = [c for c in df_display.columns if c != col_tc and c not in fixed_names]
            with st.expander("📋 Số liệu chi tiết"):
                st.dataframe(df_display[[col_tc] + match_cols + other_cols], use_container_width=True, height=200)
                
        # TAB 2: TỔNG HỢP CẢ QUÁ TRÌNH
        with tab2:
            st.subheader("Trực quan hóa Dữ liệu Tổng hợp qua các tuần")
            df_list = [clean_sheet(sheet) for sheet in all_sheets.values()]
            df_agg_raw = pd.concat(df_list, ignore_index=True)
            col_tc_agg = df_agg_raw.columns[0]
            
            df_agg_long = df_agg_raw.melt(id_vars=[col_tc_agg], var_name='Thành viên', value_name='Điểm')
            df_agg_long['Thành viên'] = df_agg_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
            df_agg_long['Điểm'] = pd.to_numeric(df_agg_long['Điểm'], errors='coerce').fillna(0)
            df_agg_long = df_agg_long.groupby([col_tc_agg, 'Thành viên'], as_index=False)['Điểm'].sum()
            
            cows_agg = df_agg_long[col_tc_agg].unique().tolist()
            
            st.altair_chart(plot_stacked_chart(df_agg_long, cows_agg, col_tc_agg, is_tong_hop=True), use_container_width=True)
            
            df_agg_display = df_agg_long.pivot_table(index=col_tc_agg, columns='Thành viên', values='Điểm', aggfunc='sum').reset_index()
            match_cols = [c for c in fixed_names if c in df_agg_display.columns]
            other_cols = [c for c in df_agg_display.columns if c != col_tc_agg and c not in fixed_names]
            with st.expander("📋 Số liệu chi tiết"):
                st.dataframe(df_agg_display[[col_tc_agg] + match_cols + other_cols], use_container_width=True, height=200)

    else:
        # Nếu chỉ có 1 Tuần duy nhất, hệ thống ẩn Tab đi và chỉ hiện 1 bảng chung
        st.subheader("Bảng Đánh Giá Tuần (Cột Chồng)")
        selected_week = list(all_sheets.keys())[0]
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        cows = df_raw[col_tc].unique().tolist()
        
        st.altair_chart(plot_stacked_chart(df_long, cows, col_tc), use_container_width=True)
        
        df_display = df_raw.copy()
        match_cols = [c for c in fixed_names if c in df_display.columns]
        other_cols = [c for c in df_display.columns if c != col_tc and c not in fixed_names]
        with st.expander("📋 Số liệu chi tiết"):
            st.dataframe(df_display[[col_tc] + match_cols + other_cols], use_container_width=True, height=200)

except Exception as e:
    st.error(f"Đang tải dữ liệu, vui lòng đợi hoặc kiểm tra file: {e}")
