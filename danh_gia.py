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
    
    # Rút gọn tên cột (lấy phần chữ trước dấu hai chấm)
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]
    
    # Lấy các cột số liệu
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    cols = df_numeric.columns.tolist()

    if len(cols) >= 4:
        c1, c2, c3, c4 = cols[0], cols[1], cols[2], cols[3]
        
        st.header(f"Phân tích Tuần: {selected_sheet}")
        st.write("---")

        # ==========================================
        # CHART 1: CÂU 1 (Biểu đồ Cột dọc - Đứng chung sân)
        # ==========================================
        st.subheader(f"1️⃣ {c1}")
        fig1, ax1 = plt.subplots(figsize=(12, 4))
        ax1.bar(df_numeric.index, df_numeric[c1], color='#4C72B0', width=0.5)
        
        ax1.spines[['top', 'right']].set_visible(False)
        ax1.set_ylabel("Điểm số")
        # Xoay nghiêng tên thành viên để không bị đè lên nhau
        plt.xticks(rotation=45, ha='right') 
        st.pyplot(fig1)

        st.write("---")

        # ==========================================
        # CHART 2: CÂU 2 (Biểu đồ Đường - Line Chart)
        # ==========================================
        st.subheader(f"2️⃣ {c2}")
        fig2, ax2 = plt.subplots(figsize=(12, 4))
        # Nối điểm các thành viên bằng đường kẻ
        ax2.plot(df_numeric.index, df_numeric[c2], marker='o', color='#E67E22', linewidth=2, markersize=8)
        
        ax2.spines[['top', 'right']].set_visible(False)
        ax2.set_ylabel("Điểm số")
        plt.xticks(rotation=45, ha='right')
        # Thêm lưới mờ ngang để dễ dóng điểm
        ax2.grid(axis='y', linestyle='--', alpha=0.5) 
        st.pyplot(fig2)

        st.write("---")

        # ==========================================
        # CHART 3: CÂU 3 & CÂU 4 (Biểu đồ Cột chồng Dọc)
        # ==========================================
        st.subheader(f"3️⃣ Tổng hợp: {c3} & {c4}")
        fig3, ax3 = plt.subplots(figsize=(12, 5))
        
        # Gộp 2 điểm thành 1 cột dựng đứng
        df_numeric[[c3, c4]].plot(kind='bar', stacked=True, ax=ax3, color=['#2ECC71', '#9B59B6'], width=0.5)
        
        ax3.spines[['top', 'right']].set_visible(False)
        ax3.set_ylabel("Tổng Điểm")
        ax3.set_xlabel("") # Xóa chữ "Thành viên" mặc định cho đỡ vướng
        plt.xticks(rotation=45, ha='right')
        
        ax3.legend(bbox_to_anchor=(1.0, 1.05))
        st.pyplot(fig3)

    else:
        st.warning("File Excel của bạn cần có ít nhất 4 cột tiêu chí để hiển thị đủ biểu đồ.")
        
    st.write("---")
    with st.expander("📋 Xem toàn bộ bảng dữ liệu gốc"):
        st.dataframe(df_numeric.astype(str), use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
