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

    # --- 1. DỌN DẸP & CHUẨN BỊ DỮ LIỆU ---
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Rút gọn tên cột cho biểu đồ thoáng hơn
    df.columns = [str(col).split(':')[0].strip() if ':' in str(col) else str(col) for col in df.columns]

    # Ép kiểu dữ liệu về số học
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # TỰ ĐỘNG TÍNH TỔNG ĐIỂM
    df_numeric['Tổng Điểm'] = df_numeric.sum(axis=1)
    
    # Sắp xếp danh sách từ cao xuống thấp theo Tổng Điểm
    df_numeric = df_numeric.sort_values('Tổng Điểm', ascending=True)

    st.subheader(f"🏆 Bảng Xếp Hạng Tổng Thể: {selected_sheet}")
    
    # --- 2. VẼ BIỂU ĐỒ CỘT CHỒNG TỔNG HỢP ---
    # Lấy các cột câu hỏi để vẽ (bỏ cột Tổng Điểm ra khỏi màu sắc)
    cols_to_plot = [c for c in df_numeric.columns if c != 'Tổng Điểm']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Vẽ biểu đồ chồng: mỗi màu là 1 câu hỏi
    df_numeric[cols_to_plot].plot(kind='barh', stacked=True, ax=ax, colormap='Set2', edgecolor='white', linewidth=1)
    
    # Làm sạch viền biểu đồ
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#E0E0E0')
    ax.spines['left'].set_color('#E0E0E0')
    
    # In con số Tổng Điểm chốt ở cuối mỗi thanh
    for i, total in enumerate(df_numeric['Tổng Điểm']):
        ax.text(total + 0.2, i, f'{total:g} đ', va='center', fontweight='bold', color='#D32F2F', fontsize=11)

    # Chỉnh sửa font chữ, chú thích
    ax.set_ylabel("")
    ax.set_xlabel("Điểm số", fontsize=11, color='#666')
    plt.legend(title="Các tiêu chí", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    st.pyplot(fig)

    # --- 3. BẢNG DỮ LIỆU TỔNG HỢP ---
    st.write("---")
    with st.expander("👀 Xem Bảng Điểm Chi Tiết (Đã tính tổng)"):
        # Đảo ngược lại để người cao điểm nhất nằm trên cùng của bảng
        st.dataframe(df_numeric.sort_values('Tổng Điểm', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
