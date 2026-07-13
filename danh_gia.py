import streamlit as st
import pandas as pd

# Tiêu đề trang web
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp Theo Tuần")
st.markdown("Dữ liệu được trích xuất từ: **Tuần 1**")

# Hàm đọc và làm sạch dữ liệu
@st.cache_data
def load_data(file_path):
    # Tự động thử các bảng mã tiếng Việt khác nhau để tránh lỗi font
    try:
        df = pd.read_csv(file_path, skiprows=2, encoding='utf-8')
    except Exception:
        try:
            df = pd.read_csv(file_path, skiprows=2, encoding='cp1258') # Bảng mã Windows VN
        except Exception:
            df = pd.read_csv(file_path, skiprows=2, encoding='latin1')
    
    # Xử lý tên cột: Xóa dấu xuống dòng (\n) trong tên người
    df.columns = [col.replace('\n', ' ') for col in df.columns]
    
    # Điền giá trị 0 cho những ô trống (NaN)
    df = df.fillna(0)
    
    # Đặt cột câu hỏi làm Index (Hàng dọc)
    df = df.set_index(df.columns[0])
    return df

# Tên file của bạn 
file_name = "Phieu_Danh_Gia_Tong_Hop_10_Nguoi.xlsx"

try:
    df = load_data(file_name)
    
    # Tách dữ liệu theo từng câu hỏi
    q1_data = df.iloc[0]
    q2_data = df.iloc[1]
    q3_data = df.iloc[2]
    q4_data = df.iloc[3]
    
    st.divider()

    # --- CHART 1 ---
    st.subheader(f"📈 Biểu đồ 1: {df.index[0]}")
    st.bar_chart(q1_data, color="#1f77b4")
    
    # --- CHART 2 ---
    st.subheader(f"🚀 Biểu đồ 2: {df.index[1]}")
    st.bar_chart(q2_data, color="#2ca02c")
    
    # --- CHART 3 (TỔNG HỢP CÂU 3 & 4) ---
    st.subheader("⚠️ Biểu đồ 3: Tổng hợp điểm cần nỗ lực & Khó khăn (Câu 3 & 4)")
    
    # Gộp dữ liệu câu 3 và câu 4 vào thành một bảng mới
    combined_df = pd.DataFrame({
        'Câu 3: Gây khó khăn': q3_data,
        'Câu 4: Cần nỗ lực hơn': q4_data
    })
    
    # Vẽ biểu đồ cột ghép
    st.bar_chart(combined_df, color=["#d62728", "#ff7f0e"])
    
    # Thêm phần xem dữ liệu thô
    with st.expander("Bấm vào đây để xem bảng dữ liệu chi tiết"):
        st.dataframe(df)

except FileNotFoundError:
    st.error(f"Không tìm thấy file `{file_name}`. Hãy kiểm tra lại xem tên file có giống hệt file trong thư mục không nhé.")
except Exception as e:
    st.error(f"Có lỗi xảy ra: {e}")
