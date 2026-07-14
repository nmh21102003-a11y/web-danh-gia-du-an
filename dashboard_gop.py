import streamlit as st
import pandas as pd
import altair as alt
import datetime
import re

st.set_page_config(layout="wide")
st.title("📊 Bảng tổng hợp đánh giá nội bộ")

st.info("📌 **Ghi chú:** 17 phiếu/tuần. Tiêu chí 1 & 2: Đóng góp. Tiêu chí 3 & 4: Cảnh báo.")

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
    if not df.empty:
        tc_col = df.columns[0]
        df[tc_col] = df[tc_col].apply(lambda x: str(x).strip() + "." if "Tiêu chí 04" in str(x) and not str(x).strip().endswith(".") else x)
    return df

def get_display_name(sheet_name):
    name = sheet_name.strip()
    clean_name = name.replace("Phiếu Đánh Giá ", "")
    if "Pre-work" in clean_name or "Tuần 1" in clean_name:
        return f"{clean_name} (22/6 - 07/7/2026)"
    match = re.search(r'Tuần\s*(\d+)', clean_name)
    if match:
        n = int(match.group(1))
        base_date = datetime.date(2026, 7, 7)
        start = base_date + datetime.timedelta(days=1 + (n - 2) * 7)
        end = start + datetime.timedelta(days=6)
        return f"{clean_name} ({start.day:02d}/{start.month} - {end.day:02d}/{end.month}/2026)"
    return name

def plot_grouped_chart(df_long, col_tc, list_cows, x_axis_title="Thành viên"):
    df_chart = df_long.copy()
    
    # Logic âm dương
    if len(list_cows) >= 4:
        df_chart.loc[df_chart[col_tc].isin(list_cows[2:]), 'Điểm'] *= -1
    
    custom_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    
    # Biểu đồ cột nhóm (Grouped Bar)
    chart = alt.Chart(df_chart).encode(
        x=alt.X(f'{x_axis_title}:N', sort=fixed_names if x_axis_title=="Thành viên" else None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Điểm:Q', title="Điểm đánh giá"),
        color=alt.Color(f'{col_tc}:N', scale=alt.Scale(domain=list_cows, range=custom_colors)),
        column=alt.Column(f'{x_axis_title}:N', sort=fixed_names if x_axis_title=="Thành viên" else None, header=alt.Header(titleOrient='bottom', labelOrient='bottom'))
    )
    
    bars = chart.mark_bar(size=25)
    text = chart.mark_text(dy=-5, color='black', size=10).encode(text=alt.condition(alt.datum.Điểm != 0, 'Điểm:Q', alt.value('')))
    
    return (bars + text).properties(height=400).interactive()

try:
    all_sheets = load_data()
    first_sheet = list(all_sheets.values())[0]
    global_cows = clean_sheet(first_sheet).iloc[:, 0].unique().tolist()
    
    tab1, tab2 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cá Nhân Theo Tuần"])
    
    with tab1:
        week_options = {get_display_name(k): k for k in all_sheets.keys()}
        selected_display = st.selectbox("Chọn Tuần:", list(week_options.keys()))
        df_raw = clean_sheet(all_sheets[week_options[selected_display]])
        col_tc = df_raw.columns[0]
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        st.altair_chart(plot_grouped_chart(df_long, col_tc, global_cows), use_container_width=True)
    
    with tab2:
        member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_m = clean_sheet(sheet).melt(id_vars=[clean_sheet(sheet).columns[0]], var_name='Thành viên', value_name='Điểm')
            for _, row in df_m[df_m['Thành viên'] == member].iterrows():
                trend_data.append({'Tuần': week_name.replace("Phiếu Đánh Giá ", ""), col_tc: row[col_tc], 'Điểm': row['Điểm']})
        
        df_trend = pd.DataFrame(trend_data)
        if not df_trend.empty:
            st.altair_chart(plot_grouped_chart(df_trend, col_tc, global_cows, x_axis_title="Tuần"), use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
