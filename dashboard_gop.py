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

# Hàm xử lý ngắt dòng thông minh cho tên Tuần dài
def format_week_name(name):
    if " - " in name:
        return name.replace(" - ", " ~ ")
    elif "Phiếu Đánh Giá " in name:
        return name.replace("Phiếu Đánh Giá ", "Phiếu Đánh Giá ~ ")
    elif "Tuần" in name and " " in name:
        return name.replace("Tuần", "~ Tuần")
    else:
        words = name.split()
        if len(words) > 2:
            mid = len(words)//2
            return " ".join(words[:mid]) + " ~ " + " ".join(words[mid:])
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
    width_per_bar = 80 if is_week_view else 150 
    chart_width = max(800, unique_x * width_per_bar)
    
    return alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X(f'{x_axis_title}:N', 
                sort=fixed_names if is_week_view else None,
                axis=alt.Axis(
                    labelAngle=0, 
                    labelOverlap=False, 
                    labelExpr="split(datum.value, ' ~ ')" # Tự động xuống dòng tại ký hiệu ~
                )),
        y=alt.Y('Điểm:Q', title="Số phiếu"),
        color=alt.Color(f'{col_tc}:N', 
                        scale=alt.Scale(domain=list_cows, range=custom_colors), # Cố định domain để không bao giờ mất tiêu chí & sai màu
                        legend=alt.Legend(title="Tiêu chí đánh giá", orient='bottom', direction='vertical', labelLimit=1000)),
        tooltip=[x_axis_title, col_tc, 'Điểm']
    ).properties(width=chart_width, height=500).interactive()

try:
    all_sheets = load_data()
    
    # Lấy danh sách tiêu chí chuẩn toàn cục (Đảm bảo chú thích luôn đầy đủ)
    first_sheet = list(all_sheets.values())[0]
    df_first = clean_sheet(first_sheet)
    col_tc_global = df_first.columns[0]
    global_cows = df_first[col_tc_global].unique().tolist()
    
    tab1, tab2 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cá Nhân Theo Tuần"])
    
    # 1. TAB ĐÁNH GIÁ TỪNG TUẦN
    with tab1:
        selected_week = st.selectbox("Chọn Tuần:", list(all_sheets.keys()))
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
            df_clean = clean_sheet(sheet
