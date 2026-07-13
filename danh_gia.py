import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # --- 1. DỌN DẸP & LÀM ĐẸP DỮ LIỆU ---
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Rút gọn tên cột (nếu có dấu 2 chấm thì chỉ lấy phần trước)
    # Ví dụ: "Câu 1: Hỗ trợ..." -> "Câu 1"
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]

    st.subheader(f"📌 Dữ liệu chi tiết: {selected_sheet}")
    
    # Ép toàn bộ thành chuỗi để lấy lại bảng st.dataframe đẹp đẽ mà không sợ sập
    st.dataframe(df.astype(str), use_container_width=True)
    
    # --- 2. VẼ BIỂU ĐỒ CHUYÊN NGHIỆP ---
    st.write("---")
    st.subheader("📈 Phân tích điểm số từng thành viên")
    
    # Ép lại về số (nếu lỗi thì bằng 0) để vẽ biểu đồ
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Bộ lọc: Chọn 1 câu để xem cho gọn
    cau_hoi = st.selectbox("Chọn tiêu chí đánh giá để hiển thị biểu đồ:", df_numeric.columns)
    
    # Cấu hình "Nhan sắc" cho Matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df_numeric.index, df_numeric[cau_hoi], color='#4C72B0', edgecolor='none')
    
    # Xóa viền đen xấu xí
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#E0E0E0')
    ax.spines['left'].set_color('#E0E0E0')
    
    # Thêm số điểm hiển thị ngay trên thanh
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.1f}', 
                va='center', ha='left', fontsize=11, color='#333333', fontweight='bold')

    # Chỉnh font và màu chữ
    ax.set_xlabel("Điểm số", fontsize=11, color='#666666')
    ax.tick_params(axis='x', colors='#666666')
    ax.tick_params(axis='y', labelsize=11, colors='#333333')
    
    plt.tight_layout()
    st.pyplot(fig)

except Exception as e:
    st.error(f"Lỗi: {e}")
