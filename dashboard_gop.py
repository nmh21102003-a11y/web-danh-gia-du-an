import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📈 Dashboard Đánh Giá Tổng Hợp Năng Lực Dự Án")

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

# HÀM VẼ BIỂU ĐỒ CỘT CHỒNG (Gọn gàng)
def plot_stacked_chart(df_long, list_cows, col_tc, is_tong_hop=False):
    df_chart = df_long.copy()
    df_chart['Điểm Biểu Đồ'] = df_chart['Điểm']
    
    if len(list_cows) > 2:
        tieu_cuc = list_cows[2:]
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm Biểu Đồ'] *= -1
        
    range_colors = ['#3498db', '#2ecc71', '#e74c3c', '#e67e22'][:len(list_cows)]
    title_y = "Tổng Điểm Tích Lũy" if is_tong_hop else "Điểm Đánh Giá (Tuần)"

    return alt.Chart(df_chart).mark_bar(size=45).encode(
        x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0, title="Thành viên")),
        y=alt.Y('Điểm Biểu Đồ:Q', axis=alt.Axis(format="d", tickMinStep=1, title=title_y)),
        color=alt.Color(f'{col_tc}:N', scale=alt.Scale(domain=list_cows, range=range_colors), 
                        legend=alt.Legend(title="Danh sách Tiêu chí", orient='bottom', direction='vertical')),
        tooltip=[
            alt.Tooltip('Thành viên:N', title='Tên'),
            alt.Tooltip(f'{col_tc}:N', title='Tiêu chí'),
            alt.Tooltip('Điểm:Q', title='Số phiếu thực tế')
        ]
    ).properties(height=500).interactive()

try:
    all_sheets = load_data()
    
    if len(all_sheets) > 1:
        tab1, tab2, tab3 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cả Quá Trình", "👤 Theo Dõi Xu Hướng Cá Nhân"])
        
        with tab1:
            selected_week = st.selectbox("📌 Chọn Tuần cần xem:", list(all_sheets.keys()))
            df_raw = clean_sheet(all_sheets[selected_week])
            col_tc = df_raw.columns[0]
            df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
            df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
            cows = df_raw[col_tc].unique().tolist()
            st.altair_chart(plot_stacked_chart(df_long, cows, col_tc), use_container_width=True)
                
        with tab2:
            df_list = [clean_sheet(sheet) for sheet in all_sheets.values()]
            df_agg_raw = pd.concat(df_list, ignore_index=True)
            col_tc_agg = df_agg_raw.columns[0]
            df_agg_long = df_agg_raw.melt(id_vars=[col_tc_agg], var_name='Thành viên', value_name='Điểm')
            df_agg_long['Điểm'] = pd.to_numeric(df_agg_long['Điểm'], errors='coerce').fillna(0)
            df_agg_long = df_agg_long.groupby([col_tc_agg, 'Thành viên'], as_index=False)['Điểm'].sum()
            cows_agg = df_agg_long[col_tc_agg].unique().tolist()
            st.altair_chart(plot_stacked_chart(df_agg_long, cows_agg, col_tc_agg, is_tong_hop=True), use_container_width=True)

        with tab3:
            selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
            trend_data = []
            for week_name, sheet in all_sheets.items():
                df_clean = clean_sheet(sheet)
                tc_col = df_clean.columns[0]
                df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
                tich_cuc = df_m[tc_col].unique()[:2].tolist()
                tieu_cuc = df_m[tc_col].unique()[2:].tolist() if len(df_m[tc_col].unique()) > 2 else []
                df_mem = df_m[df_m['Thành viên'] == selected_member]
                pos = df_mem[df_mem[tc_col].isin(tich_cuc)]['Điểm'].sum()
                neg = df_mem[df_mem[tc_col].isin(tieu_cuc)]['Điểm'].sum() if tieu_cuc else 0
                trend_data.append({'Tuần': week_name, 'Loại Điểm': 'Tích cực', 'Số phiếu': pos})
                trend_data.append({'Tuần': week_name, 'Loại Điểm': 'Tiêu cực', 'Số phiếu': -neg})
            st.altair_chart(alt.Chart(pd.DataFrame(trend_data)).mark_line(point=True).encode(
                x='Tuần:N', y='Số phiếu:Q', color='Loại Điểm:N').properties(height=400).interactive(), use_container_width=True)
    else:
        selected_week = list(all_sheets.keys())[0]
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        st.altair_chart(plot_stacked_chart(df_long, df_raw[col_tc].unique().tolist(), col_tc), use_container_width=True)

except Exception as e:
    st.error(f"Đang tải dữ liệu: {e}")
