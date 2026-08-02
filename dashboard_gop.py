import datetime
import re

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Bảng tổng hợp đánh giá nội bộ",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Bảng tổng hợp đánh giá nội bộ")

# Ghi chú nguồn phiếu
st.info(
    "📌 **Ghi chú:** Tổng số phiếu đánh giá tối đa mỗi tuần đối với từng tiêu chí là 16 phiếu "
    "(bao gồm 06 phiếu của nhóm thường trực dự án, 06 phiếu của nhóm văn phòng dự án, "
    "04 phiếu của team McKinsey). Tiêu chí 1 & 2: Tiêu chí đóng góp. "
    "Tiêu chí 3 & 4: Tiêu chí cảnh báo."
)

file_url = (
    "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/"
    "raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"
)


# ttl=0 để dữ liệu luôn được tải mới từ URL mỗi khi tải lại trang
@st.cache_data(ttl=0)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)


fixed_names = [
    "Nguyễn Tuấn Vinh",
    "Trần Trang Thảo",
    "Lưu Hoàng Minh",
    "Nguyễn Lê Huy",
    "Mai Việt Dũng",
    "Trần Quý Giáp",
    "Lê Danh Toàn",
    "Hoàng Ngọc Bích",
    "Đỗ Trung Hiếu",
    "Đỗ Thành Long",
]


def clean_sheet(sheet):
    """Làm sạch một sheet dữ liệu đánh giá."""
    df = sheet.loc[:, ~sheet.columns.str.contains(r"^Unnamed")].dropna(how="all")
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", "", regex=False)
        .str.strip()
    )

    # Tự động thêm dấu chấm vào cuối Tiêu chí 04 nếu chưa có
    if not df.empty:
        tc_col = df.columns[0]
        df[tc_col] = df[tc_col].apply(
            lambda x: (
                str(x).strip() + "."
                if isinstance(x, str)
                and "Tiêu chí 04" in str(x)
                and not str(x).strip().endswith(".")
                else x
            )
        )

    return df


def get_week_period(sheet_name):
    """
    Trả về ngày bắt đầu và ngày kết thúc của kỳ đánh giá.

    Quy ước hiện tại:
    - Pre-work & Tuần 1: 22/06/2026 - 07/07/2026.
    - Từ Tuần 2 trở đi: mỗi kỳ kéo dài 7 ngày liên tiếp.
    """
    name = sheet_name.strip()

    is_week_one = re.search(r"Tuần\s*0?1(?!\d)", name, flags=re.IGNORECASE)
    if "Pre-work" in name or is_week_one:
        return datetime.date(2026, 6, 22), datetime.date(2026, 7, 7)

    match = re.search(r"Tuần\s*(\d+)", name, flags=re.IGNORECASE)
    if not match:
        return None

    week_number = int(match.group(1))
    if week_number < 2:
        return None

    base_end_date = datetime.date(2026, 7, 7)
    start_date = base_end_date + datetime.timedelta(days=1 + (week_number - 2) * 7)
    end_date = start_date + datetime.timedelta(days=6)
    return start_date, end_date


def format_date(date_value):
    return f"{date_value.day:02d}/{date_value.month:02d}/{date_value.year}"


def get_display_name(sheet_name):
    """Tên kỳ đánh giá đầy đủ dành cho hộp chọn ở Tab 1."""
    name = sheet_name.strip()
    clean_name = name

    if "Phiếu Đánh Giá" in name:
        clean_name = "Phiếu Đánh Giá " + name.split("Phiếu Đánh Giá")[-1].strip()

    period = get_week_period(sheet_name)
    if period is None:
        return clean_name

    start_date, end_date = period
    return (
        f"{clean_name} (từ ngày {format_date(start_date)} "
        f"đến ngày {format_date(end_date)})"
    )


def get_split_week_name(sheet_name):
    """Rút gọn và ngắt dòng tên kỳ đánh giá dành cho trục X ở Tab 2."""
    name = sheet_name.strip()
    if "Phiếu Đánh Giá" in name:
        suffix = name.split("Phiếu Đánh Giá")[-1].strip()
        return f"Phiếu Đánh Giá ~ {suffix}"
    return name


