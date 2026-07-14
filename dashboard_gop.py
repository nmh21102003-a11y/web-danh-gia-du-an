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
def plot_stacked_chart(df_long, list_cows, col_tc
