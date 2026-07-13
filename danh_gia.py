import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]
    
    # 1. TỰ ĐỘNG LÀM SẠCH: Loại bỏ cột Unnamed và các dòng trống
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.dropna(how='all') 
    
    # 2. CHUYỂN DỮ LIỆU SANG DẠNG DÀI (Tự động nhận diện mọi thành viên)
    col_tieu_chi = df.columns[0]
    df_long = df.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    # Hàm vẽ biểu đồ tự động
    def draw_chart(tieu_chi_list, title, color):
        data = df_long[df_long[col_tieu_chi].isin(tieu_chi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        c = alt.Chart(data).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        
        st.subheader(title)
        st.caption(f"Nội dung: {', '.join(tieu_chi_list)}")
        st.altair_chart(c, use_container_width=True)

    # 3. TỰ ĐỘNG LẤY TẤT CẢ CÁC CÂU HỎI
    danh_sach_cau_hoi = df[col_tieu_chi].unique().tolist()

    # Hiển thị: Nếu bạn có bao nhiêu dòng trong Excel, nó sẽ tự hiện bấy nhiêu biểu đồ
    for i, cau_hoi in enumerate(danh_sach_cau_hoi):
        color = '#e74c3c' if i >= 2 else '#3498db' # 2 câu đầu xanh, từ câu 3 đỏ
        draw_chart([cau_hoi], f"Tiêu chí {i+1}", color)

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df, use_container_width=True, height=300)

except Exception as e:
    st.error(f"Lỗi tải dữ liệu. Hãy đảm bảo file Excel có định dạng chuẩn. Chi tiết: {e}")