def get_criterion_number(criterion_text):
    """Lấy số tiêu chí 1-4 từ nội dung câu hỏi."""
    match = re.search(r"Tiêu chí\s*0?([1-4])", str(criterion_text), flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def get_month_key(sheet_name):
    """
    Xác định tháng của kỳ đánh giá theo ngày kết thúc kỳ.
    Ví dụ kỳ kết thúc ngày 07/07/2026 được tính vào tháng 07/2026.
    """
    period = get_week_period(sheet_name)
    if period is None:
        return None
    _, end_date = period
    return end_date.strftime("%Y-%m")


def format_month(month_key):
    year, month = month_key.split("-")
    return f"Tháng {month}/{year}"


def build_monthly_ranking(all_sheets):
    """
    Tổng hợp xếp hạng theo tháng.

    Công thức:
    Điểm xếp hạng = tổng phiếu Tiêu chí 1 & 2 - tổng phiếu Tiêu chí 3 & 4.
    """
    records = []

    for week_name, sheet in all_sheets.items():
        month_key = get_month_key(week_name)
        if month_key is None:
            continue

        df_clean = clean_sheet(sheet)
        if df_clean.empty:
            continue

        criterion_col = df_clean.columns[0]
        df_long = df_clean.melt(
            id_vars=[criterion_col],
            var_name="Thành viên",
            value_name="Số phiếu",
        )
        df_long["Số phiếu"] = pd.to_numeric(
            df_long["Số phiếu"], errors="coerce"
        ).fillna(0)
        df_long["Mã tiêu chí"] = df_long[criterion_col].apply(get_criterion_number)

        # Chỉ lấy đúng 10 thành viên và 4 tiêu chí đánh giá.
        df_long = df_long[
            df_long["Thành viên"].isin(fixed_names)
            & df_long["Mã tiêu chí"].isin([1, 2, 3, 4])
        ]

        positive_votes = (
            df_long[df_long["Mã tiêu chí"].isin([1, 2])]
            .groupby("Thành viên")["Số phiếu"]
            .sum()
        )
        warning_votes = (
            df_long[df_long["Mã tiêu chí"].isin([3, 4])]
            .groupby("Thành viên")["Số phiếu"]
            .sum()
        )

        for member in fixed_names:
            records.append(
                {
                    "Tháng": month_key,
                    "Thành viên": member,
                    "Phiếu đóng góp": float(positive_votes.get(member, 0)),
                    "Phiếu cảnh báo": float(warning_votes.get(member, 0)),
                    "Số kỳ": 1,
                }
            )

    if not records:
        return pd.DataFrame()

    monthly = pd.DataFrame(records)
    monthly = (
        monthly.groupby(["Tháng", "Thành viên"], as_index=False)
        .agg(
            {
                "Phiếu đóng góp": "sum",
                "Phiếu cảnh báo": "sum",
                "Số kỳ": "sum",
            }
        )
    )
    monthly["Điểm xếp hạng"] = (
        monthly["Phiếu đóng góp"] - monthly["Phiếu cảnh báo"]
    )

    return monthly


def prepare_ranking_table(monthly_data, selected_month):
    """Sắp xếp và đánh số thứ hạng cho một tháng."""
    ranking = monthly_data[monthly_data["Tháng"] == selected_month].copy()
    ranking = ranking.sort_values(
        by=["Điểm xếp hạng", "Phiếu đóng góp", "Phiếu cảnh báo", "Thành viên"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    ranking.insert(0, "Xếp hạng", range(1, len(ranking) + 1))
    ranking["Hạng"] = ranking["Xếp hạng"].map(
        {1: "🥇 1", 2: "🥈 2", 3: "🥉 3"}
    ).fillna(ranking["Xếp hạng"].astype(str))

    return ranking


def add_previous_month_comparison(ranking, monthly_data, selected_month):
    """Bổ sung thay đổi điểm và thay đổi thứ hạng so với tháng liền trước có dữ liệu."""
    month_keys = sorted(monthly_data["Tháng"].dropna().unique().tolist())
    current_index = month_keys.index(selected_month)

    if current_index == 0:
        ranking["So với tháng trước"] = "—"
        return ranking, None

    previous_month = month_keys[current_index - 1]
    previous_ranking = prepare_ranking_table(monthly_data, previous_month)

    previous_rank_map = previous_ranking.set_index("Thành viên")["Xếp hạng"].to_dict()
    previous_score_map = previous_ranking.set_index("Thành viên")["Điểm xếp hạng"].to_dict()

    comparison_text = []
    for _, row in ranking.iterrows():
        member = row["Thành viên"]
        if member not in previous_rank_map:
            comparison_text.append("Mới")
            continue

        rank_change = previous_rank_map[member] - row["Xếp hạng"]
        score_change = row["Điểm xếp hạng"] - previous_score_map[member]

        if rank_change > 0:
            rank_text = f"↑ {rank_change} hạng"
        elif rank_change < 0:
            rank_text = f"↓ {abs(rank_change)} hạng"
        else:
            rank_text = "Giữ hạng"

        if score_change > 0:
            score_text = f"+{score_change:g} điểm"
        elif score_change < 0:
            score_text = f"{score_change:g} điểm"
        else:
            score_text = "0 điểm"

        comparison_text.append(f"{rank_text}; {score_text}")

    ranking["So với tháng trước"] = comparison_text
    return ranking, previous_month


# Hàm vẽ biểu đồ với cố định màu và tiêu chí
def plot_stacked_chart(
    df_long,
    col_tc,
    list_criteria,
    x_axis_title="Thành viên",
    is_week_view=True,
):
    df_chart = df_long.copy()
    df_chart["Điểm"] = pd.to_numeric(df_chart["Điểm"], errors="coerce").fillna(0)

    # Logic âm dương: Tiêu chí 1 & 2 là đóng góp, Tiêu chí 3 & 4 là cảnh báo.
    if len(list_criteria) >= 4:
        negative_criteria = list_criteria[2:]
        df_chart.loc[df_chart[col_tc].isin(negative_criteria), "Điểm"] *= -1

    # Gắn số thứ tự cho tiêu chí để giữ trật tự cố định.
    criterion_order = {criterion: i for i, criterion in enumerate(list_criteria)}
    df_chart["tc_cat_sort"] = df_chart[col_tc].map(criterion_order)
    df_chart = df_chart.sort_values(
        [x_axis_title, "tc_cat_sort"], ascending=[True, True]
    )

    # Tính vị trí giữa của từng phần cột để đặt nhãn số phiếu.
    df_chart["mid_y"] = 0.0
    for member in df_chart[x_axis_title].unique():
        mask = df_chart[x_axis_title] == member
        positive_sum = 0.0
        negative_sum = 0.0

        for index, row in df_chart[mask].iterrows():
            value = row["Điểm"]
            if value > 0:
                df_chart.loc[index, "mid_y"] = positive_sum + value / 2.0
                positive_sum += value
            elif value < 0:
                df_chart.loc[index, "mid_y"] = negative_sum + value / 2.0
                negative_sum += value

    df_text = df_chart[
        df_chart["Điểm"].notna() & (df_chart["Điểm"] != 0)
    ].copy()

    custom_colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]
    unique_x = len(df_chart[x_axis_title].unique())
    width_per_bar = 80 if is_week_view else 140
    chart_width = max(800, unique_x * width_per_bar)

    base = alt.Chart(df_chart).encode(
        x=alt.X(
            f"{x_axis_title}:N",
            sort=fixed_names if is_week_view else None,
            axis=alt.Axis(
                labelAngle=0,
                labelOverlap=False,
                labelExpr="split(datum.value, ' ~ ')",
                domain=False,
                ticks=False,
            ),
        )
    )

    bars = base.mark_bar(size=40).encode(
        y=alt.Y(
            "Điểm:Q",
            title="Số phiếu đánh giá",
            scale=alt.Scale(nice=False),
        ),
        color=alt.Color(
            f"{col_tc}:N",
            scale=alt.Scale(domain=list_criteria, range=custom_colors),
            legend=alt.Legend(
                title="Tiêu chí đánh giá",
                orient="bottom",
                direction="vertical",
                labelLimit=1000,
            ),
        ),
        order=alt.Order("tc_cat_sort:O", sort="ascending"),
        tooltip=[x_axis_title, col_tc, "Điểm"],
    )

    text = alt.Chart(df_text).mark_text(
        baseline="middle",
        align="center",
        fontWeight="bold",
    ).encode(
        x=alt.X(
            f"{x_axis_title}:N",
            sort=fixed_names if is_week_view else None,
        ),
        y=alt.Y("mid_y:Q", stack=None, title="Số phiếu đánh giá"),
        text=alt.Text("Điểm:Q", format="d"),
        color=alt.value("white"),
    )

    chart = (bars + text).properties(width=chart_width, height=500)

    zero_rule = (
        alt.Chart(pd.DataFrame({"Điểm": [0]}))
        .mark_rule(color="#333333", strokeWidth=2)
        .encode(y="Điểm:Q")
    )

    return (chart + zero_rule).interactive()


def plot_ranking_chart(ranking):
    """Biểu đồ điểm xếp hạng của các thành viên trong tháng."""
    chart_data = ranking.copy()
    chart_data["Nhãn điểm"] = chart_data["Điểm xếp hạng"].map(lambda x: f"{x:g}")

    bars = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusEnd=5)
        .encode(
            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(field="Xếp hạng", order="ascending"),
                title=None,
                axis=alt.Axis(labelLimit=180),
            ),
            x=alt.X("Điểm xếp hạng:Q", title="Điểm xếp hạng"),
            color=alt.condition(
                alt.datum["Điểm xếp hạng"] >= 0,
                alt.value("#2ecc71"),
                alt.value("#e74c3c"),
            ),
            tooltip=[
                "Xếp hạng:Q",
                "Thành viên:N",
                "Phiếu đóng góp:Q",
                "Phiếu cảnh báo:Q",
                "Điểm xếp hạng:Q",
            ],
        )
    )

    text = (
        alt.Chart(chart_data)
        .mark_text(dx=5, align="left", fontWeight="bold")
        .encode(
            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(field="Xếp hạng", order="ascending"),
            ),
            x=alt.X("Điểm xếp hạng:Q"),
            text="Nhãn điểm:N",
        )
    )

    zero_rule = (
        alt.Chart(pd.DataFrame({"Điểm xếp hạng": [0]}))
        .mark_rule(color="#333333", strokeWidth=1.5)
        .encode(x="Điểm xếp hạng:Q")
    )

    return (bars + text + zero_rule).properties(height=420)


