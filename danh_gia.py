import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Đánh giá dự án", layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp")

# Dữ liệu của bạn
data = {
    "Người đánh giá": ["Nguyễn Tuấn Vinh", "Trần Trang Thảo", "Lưu Hoàng Minh", "Nguyễn Lê Huy", "Mai Việt Dũng", "Trần Quý Giáp", "Đỗ Trung Hiếu", "Hoàng Ngọc Bích", "Lê Danh Toàn", "Đỗ Thành Long"],
    "Câu 1 (Hỗ trợ)": [1, 0, 3, 1, 4, 2, 4, 6, 0, 4],
    "Câu 2 (Hiệu quả)": [1, 1, 2, 2, 2, 2, 4, 6, 0, 2],
    "Câu 3 (Khó khăn)": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Câu 4 (Nỗ lực)": [0, 0, 0, 0, 2, 0, 0, 0, 1, 0]
}
df = pd.DataFrame(data)

# Hàm vẽ biểu đồ ngang (đẹp và dễ đọc tên)
def ve_bieu_do_ngang(cot_du_lieu, tieu_de):
    chart_data = pd.DataFrame({
        "Người đánh giá": df["Người đánh giá"],
        "Điểm số": cot_du_lieu
    })
    
    chart = alt.Chart(chart_data).mark_bar(color='#1f77b4').encode(
        x=alt.X('Điểm số', title='Số điểm'),
        y=alt.Y('Người đánh giá', sort='-x', title=''),
        tooltip=['Người đánh giá', 'Điểm số']
    ).properties(title=tieu_de)
    
    st.altair_chart(chart, use_container_width=True)

# Hiển thị biểu đồ
st.subheader("📈 Câu 1: Mức độ hỗ trợ")
ve_bieu_do_ngang(df["Câu 1 (Hỗ trợ)"], "Điểm hỗ trợ theo cá nhân")

st.subheader("🚀 Câu 2: Mức độ hiệu quả")
ve_bieu_do_ngang(df["Câu 2 (Hiệu quả)"], "Điểm hiệu quả theo cá nhân")

# Biểu đồ gộp cho câu 3 và 4
st.subheader("⚠️ Tổng hợp Khó khăn & Nỗ lực")
df_gop = df.melt("Người đánh giá", value_vars=["Câu 3 (Khó khăn)", "Câu 4 (Nỗ lực)"], var_name="Loại", value_name="Điểm")
chart_gop = alt.Chart(df_gop).mark_bar().encode(
    x=alt.X('Điểm', stack=None),
    y=alt.Y('Người đánh giá', sort='-x'),
    color='Loại',
    tooltip=['Người đánh giá', 'Loại', 'Điểm']
).properties(height=400)
st.altair_chart(chart_gop, use_container_width=True)
