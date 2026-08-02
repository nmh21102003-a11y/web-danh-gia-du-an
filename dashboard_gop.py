import datetime
import re
import unicodedata

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Bảng tổng hợp đánh giá nội bộ",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }
        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 12px;
            padding: 0.75rem;
        }
        @media (max-width: 768px) {
            .block-container {
                padding-left: 0.7rem;
                padding-right: 0.7rem;
                padding-top: 0.7rem;
            }
            h1 {
                font-size: 1.55rem !important;
            }
            h2, h3 {
                font-size: 1.15rem !important;
            }
            .stTabs [data-baseweb="tab-list"] {
                overflow-x: auto;
                white-space: nowrap;
            }
            .stTabs [data-baseweb="tab"] {
                flex-shrink: 0;
                padding-left: 0.65rem;
                padding-right: 0.65rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Bảng tổng hợp đánh giá nội bộ")

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

CONFIG_SHEET_NAMES = {
    "cấu hình tháng",
    "cau hinh thang",
    "cau_hinh_thang",
}

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


@st.cache_data(ttl=300)
def load_data():
    """Tải toàn bộ workbook từ GitHub; tự làm mới sau tối đa 5 phút."""
    return pd.read_excel(file_url, sheet_name=None)


def remove_accents(value):
    text = unicodedata.normalize("NFD", str(value))
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


def normalized_key(value):
    return re.sub(r"\s+", " ", remove_accents(value).lower().strip())


def clean_sheet(sheet):
    """Làm sạch một sheet dữ liệu đánh giá."""
    df = sheet.copy()
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")].dropna(how="all")
    df.columns = (
        df.columns.astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace("\r", "", regex=False)
        .str.strip()
    )

    if not df.empty:
        criterion_col = df.columns[0]
        df[criterion_col] = df[criterion_col].apply(
            lambda value: (
                str(value).strip() + "."
                if isinstance(value, str)
                and "Tiêu chí 04" in str(value)
                and not str(value).strip().endswith(".")
                else value
            )
        )

    return df


def get_week_period(sheet_name):
    """Tính ngày bắt đầu và ngày kết thúc chỉ để hiển thị tên kỳ."""
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
    """Tên kỳ đầy đủ trong hộp chọn của tab đánh giá tuần."""
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
    """Rút gọn tên kỳ để hiển thị trên biểu đồ."""
    name = sheet_name.strip()
    if "Phiếu Đánh Giá" in name:
        suffix = name.split("Phiếu Đánh Giá")[-1].strip()
        return f"Phiếu Đánh Giá ~ {suffix}"
    return name


def get_criterion_number(criterion_text):
    match = re.search(
        r"Tiêu chí\s*0?([1-4])",
        str(criterion_text),
        flags=re.IGNORECASE,
    )
    return int(match.group(1)) if match else None


def parse_month_value(value):
    """Nhận các dạng 07/2026, 2026-07, Tháng 07/2026 hoặc ngày Excel."""
    if value is None or pd.isna(value):
        return None

    if isinstance(value, (pd.Timestamp, datetime.datetime, datetime.date)):
        return value.strftime("%Y-%m")

    text = str(value).strip()
    match = re.search(r"(?<!\d)(0?[1-9]|1[0-2])\s*[/\-]\s*(20\d{2})(?!\d)", text)
    if match:
        month = int(match.group(1))
        year = int(match.group(2))
        return f"{year:04d}-{month:02d}"

    match = re.search(r"(?<!\d)(20\d{2})\s*[/\-]\s*(0?[1-9]|1[0-2])(?!\d)", text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return f"{year:04d}-{month:02d}"

    return None


def find_config_sheet(all_sheets):
    for sheet_name in all_sheets:
        if normalized_key(sheet_name) in CONFIG_SHEET_NAMES:
            return sheet_name
    return None


def build_month_config(config_sheet):
    """Đọc sheet Cấu hình tháng thành dictionary theo tên sheet dữ liệu."""
    if config_sheet is None or config_sheet.empty:
        return {}

    config = config_sheet.copy().dropna(how="all")
    config.columns = [str(column).strip() for column in config.columns]
    column_map = {normalized_key(column): column for column in config.columns}

    sheet_column = column_map.get("ten sheet")
    month_column = column_map.get("thang xep hang")
    order_column = column_map.get("thu tu ky")
    include_column = column_map.get("tinh vao bxh")

    if sheet_column is None or month_column is None:
        return {}

    result = {}
    for _, row in config.iterrows():
        raw_sheet_name = row.get(sheet_column)
        if raw_sheet_name is None or pd.isna(raw_sheet_name):
            continue

        sheet_name = str(raw_sheet_name).strip()
        month_key = parse_month_value(row.get(month_column))

        raw_order = row.get(order_column) if order_column is not None else None
        order_value = pd.to_numeric(raw_order, errors="coerce")
        order_value = int(order_value) if pd.notna(order_value) else None

        raw_include = row.get(include_column) if include_column is not None else "Có"
        include_text = normalized_key(raw_include)
        include = include_text not in {"khong", "no", "false", "0"}

        result[sheet_name] = {
            "month": month_key,
            "order": order_value,
            "include": include,
        }

    return result


def get_fallback_period_order(sheet_name):
    name = sheet_name.strip()
    if "Pre-work" in name:
        return 1

    match = re.search(r"Tuần\s*(\d+)", name, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))

    return 9999


def sort_period_names(period_names, month_config):
    def sort_key(sheet_name):
        configured_order = month_config.get(sheet_name, {}).get("order")
        order_value = (
            configured_order
            if configured_order is not None
            else get_fallback_period_order(sheet_name)
        )
        return order_value, sheet_name

    return sorted(period_names, key=sort_key)


def format_month(month_key):
    year, month = month_key.split("-")
    return f"Tháng {month}/{year}"


def get_month_key(sheet_name, month_config):
    """Chỉ lấy tháng từ sheet Cấu hình tháng, không suy ra từ ngày kết thúc."""
    return month_config.get(sheet_name, {}).get("month")


def build_monthly_ranking(evaluation_sheets, month_config):
    records = []

    for period_name, sheet in evaluation_sheets.items():
        config_row = month_config.get(period_name, {})
        if not config_row.get("include", True):
            continue

        month_key = get_month_key(period_name, month_config)
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
    monthly["Điểm TB/kỳ"] = monthly["Điểm xếp hạng"] / monthly["Số kỳ"]
    return monthly


def prepare_ranking_table(monthly_data, selected_month):
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
    """So sánh hạng và điểm trung bình mỗi kỳ với tháng liền trước có dữ liệu."""
    month_keys = sorted(monthly_data["Tháng"].dropna().unique().tolist())
    current_index = month_keys.index(selected_month)

    if current_index == 0:
        ranking["So với tháng trước"] = "—"
        return ranking, None

    previous_month = month_keys[current_index - 1]
    previous_ranking = prepare_ranking_table(monthly_data, previous_month)

    previous_rank_map = previous_ranking.set_index("Thành viên")["Xếp hạng"].to_dict()
    previous_average_map = previous_ranking.set_index("Thành viên")["Điểm TB/kỳ"].to_dict()

    comparison_text = []
    for _, row in ranking.iterrows():
        member = row["Thành viên"]
        if member not in previous_rank_map:
            comparison_text.append("Mới")
            continue

        rank_change = previous_rank_map[member] - row["Xếp hạng"]
        average_change = row["Điểm TB/kỳ"] - previous_average_map[member]

        if rank_change > 0:
            rank_text = f"↑ {rank_change} hạng"
        elif rank_change < 0:
            rank_text = f"↓ {abs(rank_change)} hạng"
        else:
            rank_text = "Giữ hạng"

        if average_change > 0:
            score_text = f"+{average_change:.2f} điểm TB/kỳ"
        elif average_change < 0:
            score_text = f"{average_change:.2f} điểm TB/kỳ"
        else:
            score_text = "0 điểm TB/kỳ"

        comparison_text.append(f"{rank_text}; {score_text}")

    ranking["So với tháng trước"] = comparison_text
    return ranking, previous_month


def prepare_stacked_data(df_long, criterion_col, list_criteria, category_col):
    df_chart = df_long.copy()
    df_chart["Số phiếu"] = pd.to_numeric(
        df_chart["Số phiếu"], errors="coerce"
    ).fillna(0)
    df_chart["Giá trị biểu đồ"] = df_chart["Số phiếu"]

    if len(list_criteria) >= 4:
        negative_criteria = list_criteria[2:]
        df_chart.loc[
            df_chart[criterion_col].isin(negative_criteria),
            "Giá trị biểu đồ",
        ] *= -1

    criterion_order = {criterion: index for index, criterion in enumerate(list_criteria)}
    df_chart["tc_cat_sort"] = df_chart[criterion_col].map(criterion_order)
    df_chart = df_chart.sort_values(
        [category_col, "tc_cat_sort"],
        ascending=[True, True],
    )

    df_chart["Vị trí nhãn"] = 0.0
    for category in df_chart[category_col].dropna().unique():
        mask = df_chart[category_col] == category
        positive_sum = 0.0
        negative_sum = 0.0

        for index, row in df_chart[mask].iterrows():
            value = row["Giá trị biểu đồ"]
            if value > 0:
                df_chart.loc[index, "Vị trí nhãn"] = positive_sum + value / 2.0
                positive_sum += value
            elif value < 0:
                df_chart.loc[index, "Vị trí nhãn"] = negative_sum + value / 2.0
                negative_sum += value

    df_chart["Nhãn phiếu"] = df_chart["Số phiếu"].round(0).astype(int)
    return df_chart


def plot_stacked_chart(
    df_long,
    criterion_col,
    list_criteria,
    category_col="Thành viên",
    category_sort=None,
    mobile_mode=False,
):
    df_chart = prepare_stacked_data(
        df_long,
        criterion_col,
        list_criteria,
        category_col,
    )
    df_text = df_chart[df_chart["Số phiếu"] != 0].copy()
    custom_colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]
    sort_order = category_sort

    color_encoding = alt.Color(
        f"{criterion_col}:N",
        scale=alt.Scale(domain=list_criteria, range=custom_colors),
        legend=alt.Legend(
            title="Tiêu chí đánh giá",
            orient="bottom",
            direction="vertical",
            labelLimit=1000,
        ),
    )

    tooltip = [
        alt.Tooltip(f"{category_col}:N"),
        alt.Tooltip(f"{criterion_col}:N"),
        alt.Tooltip("Số phiếu:Q", format=".0f"),
    ]

    if mobile_mode:
        unique_categories = len(df_chart[category_col].dropna().unique())
        chart_height = max(420, unique_categories * 52)

        bars = (
            alt.Chart(df_chart)
            .mark_bar(size=30)
            .encode(
                y=alt.Y(
                    f"{category_col}:N",
                    sort=sort_order,
                    title=None,
                    axis=alt.Axis(labelLimit=160),
                ),
                x=alt.X(
                    "Giá trị biểu đồ:Q",
                    title="Số phiếu đánh giá",
                    scale=alt.Scale(nice=False),
                ),
                color=color_encoding,
                order=alt.Order("tc_cat_sort:O", sort="ascending"),
                tooltip=tooltip,
            )
        )

        text = (
            alt.Chart(df_text)
            .mark_text(baseline="middle", align="center", fontWeight="bold")
            .encode(
                y=alt.Y(f"{category_col}:N", sort=sort_order),
                x=alt.X("Vị trí nhãn:Q", stack=None),
                text=alt.Text("Nhãn phiếu:Q", format="d"),
                color=alt.value("white"),
            )
        )

        zero_rule = (
            alt.Chart(pd.DataFrame({"Giá trị biểu đồ": [0]}))
            .mark_rule(color="#333333", strokeWidth=1.5)
            .encode(x="Giá trị biểu đồ:Q")
        )
        return (bars + text + zero_rule).properties(height=chart_height).interactive()

    unique_categories = len(df_chart[category_col].dropna().unique())
    chart_width = max(800, unique_categories * 90)

    bars = (
        alt.Chart(df_chart)
        .mark_bar(size=40)
        .encode(
            x=alt.X(
                f"{category_col}:N",
                sort=sort_order,
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelOverlap=False,
                    labelExpr="split(datum.value, ' ~ ')",
                    domain=False,
                    ticks=False,
                ),
            ),
            y=alt.Y(
                "Giá trị biểu đồ:Q",
                title="Số phiếu đánh giá",
                scale=alt.Scale(nice=False),
            ),
            color=color_encoding,
            order=alt.Order("tc_cat_sort:O", sort="ascending"),
            tooltip=tooltip,
        )
    )

    text = (
        alt.Chart(df_text)
        .mark_text(baseline="middle", align="center", fontWeight="bold")
        .encode(
            x=alt.X(f"{category_col}:N", sort=sort_order),
            y=alt.Y("Vị trí nhãn:Q", stack=None),
            text=alt.Text("Nhãn phiếu:Q", format="d"),
            color=alt.value("white"),
        )
    )

    zero_rule = (
        alt.Chart(pd.DataFrame({"Giá trị biểu đồ": [0]}))
        .mark_rule(color="#333333", strokeWidth=2)
        .encode(y="Giá trị biểu đồ:Q")
    )

    return (
        (bars + text + zero_rule)
        .properties(width=chart_width, height=500)
        .interactive()
    )


