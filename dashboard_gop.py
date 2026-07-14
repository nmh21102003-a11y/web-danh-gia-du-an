import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Bảng tổng hợp đánh giá nội bộ")

# Ghi chú nguồn phiếu
st.info("📌 **Ghi chú:** Tổng số phiếu đánh giá tối đa mỗi tuần là 17 phiếu (bao gồm 06 phiếu của nhóm thường trực dự án, 06 phiếu của nhóm văn phòng dự án, 05 phiếu của team McKinsey). Tiêu chí 1 & 2: Tiêu chí đóng góp. Tiêu chí 3 & 4: Tiêu chí cảnh báo.")

file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

fixed_names = [
    "Nguyễn Tuấn Vinh", "Trần Trang Thảo", "Lưu Hoàng Minh", "Nguyễn Lê Huy", "Mai Việt Dũng",
    "Trần Quý Giáp", "Lê Danh Toàn", "Hoàng Ngọc Bích", "Đỗ Trung Hiếu", "Đỗ Thành Long"
]

def clean_sheet(sheet):
    df = sheet.loc[:, ~sheet.columns.str.contains('^Unnamed')].dropna(how='all')
    df.columns = df.columns.str.replace('\n', ' ').str.replace('\r', '').str.strip()
    return df

# Hàm vẽ biểu đồ
def plot_stacked_chart(df_long, col_tc, x_axis_title="Thành viên", is_week_view=True):
    df_chart = df_long.copy()
    
    # Logic âm dương (2 cuối là cảnh báo)
    cows = df_chart[col_tc].unique()
    if len(cows) >= 4:
        tieu_cuc = cows[2:]
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm'] *= -1
    
    custom_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    
    # Tính toán chiều rộng để tạo thanh cuộn ngang
    unique_x = len(df_chart[x_axis_title].unique())
    width_per_bar = 80 if is_week_view else 150 # Tab 2 (theo tuần) rộng hơn để không bị khít
    chart_width = max(800, unique_x * width_per_bar)
    
    # Xoay chữ trục X 45 độ ở Tab 2 để không bị đè lên nhau
    x_angle = 0 if is_week_view else -45
    
    return alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X(f'{x_axis_title}:N', 
                sort=fixed_names if is_week_view else None,
                axis=alt.Axis(labelAngle=x_angle, labelOverlap=False)), # labelOverlap=False Ép hiện 100% chữ
        y=alt.Y('Điểm:Q', title="Số phiếu"),
        color=alt.Color(f'{col_tc}:N', 
                        scale=alt.Scale(range=custom_colors), 
                        legend=alt.Legend(title="Tiêu chí", orient='bottom', direction='vertical', labelLimit=1000)),
        tooltip=[x_axis_title, col_tc, 'Điểm']
    ).properties(width=chart_width, height=500).interactive()

try:
    all_sheets = load_data()
    tab1, tab2 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cá Nhân Theo Tuần"])
    
    with tab1:
        selected_week = st.selectbox("Chọn Tuần:", list(all_sheets.keys()))
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        st.altair_chart(plot_stacked_chart(df_long, col_tc, x_axis_title="Thành viên", is_week_view=True), use_container_width=True)
        with st.expander("📋 Số liệu chi tiết"): st.dataframe(df_raw, use_container_width=True)

    with tab2:
        selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_clean = clean_sheet(sheet)
            tc_col = df_clean.columns[0]
            df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
            df_mem = df_m[df_m['Thành viên'] == selected_member]
            for _, row in df_mem.iterrows():
                trend_data.append({'Tuần': week_name, tc_col: row[tc_col], 'Điểm': row['Điểm']})
        
        df_trend = pd.DataFrame(trend_data)
        if not df_trend.empty:
            tc_col = df_trend.columns[1]
            
            # Quan trọng: Đặt use_container_width=False để thanh kéo ngang hoạt động
            st.altair_chart(plot_stacked_chart(df_trend, tc_col, x_axis_title="Tuần", is_week_view=False), use_container_width=False)
        else:
            st.warning("Chưa có dữ liệu cho thành viên này.")

except Exception as e:
    st.error(f"Lỗi: {e}")
