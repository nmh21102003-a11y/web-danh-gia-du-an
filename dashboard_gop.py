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

# Hàm tự động cắt ngắn tên sheet, chỉ lấy phần "Tuần X"
def get_short_week_name(sheet_name):
    if "Phiếu Đánh Giá " in sheet_name:
        return sheet_name.split("Phiếu Đánh Giá ")[-1].strip()
    return sheet_name.strip()

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
    width_per_bar = 80 if is_week_view else 120 # Tab 2 thu gọn lại một chút vì tên tuần giờ đã rất ngắn
    chart_width = max(800, unique_x * width_per_bar)
    
    chart = alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X(f'{x_axis_title}:N', 
                sort=fixed_names if is_week_view else None,
                axis=alt.Axis(
                    labelAngle=0, 
                    labelOverlap=False, 
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
    
    tab1, tab2 = st.tabs(["📅 Đ