def build_member_trend(evaluation_sheets, month_config, selected_member):
    records = []
    ordered_periods = sort_period_names(list(evaluation_sheets.keys()), month_config)

    for sequence, period_name in enumerate(ordered_periods, start=1):
        df_clean = clean_sheet(evaluation_sheets[period_name])
        if df_clean.empty or selected_member not in df_clean.columns:
            continue

        criterion_col = df_clean.columns[0]
        member_data = df_clean[[criterion_col, selected_member]].copy()
        member_data["Số phiếu"] = pd.to_numeric(
            member_data[selected_member], errors="coerce"
        ).fillna(0)
        member_data["Mã tiêu chí"] = member_data[criterion_col].apply(
            get_criterion_number
        )

        positive = member_data.loc[
            member_data["Mã tiêu chí"].isin([1, 2]), "Số phiếu"
        ].sum()
        warning = member_data.loc[
            member_data["Mã tiêu chí"].isin([3, 4]), "Số phiếu"
        ].sum()

        configured_order = month_config.get(period_name, {}).get("order")
        order_value = configured_order if configured_order is not None else sequence

        records.append(
            {
                "Kỳ": get_split_week_name(period_name),
                "Tên sheet": period_name,
                "Thứ tự kỳ": order_value,
                "Phiếu đóng góp": float(positive),
                "Phiếu cảnh báo": float(warning),
                "Điểm tuần": float(positive - warning),
            }
        )

    trend = pd.DataFrame(records)
    if trend.empty:
        return trend

    trend = trend.sort_values(["Thứ tự kỳ", "Tên sheet"]).reset_index(drop=True)
    changes = trend["Điểm tuần"].diff()
    comparison = []
    for value in changes:
        if pd.isna(value):
            comparison.append("—")
        elif value > 0:
            comparison.append(f"↑ +{value:g}")
        elif value < 0:
            comparison.append(f"↓ {value:g}")
        else:
            comparison.append("Không đổi")
    trend["So với kỳ trước"] = comparison
    return trend


