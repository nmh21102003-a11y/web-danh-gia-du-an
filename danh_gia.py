import streamlit as st
import pandas as pd

st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp")

# Nhập cứng dữ liệu để loại bỏ hoàn toàn lỗi đọc file trên server
data = {
    "Người đánh giá": ["Nguyễn Tuấn Vinh", "Trần Trang Thảo", "Lưu Hoàng Minh", "Nguyễn Lê Huy", "Mai Việt Dũng", "Trần Quý Giáp", "Đỗ Trung Hiếu", "Hoàng Ngọc Bích", "Lê Danh Toàn", "Đỗ Thành Long"],
    "Câu 1 (Hỗ trợ)": [1, 0, 3, 1, 4, 2, 4, 6, 0, 4],
    "Câu 2 (Hiệu quả)": [1, 1, 2, 2, 2, 2, 4, 6, 0, 2],
    "Câu 3 (Khó khăn)": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Câu 4 (Nỗ lực)": [0, 0, 0, 0, 2, 0, 0, 0, 1, 0]
}
df = pd.DataFrame(data).set_index("Người đánh giá")

# Vẽ biểu đồ
st.subheader("📈 Câu 1: Ai giúp đỡ bạn nhiều nhất?")
st.bar_chart(df["Câu 1 (Hỗ trợ)"])

st.subheader("🚀 Câu 2: Ai làm việc hiệu quả nhất?")
st.bar_chart(df["Câu 2 (Hiệu quả)"])

st.subheader("⚠️ Tổng hợp Câu 3 & 4")
st.bar_chart(df[["Câu 3 (Khó khăn)", "Câu 4 (Nỗ lực)"]])
