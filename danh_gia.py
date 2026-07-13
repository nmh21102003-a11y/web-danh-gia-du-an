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

    # --- 1. CHUẨN BỊ DỮ LIỆU ---
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]

    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_numeric['Tổng Điểm'] = df_numeric.sum(axis=1)
    
    # Sắp xếp để vẽ Leaderboard
    df_leaderboard = df_numeric.sort_values('Tổng Điểm', ascending=True)

    # --- 2. BIỂU ĐỒ XẾP HẠNG (Chỉ vẽ Tổng Điểm) ---
    st.subheader(f"🏆 Xếp Hạng Tổng Điểm: {selected_sheet}")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df_leaderboard.index, df_leaderboard['Tổng Điểm'], color='#2ECC71') # Màu xanh lá tích cực
    
    # Xóa viền đen cho thoáng
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#E0E0E0')
    ax.spines['left'].set_color('#E0E0E0')
    
    # Ghi số tổng điểm
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:g}', 
                va='center', fontweight='bold', color='#333', fontsize=11)

    plt.tight_layout()
    st.pyplot(fig)

    # --- 3. BẢNG BẢN ĐỒ NHIỆT (Dễ nhìn hơn biểu đồ) ---
    st.write("---")
    st.subheader("🔥 Bảng Phân Tích Chi Tiết (Bản Đồ Nhiệt)")
    st.markdown("*Mẹo: Nhìn vào bảng, **màu xanh càng đậm** thể hiện **điểm càng cao**. Bạn có thể dễ dàng so sánh điểm của từng người theo từng câu hỏi.*")
    
    # Lấy các cột câu hỏi (bỏ cột Tổng Điểm để tô màu cho chuẩn)
    cols_chi_tiet = [c for c in df_numeric.columns if c != 'Tổng Điểm']
    
    # Sắp xếp tên theo thứ tự ABC cho dễ tìm
    df_heatmap = df_numeric[cols_chi_tiet].sort_index()
    
    # Tạo bản đồ nhiệt bằng thư viện Pandas (cực kỳ nhẹ và không bao giờ sập)
    styled_df = df_heatmap.style.background_gradient(cmap='Blues', axis=None).format(precision=1)
    
    # Hiển thị ra màn hình
    st.dataframe(styled_df, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