def plot_member_score_trend(member_trend, mobile_mode=False):
    chart_data = member_trend.copy()
    period_sort = chart_data["Kỳ"].tolist()

    line = (
        alt.Chart(chart_data)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(
                "Kỳ:N",
                sort=period_sort,
                title=None,
                axis=alt.Axis(
                    labelAngle=-35 if mobile_mode else 0,
                    labelExpr="split(datum.value, ' ~ ')",
                    labelLimit=130,
                ),
            ),
            y=alt.Y("Điểm tuần:Q", title="Điểm tuần"),
            tooltip=[
                alt.Tooltip("Kỳ:N"),
                alt.Tooltip("Phiếu đóng góp:Q", format=".0f"),
                alt.Tooltip("Phiếu cảnh báo:Q", format=".0f"),
                alt.Tooltip("Điểm tuần:Q", format=".0f"),
            ],
        )
    )

    labels = (
        alt.Chart(chart_data)
        .mark_text(dy=-12, fontWeight="bold")
        .encode(
            x=alt.X("Kỳ:N", sort=period_sort),
            y=alt.Y("Điểm tuần:Q"),
            text=alt.Text("Điểm tuần:Q", format=".0f"),
        )
    )

    zero_rule = (
        alt.Chart(pd.DataFrame({"Điểm tuần": [0]}))
        .mark_rule(color="#666666", strokeDash=[5, 5])
        .encode(y="Điểm tuần:Q")
    )

    return (line + labels + zero_rule).properties(height=330)