try:
    all_sheets = load_data()

    if not all_sheets:
        st.warning("File Excel chưa có sheet dữ liệu.")
        st.stop()

    first_sheet = list(all_sheets.values())[0]
    df_first = clean_sheet(first_sheet)

    if df_first.empty:
        st.warning("Sheet đầu tiên chưa có dữ liệu.")
        st.stop()

    global_criterion_col = df_first.columns[0]
    global_criteria = df_first[global_criterion_col].dropna().unique().tolist()

    tab1, tab2, tab3 = st.tabs(
        [
            "📅 Đánh Giá Từng Tuần",
            "📈 Tổng Hợp Cá Nhân Theo Tuần",
            "🏆 Xếp Hạng Theo Tháng",
        ]
    )

    with tab1:
        week_options = {get_display_name(name): name for name in all_sheets.keys()}
        selected_display_week = st.selectbox(
            "Chọn Tuần:",
            list(week_options.keys()),
            key="selected_week",
        )
        selected_week = week_options[selected_display_week]

        df_raw = clean_sheet(all_sheets[selected_week])
        criterion_col = df_raw.columns[0]
        df_long = df_raw.melt(
            id_vars=[criterion_col],
            var_name="Thành viên",
            value_name="Điểm",
        )
        df_long["Điểm"] = pd.to_numeric(df_long["Điểm"], errors="coerce").fillna(0)

        st.altair_chart(
            plot_stacked_chart(
                df_long,
                criterion_col,
                global_criteria,
                x_axis_title="Thành viên",
                is_week_view=True,
            ),
            use_container_width=True,
        )

        with st.expander("📋 Số liệu chi tiết"):
            st.dataframe(df_raw, use_container_width=True, hide_index=True)

    with tab2:
        selected_member = st.selectbox(
            "🔍 Chọn Thành viên:",
            fixed_names,
            key="selected_member",
        )

        trend_data = []
        for week_name, sheet in all_sheets.items():
            df_clean = clean_sheet(sheet)
            if df_clean.empty:
                continue

            criterion_col = df_clean.columns[0]
            df_melted = df_clean.melt(
                id_vars=[criterion_col],
                var_name="Thành viên",
                value_name="Điểm",
            )
            df_member = df_melted[df_melted["Thành viên"] == selected_member].copy()
            df_member["Điểm"] = pd.to_numeric(
                df_member["Điểm"], errors="coerce"
            ).fillna(0)

            display_week = get_split_week_name(week_name)

            for _, row in df_member.iterrows():
                trend_data.append(
                    {
                        "Tuần": display_week,
                        criterion_col: row[criterion_col],
                        "Điểm": row["Điểm"],
                    }
                )

        df_trend = pd.DataFrame(trend_data)
        if not df_trend.empty:
            criterion_col = df_trend.columns[1]
            st.altair_chart(
                plot_stacked_chart(
                    df_trend,
                    criterion_col,
                    global_criteria,
                    x_axis_title="Tuần",
                    is_week_view=False,
                ),
                use_container_width=True,
            )
        else:
            st.warning("Chưa có dữ liệu cho thành viên này.")

    with tab3:
        monthly_data = build_monthly_ranking(all_sheets)

        if monthly_data.empty:
            st.warning(
                "Chưa xác định được tháng từ tên các sheet. "
                "Vui lòng giữ cách đặt tên như 'Phiếu Đánh Giá Tuần 5'."
            )
        else:
            month_keys = sorted(monthly_data["Tháng"].unique().tolist(), reverse=True)
            month_options = {format_month(key): key for key in month_keys}

            selected_display_month = st.selectbox(
                "Chọn tháng:",
                list(month_options.keys()),
                key="selected_month",
            )
            selected_month = month_options[selected_display_month]

            ranking = prepare_ranking_table(monthly_data, selected_month)
            ranking, previous_month = add_previous_month_comparison(
                ranking,
                monthly_data,
                selected_month,
            )

            st.caption(
                "Cách tính: **Điểm xếp hạng = tổng phiếu đóng góp "
                "(Tiêu chí 1 + 2) − tổng phiếu cảnh báo (Tiêu chí 3 + 4)**. "
                "Một kỳ đánh giá được tính vào tháng chứa ngày kết thúc của kỳ."
            )

            top_members = ranking.head(3).to_dict("records")
            top_columns = st.columns(3)
            medals = ["🥇", "🥈", "🥉"]

            for index, column in enumerate(top_columns):
                with column:
                    if index < len(top_members):
                        member = top_members[index]
                        st.metric(
                            label=f"{medals[index]} Hạng {index + 1}",
                            value=member["Thành viên"],
                            delta=f'{member["Điểm xếp hạng"]:g} điểm',
                            delta_color="off",
                        )

            st.altair_chart(
                plot_ranking_chart(ranking),
                use_container_width=True,
            )

            display_columns = [
                "Hạng",
                "Thành viên",
                "Phiếu đóng góp",
                "Phiếu cảnh báo",
                "Điểm xếp hạng",
                "So với tháng trước",
            ]
            display_ranking = ranking[display_columns].copy()

            for numeric_col in [
                "Phiếu đóng góp",
                "Phiếu cảnh báo",
                "Điểm xếp hạng",
            ]:
                display_ranking[numeric_col] = display_ranking[numeric_col].map(
                    lambda value: int(value) if float(value).is_integer() else value
                )

            st.dataframe(
                display_ranking,
                use_container_width=True,
                hide_index=True,
            )

            number_of_periods = int(ranking["Số kỳ"].max()) if not ranking.empty else 0
            comparison_note = (
                f"; so sánh với {format_month(previous_month)}"
                if previous_month is not None
                else ""
            )
            st.caption(
                f"Dữ liệu tháng này gồm {number_of_periods} kỳ đánh giá{comparison_note}."
            )

except Exception as error:
    st.error(f"Lỗi: {error}")
