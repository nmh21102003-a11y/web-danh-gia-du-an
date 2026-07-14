import streamlit as st
import pandas as pd
import altair as alt
import datetime
import re

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

# Hàm 1: Tự động tính ngày dành cho hộp chọn ở Tab 1
def get_display_name(sheet_name):
    name = sheet_name.strip()
    clean_name = name
    if "Phiếu Đánh Giá" in name:
        clean_name = "Phiếu Đánh Giá " + name.split("Phiếu Đánh Giá")[-1].strip()

    if "Pre-work" in clean_name or "Tuần 1" in clean_name:
        return f"{clean_name} (từ ngày 22/6/2026 đến ngày 07/7/2026)"
    
    match = re.search(r'Tuần\s*(\d+)', clean_name)
    if match:
        n = int(match.group(1))
        if n >= 2:
            base_end_date = datetime.date(2026, 7, 7)
            start_date = base_end_date + datetime.timedelta(days=1 + (n - 2) * 7)
            end_date = start_date + datetime.timedelta(days=6)
            def format_dt(dt):
                return f"{dt.day:02d}/{dt.month}/{dt.year}" # Thêm số 0 nếu ngày < 10
            return f"{clean_name} (từ ngày {format_dt(start_date)} đến ngày {format_dt(end_date)})"
            
    return clean_name

# Hàm 2: Rút gọn và ngắt dòng trục X dành cho Tab 2
def get_split_week_name(sheet_name):
    name = sheet_name.strip()
    if "Phiếu Đánh Giá" in name:
        suffix = name.split("Phiếu Đánh Giá")[-1].strip()
        return f"Phiếu Đánh Giá ~ {suffix}"
    return name

# Hàm vẽ biểu đồ với CỐ ĐỊNH màu và tiêu chí
def plot_stacked_chart(df_long, col_tc, list_cows, x_axis_title="Thành viên", is_week_view=True):
    df_chart = df_long.copy()
    
    # Logic âm dương
    if len(list_cows) >= 4:
        tieu_cuc = list_cows[2:]
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm'] *= -1
    
    custom_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    
    # Tính toán chiều rộng để thanh cuộn hoạt động tốt
    unique_x = len(df_chart[x_axis_title].unique())
    width_per_bar = 80 if is_week_view else 140 # Tab 2 rộng hơn chút để hiển thị chữ thoải mái
    chart_width = max(800, unique_x * width_per_bar)
    
    chart = alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X(f'{x_axis_title}:N', 
                sort=fixed_names if is_week_view else None,
                axis=alt.Axis(
                    labelAngle=0, 
                    labelOverlap=False,
                    labelExpr="split(datum.value, ' ~ ')", # Tách chữ xuống dòng tại dấu ~
                    domain=False, 
                    ticks=False   
                )),
        y=alt.Y('Điểm:Q', 
                title="Số phiếu",
                scale=alt.Scale(nice=False)), # Ép trục Y cắt bỏ khoảng trống thừa để số 0 sát tên trục X
        color=alt.Color(f'{col_tc}:N', 
                        scale=alt.Scale(domain=list_cows, range=custom_colors), 
                        legend=alt.Legend(title="Tiêu chí đánh giá", orient='bottom', direction='vertical', labelLimit=1000)),
        tooltip=[x_axis_title, col_tc, 'Điểm']
    ).properties(width=chart_width, height=500)
    
    # Kẻ một đường chuẩn (baseline) màu đen tại mốc 0
    rule = alt.Chart(pd.DataFrame({'Điểm': [0]})).mark_rule(color='#333333', strokeWidth=2).encode(
        y='Điểm:Q'
    )
    
    return (chart + rule).interactive()

try:
    all_sheets = load_data()
    
    # Lấy danh sách tiêu chí chuẩn toàn cục
    first_sheet = list(all_sheets.values())[0]
    df_first = clean_sheet(first_sheet)
    col_tc_global = df_first.columns[0]
    global_cows = df_first[col_tc_global].unique().tolist()
    
    tab1, tab2 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cá Nhân Theo Tuần"])
    
    # 1. TAB ĐÁNH GIÁ TỪNG TUẦN
    with tab1:
        # Sử dụng hàm có ngày tháng cho hộp chọn (Dropdown)
        week_options = {get_display_name(k): k for k in all_sheets.keys()}
        selected_display_week = st.selectbox("Chọn Tuần:", list(week_options.keys()))
        selected_week = week_options[selected_display_week]
        
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        st.altair_chart(plot_stacked_chart(df_long, col_tc, global_cows, x_axis_title="Thành viên", is_week_view=True), use_container_width=True)
        with st.expander("📋 Số liệu chi tiết"): st.dataframe(df_raw, use_container_width=True)

    # 2. TAB TỔNG HỢP CÁ NHÂN THEO TUẦN
    with tab2:
        selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_clean = clean_sheet(sheet)
            tc_col = df_clean.columns[0]
            df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
            df_mem = df_m[df_m['Thành viên'] == selected_member]
            
            # Sử dụng hàm ngắt dòng (không ngày tháng) cho trục X của Tab 2
            display_week = get_split_week_name(week_name)
            
            for _, row in df_mem.iterrows():
                trend_data.append({'Tuần': display_week, tc_col: row[tc_col], 'Điểm': row['Điểm']})
        
        df_trend = pd.DataFrame(trend_data)
        if not df_trend.empty:
            tc_col = df_trend.columns[1]
            # use_container_width=False để thanh trượt ngang hoạt động khi số tuần tăng lên
            st.altair_chart(plot_stacked_chart(df_trend, tc_col, global_cows, x_axis_title="Tuần", is_week_view=False), use_container_width=False)
        else:
            st.warning("Chưa có dữ liệu cho thành viên này.")

except Exception as e:
    st.error(f"Lỗi: {e}")
