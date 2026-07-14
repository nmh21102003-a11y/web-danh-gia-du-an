import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📈 Dashboard Đánh Giá Tổng Hợp Năng Lực Dự Án")

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

# 1️⃣ HÀM TẠO THẺ KPI (CHỈ SỐ NỔI BẬT)
def render_kpi_cards(df_long, list_cows, col_tc):
    tich_cuc = list_cows[:2]
    tieu_cuc = list_cows[2:] if len(list_cows) > 2 else []
    
    df_pos = df_long[df_long[col_tc].isin(tich_cuc)].groupby('Thành viên')['Điểm'].sum()
    df_neg = df_long[df_long[col_tc].isin(tieu_cuc)].groupby('Thành viên')['Điểm'].sum() if tieu_cuc else pd.Series(dtype=float)
    
    top_star = df_pos.idxmax() if not df_pos.empty and df_pos.max() > 0 else "Chưa có"
    top_star_score = int(df_pos.max()) if not df_pos.empty else 0
    
    top_alert = df_neg.idxmax() if not df_neg.empty and df_neg.max() > 0 else "Không có"
    top_alert_score = int(df_neg.max()) if not df_neg.empty else 0
    
    total_net = int(df_pos.sum() - (df_neg.sum() if not df_neg.empty else 0))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🌟 Ngôi Sao (Tích cực cao nhất)", value=top_star, delta=f"{top_star_score} phiếu tốt")
    with col2:
        st.metric(label="⚠️ Cần Lưu Ý (Tiêu cực cao nhất)", value=top_alert, delta=f"-{top_alert_score} phiếu phạt", delta_color="inverse")
    with col3:
        st.metric(label="📊 Chỉ Số Net Toàn Team", value=f"{total_net} điểm", delta="Tổng Tích Cực - Tổng Tiêu Cực")
    st.divider()

# 2️⃣ HÀM VẼ BIỂU ĐỒ CỘT CHỒNG + ĐƯỜNG TRUNG BÌNH
def plot_stacked_chart(df_long, list_cows, col_tc, is_tong_hop=False):
    df_chart = df_long.copy()
    df_chart['Điểm Biểu Đồ'] = df_chart['Điểm']
    
    if len(list_cows) > 2:
        tieu_cuc = list_cows[2:]
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm Biểu Đồ'] *= -1
        
    range_colors = ['#3498db', '#2ecc71', '#e74c3c', '#e67e22'][:len(list_cows)]
    title_y = "Tổng Điểm Tích Lũy" if is_tong_hop else "Điểm Đánh Giá (Tuần)"

    # Biểu đồ cột
    bar = alt.Chart(df_chart).mark_bar(size=45).encode(
        x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0, title="Thành viên")),
        y=alt.Y('Điểm Biểu Đồ:Q', axis=alt.Axis(format="d", tickMinStep=1, title=title_y)),
        color=alt.Color(f'{col_tc}:N', scale=alt.Scale(domain=list_cows, range=range_colors), 
                        legend=alt.Legend(title="Các Tiêu Chí", orient='bottom', direction='vertical', labelLimit=800)),
        tooltip=[
            alt.Tooltip('Thành viên:N', title='Tên'),
            alt.Tooltip(f'{col_tc}:N', title='Tiêu chí'),
            alt.Tooltip('Điểm:Q', title='Số phiếu thực tế')
        ]
    )

    # Tính đường trung bình tích cực của cả team
    tich_cuc_cows = list_cows[:2]
    avg_pos = df_chart[df_chart[col_tc].isin(tich_cuc_cows)].groupby('Thành viên')['Điểm'].sum().mean()
    rule_df = pd.DataFrame({'Trung bình Tích cực': [avg_pos]})
    
    # Vẽ Đường đứt nét (Đường Trung bình)
    rule = alt.Chart(rule_df).mark_rule(color='black', strokeDash=[5, 5], size=2).encode(
        y='Trung bình Tích cực:Q',
        tooltip=[alt.Tooltip('Trung bình Tích cực:Q', title="Điểm TB Team", format=".1f")]
    )

    return (bar + rule).properties(height=500).interactive()

