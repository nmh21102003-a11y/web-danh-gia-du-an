import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Chi Tiết")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # --- CHUẨN BỊ DỮ LIỆU ---
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Rút gọn tên cột (lấy phần chữ trước dấu hai chấm nếu có)
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]
    
    # Lấy các cột số liệu
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    cols = df_numeric.columns.tolist()

    # Kiểm tra xem có đủ ít nhất 4 cột không
    if len(cols) >= 4:
        c1, c2, c3, c4 = cols[0], cols[1], cols[2], cols[3]
        
        st.header(f"Tuần: {selected_sheet}")
        st.write("---")

        # ==========================================
        # CHART 1: CÂU 1 (Biểu đồ thanh ngang)
        # ==========================================
        st.subheader(f"1️⃣ {c1}")
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        ax1.barh(df_numeric.index, df_numeric[c1], color='#4C72B0', height=0.5)
        ax1.spines[['top', 'right']].set_visible(False)
        ax1.spines[['bottom', 'left']].set_color('#E0E0E0')
        ax1.set_xlabel("Điểm số")
        st.pyplot(fig1)

        st.write("---")

        # ==========================================
        # CHART 2: CÂU 2 (Biểu đồ Kẹo mút - Lollipop)
        # ==========================================
        st.subheader(f"2️⃣ {c2}")
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        # Vẽ đường thẳng mảnh
        ax2.hlines(y=df_numeric.index, xmin=0, xmax=df_numeric[c2], color='#E67E22', linewidth=2)
        # Vẽ dấu chấm ở đầu
        ax2.plot(df_numeric[c2], df_numeric.index, "o", markersize=10, color='#D35400')
        
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.spines[['bottom', 'left']].set_color('#E0E0E0')
        ax2.set_xlabel("Điểm số")
        st.pyplot(fig2)

        st.write("---")

        # ==========================================
        # CHART 3: CÂU 3 & CÂU 4 (Biểu đồ cột chồng - Stacked Bar)
        # ==========================================
        st.subheader(f"3️⃣ Tổng hợp: {c3} & {c4}")
        fig3, ax3 = plt.subplots(figsize=(10, 4))
        
        # Dùng lệnh plot với stacked=True để gộp 2 cột thành 1 thanh
        df_numeric[[c3, c4]].plot(kind='barh', stacked=True, ax=ax3, color=['#2ECC71', '#9B59B6'], width=0.5)
        
        ax3.spines[['top', 'right']].set_visible(False)
        ax3.spines[['bottom', 'left']].set_color('#E0E0E0')
        ax3.set_xlabel("Tổng Điểm")
        ax3.set_ylabel("") # Ẩn nhãn trục Y cho đỡ rối
        
        # Đưa bảng chú thích ra ngoài biểu đồ một chút cho thoáng
        ax3.legend(bbox_to_anchor=(1.0, 1.05))
        
        st.pyplot(fig3)

    else:
        st.warning("File Excel của bạn cần có ít nhất 4 cột tiêu chí (Câu hỏi) để hiển thị đầy đủ các biểu đồ này.")
        
    st.write("---")
    with st.expander("📋 Xem toàn bộ bảng dữ liệu gốc"):
        st.dataframe(df_numeric.astype(str), use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