def plot_ranking_chart(ranking):
    chart_data = ranking.copy()
    chart_data["Nhãn điểm"] = chart_data["Điểm xếp hạng"].map(lambda value: f"{value:g}")

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
                alt.Tooltip("Xếp hạng:Q"),
                alt.Tooltip("Thành viên:N"),
                alt.Tooltip("Phiếu đóng góp:Q", format=".0f"),
                alt.Tooltip("Phiếu cảnh báo:Q", format=".0f"),
                alt.Tooltip("Điểm xếp hạng:Q", format=".0f"),
                alt.Tooltip("Điểm TB/kỳ:Q", format=".2f"),
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

    return (bars + text + zero_rule).properties(height=430)


def format_number(value, decimals=0):
    if pd.isna(value):
        return "—"
    if decimals == 0 and float(value).is_integer():
        return int(value)
    return round(float(value), decimals)


mobile_mode = st.sidebar.checkbox(
    "📱 Chế độ xem trên điện thoại",
    value=False,
    help="Chuyển các biểu đồ cột chồng sang dạng ngang để dễ đọc trên màn hình nhỏ.",
)

if st.sidebar.button("🔄 Làm mới dữ liệu", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("Dữ liệu được tự làm mới sau tối đa 5 phút.")

try:
    all_sheets = load_data()

    if not all_sheets:
        st.warning("File Excel chưa có sheet dữ liệu.")
        st.stop()

    config_sheet_name = find_config_sheet(all_sheets)
    config_sheet = all_sheets.get(config_sheet_name) if config_sheet_name else None
    month_config = build_month_config(config_sheet)

    evaluation_sheets = {
        name: sheet
        for name, sheet in all_sheets.items()
        if name != config_sheet_name
    }

    if not evaluation_sheets:
        st.warning("Workbook chưa có sheet đánh giá.")
        st.stop()

    ordered_period_names = sort_period_names(
        list(evaluation_sheets.keys()),
        month_config,
    )

    first_sheet = evaluation_sheets[ordered_period_names[0]]
    df_first = clean_sheet(first_sheet)
    if df_first.empty:
        st.warning("Sheet dữ liệu đầu tiên chưa có dữ liệu.")
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
        week_options = {
            get_display_name(name): name
            for name in ordered_period_names
        }
        week_labels = list(week_options.keys())
        selected_display_week = st.selectbox(
            "Chọn kỳ đánh giá:",
            week_labels,
            index=len(week_labels) - 1,
            key="selected_week",
        )
        selected_week = week_options[selected_display_week]

        df_raw = clean_sheet(evaluation_sheets[selected_week])
        criterion_col = df_raw.columns[0]
        df_long = df_raw.melt(
            id_vars=[criterion_col],
            var_name="Thành viên",
            value_name="Số phiếu",
        )

        st.altair_chart(
            plot_stacked_chart(
                df_long,
                criterion_col,
                global_criteria,
                category_col="Thành viên",
                category_sort=fixed_names,
                mobile_mode=mobile_mode,
            ),
            use_container_width=True,
        )

        with st.expander("📋 Số liệu chi tiết"):
            st.dataframe(df_raw, use_container_width=True, hide_index=True)

    with tab2:
        selected_member = st.selectbox(
            "🔍 Chọn thành viên:",
            fixed_names,
            key="selected_member",
        )

        stacked_records = []
        period_label_order = []

        for period_name in ordered_period_names:
            df_clean = clean_sheet(evaluation_sheets[period_name])
            if df_clean.empty:
                continue

            criterion_col = df_clean.columns[0]
            df_melted = df_clean.melt(
                id_vars=[criterion_col],
                var_name="Thành viên",
                value_name="Số phiếu",
            )
            df_member = df_melted[
                df_melted["Thành viên"] == selected_member
            ].copy()

            display_period = get_split_week_name(period_name)
            period_label_order.append(display_period)

            for _, row in df_member.iterrows():
                stacked_records.append(
                    {
                        "Kỳ": display_period,
                        criterion_col: row[criterion_col],
                        "Số phiếu": row["Số phiếu"],
                    }
                )

        df_stacked_trend = pd.DataFrame(stacked_records)
        if not df_stacked_trend.empty:
            criterion_col = df_stacked_trend.columns[1]
            st.subheader("Cơ cấu phiếu theo từng kỳ")
            st.altair_chart(
                plot_stacked_chart(
                    df_stacked_trend,
                    criterion_col,
                    global_criteria,
                    category_col="Kỳ",
                    category_sort=period_label_order,
                    mobile_mode=mobile_mode,
                ),
                use_container_width=True,
            )

            member_trend = build_member_trend(
                evaluation_sheets,
                month_config,
                selected_member,
            )

            if not member_trend.empty:
                st.subheader("Xu hướng điểm qua các kỳ")
                st.caption(
                    "Điểm tuần = phiếu đóng góp (Tiêu chí 1 + 2) − "
                    "phiếu cảnh báo (Tiêu chí 3 + 4)."
                )
                st.altair_chart(
                    plot_member_score_trend(member_trend, mobile_mode),
                    use_container_width=True,
                )

                trend_table = member_trend[
                    [
                        "Kỳ",
                        "Phiếu đóng góp",
                        "Phiếu cảnh báo",
                        "Điểm tuần",
                        "So với kỳ trước",
                    ]
                ].copy()
                for column in ["Phiếu đóng góp", "Phiếu cảnh báo", "Điểm tuần"]:
                    trend_table[column] = trend_table[column].map(format_number)

                st.dataframe(
                    trend_table,
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning("Chưa có dữ liệu cho thành viên này.")

    with tab3:
        if config_sheet_name is None:
            st.warning(
                "Chưa có sheet **Cấu hình tháng**. Hãy dùng file Excel mẫu và khai báo "
                "tháng xếp hạng cho từng sheet dữ liệu."
            )
        elif not month_config:
            st.warning(
                "Sheet **Cấu hình tháng** chưa có hai cột bắt buộc: "
                "**Tên sheet** và **Tháng xếp hạng**."
            )
        else:
            monthly_data = build_monthly_ranking(evaluation_sheets, month_config)

            unconfigured_periods = [
                name
                for name in ordered_period_names
                if name not in month_config or month_config[name].get("month") is None
            ]
            if unconfigured_periods:
                st.warning(
                    "Các kỳ sau chưa được tính vào bảng xếp hạng vì chưa khai báo tháng: "
                    + ", ".join(unconfigured_periods)
                )

            if monthly_data.empty:
                st.warning("Chưa có kỳ đánh giá nào được khai báo tháng hợp lệ.")
            else:
                month_keys = sorted(
                    monthly_data["Tháng"].unique().tolist(),
                    reverse=True,
                )
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
                    "**Điểm xếp hạng = tổng phiếu đóng góp (Tiêu chí 1 + 2) − "
                    "tổng phiếu cảnh báo (Tiêu chí 3 + 4).** "
                    "Tháng của từng kỳ được lấy trực tiếp từ sheet Cấu hình tháng. "
                    "Điểm TB/kỳ được dùng để so sánh mức thay đổi giữa các tháng."
                )

                top_members = ranking.head(3).to_dict("records")
                medals = ["🥇", "🥈", "🥉"]

                if mobile_mode:
                    for index, member in enumerate(top_members):
                        st.metric(
                            label=f"{medals[index]} Hạng {index + 1}",
                            value=member["Thành viên"],
                            delta=(
                                f'{member["Điểm xếp hạng"]:g} điểm | '
                                f'{member["Điểm TB/kỳ"]:.2f} điểm/kỳ'
                            ),
                            delta_color="off",
                        )
                else:
                    top_columns = st.columns(3)
                    for index, column in enumerate(top_columns):
                        with column:
                            if index < len(top_members):
                                member = top_members[index]
                                st.metric(
                                    label=f"{medals[index]} Hạng {index + 1}",
                                    value=member["Thành viên"],
                                    delta=(
                                        f'{member["Điểm xếp hạng"]:g} điểm | '
                                        f'{member["Điểm TB/kỳ"]:.2f} điểm/kỳ'
                                    ),
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
                    "Số kỳ",
                    "Điểm TB/kỳ",
                    "So với tháng trước",
                ]
                display_ranking = ranking[display_columns].copy()

                for column in [
                    "Phiếu đóng góp",
                    "Phiếu cảnh báo",
                    "Điểm xếp hạng",
                    "Số kỳ",
                ]:
                    display_ranking[column] = display_ranking[column].map(format_number)
                display_ranking["Điểm TB/kỳ"] = display_ranking["Điểm TB/kỳ"].map(
                    lambda value: format_number(value, decimals=2)
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
                    f"Dữ liệu tháng này gồm {number_of_periods} kỳ đánh giá"
                    f"{comparison_note}."
                )

except Exception as error:
    st.error(f"Lỗi: {error}")
