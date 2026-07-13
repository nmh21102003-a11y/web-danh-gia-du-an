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
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')].dropna(how='all')
    
    col_tieu_chi = df.columns[0]
    df_long = df.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    def draw_chart(tieu_chi_list, title, color, note):
        data = df_long[df_long[col_tieu_chi].isin(tieu_chi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        c = alt.Chart(data).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        
        st.subheader(title)
        st.caption(note)
        st.altair_chart(c, use_container_width=True)

    cows = df[col_tieu_chi].unique().tolist()

    # Bảng 1
    draw_chart([cows[0]], "1️⃣ Tiêu chí 1", '#3498db', cows[0])
    # Bảng 2
    draw_chart([cows[1]], "2️⃣ Tiêu chí 2", '#3498db', cows[1])
    # Bảng 3 & 4 (Gộp)
    draw_chart([cows[2], cows[3]], "3️⃣ & 4️⃣ Tiêu chí tiêu cực", '#e74c3c', f"{cows[2]} & {cows[3]}")

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df, use_container_width=True, height=300)

except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
