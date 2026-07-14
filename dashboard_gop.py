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

try:
    all_sheets = load_data()
    tab1, tab2 = st.tabs(["📅 Đánh Giá Từng Tuần", "📈 Tổng Hợp Cá Nhân Theo Tuần"])
    
    # 1. TAB ĐÁNH GIÁ TỪNG TUẦN
    with tab1:
        selected_week = st.selectbox("Chọn Tuần cần xem:", list(all_sheets.keys()))
        df_raw = clean_sheet(all_sheets[selected_week])
        col_tc = df_raw.columns[0]
        
        df_long = df_raw.melt(id_vars=[col_tc], var_name='Thành viên', value_name='Điểm')
        df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)
        
        # Biểu đồ cột cho tuần cụ thể
        chart = alt.Chart(df_long).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', title="Số phiếu"),
            color=alt.Color(f'{col_tc}:N', legend=alt.Legend(title="Tiêu chí", orient='bottom', direction='vertical', labelLimit=1000)),
            tooltip=['Thành viên', f'{col_tc}', 'Điểm']
        ).properties(height=500).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        with st.expander("📋 Số liệu chi tiết"): st.dataframe(df_raw, use_container_width=True)

    # 2. TAB TỔNG HỢP CÁ NHÂN THEO TUẦN (Thay thế xu hướng)
    with tab2:
        st.subheader("Theo dõi biến động phong độ cá nhân qua từng tuần")
        selected_member = st.selectbox("🔍 Chọn Thành viên:", fixed_names)
        
        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_clean = clean_sheet(sheet)
            tc_col = df_clean.columns[0]
            df_m = df_clean.melt(id_vars=[tc_col], var_name='Thành viên', value_name='Điểm')
            df_mem = df_m[df_m['Thành viên'] == selected_member]
            
            cows_list = df_m[tc_col].unique()
            pos = df_mem[df_mem[tc_col].isin(cows_list[:2])]['Điểm'].sum()
            neg = df_mem[df_mem[tc_col].isin(cows_list[2:])]['Điểm'].sum() if len(cows_list) >= 4 else 0
            
            trend_data.append({'Tuần': week_name, 'Đóng góp': pos, 'Cảnh báo': neg})
        
        df_trend = pd.DataFrame(trend_data)
        
        # Vẽ biểu đồ kết hợp cột (Đóng góp) và đường (Cảnh báo)
        base = alt.Chart(df_trend).encode(x=alt.X('Tuần:N', title="Chu kỳ tuần", axis=alt.Axis(labelAngle=0)))
        
        bar = base.mark_bar(color='#2ecc71', opacity=0.6).encode(
            y=alt.Y('Đóng góp:Q', title="Số điểm")
        )
        line = base.mark_line(color='#e74c3c', strokeWidth=3, point=True).encode(
            y=alt.Y('Cảnh báo:Q', title="Số điểm")
        )
        
        st.altair_chart((bar + line).properties(height=400).interactive(), use_container_width=True)
        st.info("💡 **Cách đọc:** Cột xanh (Tiêu chí 1&2) là tổng điểm Đóng góp. Đường đỏ (Tiêu chí 3&4) là tổng điểm Cảnh báo qua các tuần.")

except Exception as e:
    st.error(f"Lỗi: {e}")
