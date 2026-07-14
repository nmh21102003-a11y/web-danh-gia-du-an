import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📈 Dashboard Đánh Giá Tổng Hợp Năng Lực Dự Án")

# Dữ liệu nguồn
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

# Hàm vẽ biểu đồ với logic 4 tiêu chí (2 đầu dương, 2 cuối âm)
def plot_stacked_chart(df_long, list_cows, col_tc):
    df_chart = df_long.copy()
    # Logic: Tiêu chí 3 và 4 (vị trí index 2, 3) sẽ hiển thị số âm
    if len(list_cows) >= 4:
        tieu_cuc = list_cows[2:] # Lấy từ tiêu chí 3 trở đi
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm'] *= -1
    
    return alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Điểm:Q', title="Số phiếu (Dương: Tốt | Âm: Cảnh báo)"),
        color=alt.Color(f'{col_tc}:N', legend=alt.Legend(title="4 Tiêu chí", orient='bottom', labelLimit=800)),
        tooltip=['Thành viên', f'{col_tc}', 'Điểm']
    ).properties(height=500).interactive()

try:
    all_sheets = load_data()
    tab1, tab2, tab3 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cả Quá Trình", "👤 Xu Hướng Cá Nhân"])
    
    note_text = "📌 **Ghi chú:** 2 tiêu chí đầu là Đóng góp (Dương), 2 tiêu chí cuối là Cảnh báo (Âm). Tối đa 17 phiếu/thành viên/tuần."

    with tab1:
        selected_week = st.selectbox("Chọn Tuần:", list(all_sheets.keys()))
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        st.altair_chart(plot_stacked_chart(df_long, df_raw[col_tc].unique().tolist(), col_tc), use_container_width=True)
        st.info(note_text)
        with st.expander("Số liệu chi tiết"): st.dataframe(df_raw, use_container_width=True)
            
    with tab2:
        df_list = [clean_sheet(sheet) for sheet in all_sheets.values()]
        df_agg_raw = pd.concat(df_list, ignore_index=True)
        col_tc_agg = df_agg_raw.columns[0]
        df_agg_long = df_agg_raw.melt(id_vars=[col_tc_agg], var_name='Thành viên', value_name='Điểm')
        df_agg_long['Điểm'] = pd.to_numeric(df_agg_long['Điểm'], errors='coerce').fillna(0)
        df_agg_grouped = df_agg_long.groupby([col_tc_agg, 'Thành viên'], as_index=False)['Điểm'].sum()
        st.altair_chart(plot_stacked_chart(df_agg_grouped, df_agg_grouped[col_tc_agg].unique().tolist(), col_tc_agg), use_container_width=True)
        st.info(note_text)
        with st.expander("Số liệu tổng hợp"): st.dataframe(df_agg_grouped.pivot_table(index=col_tc_agg, columns='Thành viên', values='Điểm', aggfunc='sum'), use_container_width=True)

    with tab3:
        st.subheader("Bức tranh phong độ: Đóng góp (Cột) & Cảnh báo (Đường)")
        selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_clean = clean_sheet(sheet)
            tc_col = df_clean.columns[0]
            df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
            df_mem = df_m[df_m['Thành viên'] == selected_member]
            cows_list = df_m[tc_col].unique()
            # Pos: 2 tiêu chí đầu, Neg: 2 tiêu chí cuối
            pos = df_mem[df_mem[tc_col].isin(cows_list[:2])]['Điểm'].sum()
            neg = df_mem[df_mem[tc_col].isin(cows_list[2:])]['Điểm'].sum() if len(cows_list) >= 4 else 0
            trend_data.append({'Tuần': week_name, 'Đóng góp (Tốt)': pos, 'Cảnh báo (Xấu)': neg})
        
        df_trend = pd.DataFrame(trend_data)
        base = alt.Chart(df_trend).encode(x=alt.X('Tuần:N', title="Chu kỳ tuần", axis=alt.Axis(labelAngle=0)))
        bar = base.mark_bar(color='#2ecc71', opacity=0.6).encode(y=alt.Y('Đóng góp (Tốt):Q', title="Điểm"))
        line = base.mark_line(color='#e74c3c', strokeWidth=3, point=True).encode(y=alt.Y('Cảnh báo (Xấu):Q', title="Điểm"))
        st.altair_chart((bar + line).properties(height=400).interactive(), use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