try:
    all_sheets = load_data()
    
    if len(all_sheets) > 1:
        # TẠO 3 TABS KHI CÓ NHIỀU TUẦN
        tab1, tab2, tab3 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cả Quá Trình", "👤 Theo Dõi Xu Hướng Cá Nhân"])
        
        # TAB 1: XEM TỪNG TUẦN
        with tab1:
            selected_week = st.selectbox("📌 Chọn Tuần cần xem:", list(all_sheets.keys()))
            df_raw = clean_sheet(all_sheets[selected_week])
            col_tc = df_raw.columns[0]
            
            df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
            df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
            df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
            cows = df_raw[col_tc].unique().tolist()
            
            # Hiển thị KPI & Biểu đồ
            render_kpi_cards(df_long, cows, col_tc)
            st.altair_chart(plot_stacked_chart(df_long, cows, col_tc), use_container_width=True)
            
            with st.expander("📋 Số liệu chi tiết"):
                df_display = df_raw.copy()
                match_cols = [c for c in fixed_names if c in df_display.columns]
                other_cols = [c for c in df_display.columns if c != col_tc and c not in fixed_names]
                st.dataframe(df_display[[col_tc] + match_cols + other_cols], use_container_width=True, height=200)
                
        # TAB 2: TỔNG HỢP TOÀN BỘ
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
            
            render_kpi_cards(df_agg_long, cows_agg, col_tc_agg)
            st.altair_chart(plot_stacked_chart(df_agg_long, cows_agg, col_tc_agg, is_tong_hop=True), use_container_width=True)
            
            with st.expander("📋 Số liệu chi tiết"):
                df_agg_display = df_agg_long.pivot_table(index=col_tc_agg, columns='Thành viên', values='Điểm', aggfunc='sum').reset_index()
                match_cols = [c for c in fixed_names if c in df_agg_display.columns]
                other_cols = [c for c in df_agg_display.columns if c != col_tc_agg and c not in fixed_names]
                st.dataframe(df_agg_display[[col_tc_agg] + match_cols + other_cols], use_container_width=True, height=200)

        # 3️⃣ TAB 3: BIỂU ĐỒ XU HƯỚNG CÁ NHÂN (LINE CHART)
        with tab3:
            st.subheader("Biểu đồ Theo dõi Phong độ Cá nhân")
            selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
            
            trend_data = []
            for week_name, sheet in all_sheets.items():
                df_clean = clean_sheet(sheet)
                tc_col = df_clean.columns[0]
                df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
                df_m['Thành viên'] = df_m['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
                df_m['Điểm'] = pd.to_numeric(df_m['Điểm'], errors='coerce').fillna(0)
                
                tich_cuc = df_m[tc_col].unique()[:2].tolist()
                tieu_cuc = df_m[tc_col].unique()[2:].tolist() if len(df_m[tc_col].unique()) > 2 else []
                
                df_mem = df_m[df_m['Thành viên'] == selected_member]
                pos_score = df_mem[df_mem[tc_col].isin(tich_cuc)]['Điểm'].sum()
                neg_score = df_mem[df_mem[tc_col].isin(tieu_cuc)]['Điểm'].sum() if tieu_cuc else 0
                
                trend_data.append({'Tuần': week_name, 'Loại Điểm': 'Tích cực', 'Số phiếu': pos_score})
                trend_data.append({'Tuần': week_name, 'Loại Điểm': 'Tiêu cực', 'Số phiếu': -neg_score}) # Âm hóa để vẽ trực quan
                
            df_trend = pd.DataFrame(trend_data)
            
            line_chart = alt.Chart(df_trend).mark_line(point=True, size=3).encode(
                x=alt.X('Tuần:N', sort=list(all_sheets.keys()), title="Chu kỳ"),
                y=alt.Y('Số phiếu:Q', axis=alt.Axis(format="d", tickMinStep=1)),
                color=alt.Color('Loại Điểm:N', scale=alt.Scale(domain=['Tích cực', 'Tiêu cực'], range=['#2ecc71', '#e74c3c'])),
                tooltip=['Tuần', 'Loại Điểm', 'Số phiếu']
            ).properties(height=400).interactive()
            
            st.altair_chart(line_chart, use_container_width=True)

    else:
        # GIAO DIỆN KHI CHỈ CÓ 1 TUẦN
        st.subheader("Bảng Đánh Giá Tuần (Cột Chồng)")
        selected_week = list(all_sheets.keys())[0]
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Thành viên'] = df_long['Thành viên'].str.replace('\n', ' ').str.replace('\r', '').str.strip()
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        cows = df_raw[col_tc].unique().tolist()
        
        render_kpi_cards(df_long, cows, col_tc)
        st.altair_chart(plot_stacked_chart(df_long, cows, col_tc), use_container_width=True)
        
        with st.expander("📋 Số liệu chi tiết"):
            df_display = df_raw.copy()
            match_cols = [c for c in fixed_names if c in df_display.columns]
            other_cols = [c for c in df_display.columns if c != col_tc and c not in fixed_names]
            st.dataframe(df_display[[col_tc] + match_cols + other_cols], use_container_width=True, height=200)

except Exception as e:
    st.error(f"Đang tải dữ liệu, vui lòng đợi hoặc kiểm tra file: {e}")
