def plot_stacked_chart(df_long, list_cows, col_tc):
    df_chart = df_long.copy()
    # 2 tiêu chí cuối là tiêu chí cảnh báo -> nhân -1 để nằm dưới trục 0
    if len(list_cows) >= 4:
        tieu_cuc = list_cows[2:] 
        df_chart.loc[df_chart[col_tc].isin(tieu_cuc), 'Điểm'] *= -1
    
    # Bảng màu: Xanh dương, Xanh lá, Cam, Đỏ
    custom_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']
    
    return alt.Chart(df_chart).mark_bar(size=40).encode(
        x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Điểm:Q', title="Số phiếu"),
        color=alt.Color(f'{col_tc}:N', 
                        scale=alt.Scale(range=custom_colors), 
                        legend=alt.Legend(
                            title="Tiêu chí đánh giá", 
                            orient='bottom', 
                            direction='vertical', # Xếp dọc để hiển thị hết chữ
                            labelLimit=1000 # Cho phép chữ dài tối đa 1000px
                        )),
        tooltip=['Thành viên', f'{col_tc}', 'Điểm']
    ).properties(height=500).interactive()
