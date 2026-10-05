import datetime
import re
import unicodedata

import altair as alt
import pandas as pd
import streamlit as st


# ============================================================
# CẤU HÌNH TRANG
# ============================================================
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


# ============================================================
# NGUỒN DỮ LIỆU
# ============================================================
file_url = (
    "https://raw.githubusercontent.com/"
    "nmh21102003-a11y/web-danh-gia-du-an/main/Du_Lieu_Danh_Gia.xlsx"
)

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


@st.cache_data(ttl=60)
def load_data(cache_key):
    """Tải workbook mới nhất từ GitHub và tránh cache bản Excel cũ."""
    fresh_url = f"{file_url}?v={cache_key}"
    return pd.read_excel(
        fresh_url,
        sheet_name=None,
        engine="openpyxl",
    )


# ============================================================
# HÀM XỬ LÝ DỮ LIỆU CHUNG
# ============================================================
def remove_accents(value):
    text = unicodedata.normalize("NFD", str(value))
    return "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )


def normalized_key(value):
    return re.sub(
        r"\s+",
        " ",
        remove_accents(value).lower().strip(),
    )


def clean_sheet(sheet):
    """Làm sạch sheet đánh giá."""
    df = sheet.copy()

    df = df.loc[
        :,
        ~df.columns.astype(str).str.contains(r"^Unnamed")
    ].dropna(how="all")

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


def get_criterion_number(criterion_text):
    match = re.search(
        r"Tiêu chí\s*0?([1-4])",
        str(criterion_text),
        flags=re.IGNORECASE,
    )

    return int(match.group(1)) if match else None


def get_week_period(sheet_name):
    """Tính ngày bắt đầu/kết thúc chỉ để hiển thị ở tab tuần."""
    name = sheet_name.strip()

    is_week_one = re.search(
        r"Tuần\s*0?1(?!\d)",
        name,
        flags=re.IGNORECASE,
    )

    if "Pre-work" in name or is_week_one:
        return (
            datetime.date(2026, 6, 22),
            datetime.date(2026, 7, 7),
        )

    match = re.search(
        r"Tuần\s*(\d+)",
        name,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    week_number = int(match.group(1))

    if week_number < 2:
        return None

    base_end_date = datetime.date(2026, 7, 7)

    start_date = base_end_date + datetime.timedelta(
        days=1 + (week_number - 2) * 7
    )

    end_date = start_date + datetime.timedelta(days=6)

    return start_date, end_date


def format_date(date_value):
    return (
        f"{date_value.day:02d}/"
        f"{date_value.month:02d}/"
        f"{date_value.year}"
    )


def get_display_name(sheet_name):
    """Tên tuần đầy đủ trong hộp chọn."""
    name = sheet_name.strip()
    clean_name = name

    if "Phiếu Đánh Giá" in name:
        clean_name = (
            "Phiếu Đánh Giá "
            + name.split("Phiếu Đánh Giá")[-1].strip()
        )

    period = get_week_period(sheet_name)

    if period is None:
        return clean_name

    start_date, end_date = period

    return (
        f"{clean_name} "
        f"(từ ngày {format_date(start_date)} "
        f"đến ngày {format_date(end_date)})"
    )


def get_split_week_name(sheet_name):
    """Tên ngắn của tuần để hiển thị trên biểu đồ."""
    name = sheet_name.strip()

    if "Phiếu Đánh Giá" in name:
        suffix = name.split("Phiếu Đánh Giá")[-1].strip()
        return f"Phiếu Đánh Giá ~ {suffix}"

    return name


def get_fallback_week_order(sheet_name):
    """Thứ tự tuần dự phòng nếu sheet cấu hình chưa khai báo."""
    name = sheet_name.strip()

    if "Pre-work" in name:
        return 1

    match = re.search(
        r"Tuần\s*(\d+)",
        name,
        flags=re.IGNORECASE,
    )

    if match:
        return int(match.group(1))

    return 9999


# ============================================================
# SHEET CẤU HÌNH THÁNG
# ============================================================
def parse_month_value(value):
    """Nhận 07/2026, 2026-07 hoặc ô ngày trong Excel."""
    if value is None or pd.isna(value):
        return None

    if isinstance(
        value,
        (pd.Timestamp, datetime.datetime, datetime.date),
    ):
        return value.strftime("%Y-%m")

    text = str(value).strip()

    match = re.search(
        r"(?<!\d)(0?[1-9]|1[0-2])\s*[/\-]\s*(20\d{2})(?!\d)",
        text,
    )

    if match:
        month = int(match.group(1))
        year = int(match.group(2))
        return f"{year:04d}-{month:02d}"

    match = re.search(
        r"(?<!\d)(20\d{2})\s*[/\-]\s*(0?[1-9]|1[0-2])(?!\d)",
        text,
    )

    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return f"{year:04d}-{month:02d}"

    return None


def find_config_sheet(all_sheets):
    """Tìm sheet Cấu hình tháng, kể cả trường hợp bỏ dấu."""
    for sheet_name in all_sheets:
        key = normalized_key(sheet_name).replace("_", " ")

        if key == "cau hinh thang":
            return sheet_name

    return None


def build_month_config(config_sheet):
    """Đọc sheet Cấu hình tháng."""
    if config_sheet is None or config_sheet.empty:
        return {}

    config = config_sheet.copy().dropna(how="all")

    config.columns = [
        str(column).strip()
        for column in config.columns
    ]

    column_map = {
        normalized_key(column): column
        for column in config.columns
    }

    sheet_column = column_map.get("ten sheet")
    month_column = column_map.get("thang xep hang")

    order_column = (
        column_map.get("thu tu tuan")
        or column_map.get("thu tu ky")
    )

    include_column = column_map.get("tinh vao bxh")

    if sheet_column is None or month_column is None:
        return {}

    result = {}

    for _, row in config.iterrows():
        raw_sheet_name = row.get(sheet_column)

        if raw_sheet_name is None or pd.isna(raw_sheet_name):
            continue

        sheet_name = str(raw_sheet_name).strip()

        month_key = parse_month_value(
            row.get(month_column)
        )

        raw_order = (
            row.get(order_column)
            if order_column is not None
            else None
        )

        order_value = pd.to_numeric(
            raw_order,
            errors="coerce",
        )

        order_value = (
            int(order_value)
            if pd.notna(order_value)
            else None
        )

        raw_include = (
            row.get(include_column)
            if include_column is not None
            else "Có"
        )

        include_text = normalized_key(raw_include)

        include = include_text not in {
            "khong",
            "no",
            "false",
            "0",
        }

        result[sheet_name] = {
            "month": month_key,
            "order": order_value,
            "include": include,
        }

    return result


def sort_week_names(week_names, month_config):

    def sort_key(sheet_name):

        configured_order = month_config.get(
            sheet_name,
            {},
        ).get("order")

        order_value = (
            configured_order
            if configured_order is not None
            else get_fallback_week_order(sheet_name)
        )

        return order_value, sheet_name

    return sorted(
        week_names,
        key=sort_key,
    )


def format_month(month_key):
    year, month = month_key.split("-")
    return f"Tháng {month}/{year}"


# ============================================================
# BIỂU ĐỒ CỘT CHỒNG
# ============================================================
def prepare_stacked_data(
    df_long,
    criterion_col,
    list_criteria,
    category_col,
):

    df_chart = df_long.copy()

    df_chart["Số phiếu"] = pd.to_numeric(
        df_chart["Số phiếu"],
        errors="coerce",
    ).fillna(0)

    df_chart["Giá trị biểu đồ"] = df_chart["Số phiếu"]

    if len(list_criteria) >= 4:

        negative_criteria = list_criteria[2:]

        df_chart.loc[
            df_chart[criterion_col].isin(
                negative_criteria
            ),
            "Giá trị biểu đồ",
        ] *= -1

    criterion_order = {
        criterion: index
        for index, criterion in enumerate(
            list_criteria
        )
    }

    df_chart["tc_cat_sort"] = (
        df_chart[criterion_col]
        .map(criterion_order)
    )

    df_chart = df_chart.sort_values(
        [
            category_col,
            "tc_cat_sort",
        ]
    )

    df_chart["Vị trí nhãn"] = 0.0

    for category in (
        df_chart[category_col]
        .dropna()
        .unique()
    ):

        mask = (
            df_chart[category_col]
            == category
        )

        positive_sum = 0.0
        negative_sum = 0.0

        for index, row in (
            df_chart[mask]
            .iterrows()
        ):

            value = row[
                "Giá trị biểu đồ"
            ]

            if value > 0:

                df_chart.loc[
                    index,
                    "Vị trí nhãn",
                ] = (
                    positive_sum
                    + value / 2
                )

                positive_sum += value

            elif value < 0:

                df_chart.loc[
                    index,
                    "Vị trí nhãn",
                ] = (
                    negative_sum
                    + value / 2
                )

                negative_sum += value

    df_chart["Nhãn phiếu"] = (
        df_chart[
            "Giá trị biểu đồ"
        ]
        .round()
        .astype(int)
    )

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

    df_text = df_chart[
        df_chart["Số phiếu"] != 0
    ].copy()

    colors = [
        "#3498db",
        "#2ecc71",
        "#f39c12",
        "#e74c3c",
    ]

    color_encoding = alt.Color(
        f"{criterion_col}:N",
        scale=alt.Scale(
            domain=list_criteria,
            range=colors,
        ),
        legend=alt.Legend(
            title="Tiêu chí đánh giá",
            orient="bottom",
            direction="vertical",
            labelLimit=1000,
        ),
    )

    tooltip = [
        alt.Tooltip(
            f"{category_col}:N"
        ),
        alt.Tooltip(
            f"{criterion_col}:N"
        ),
        alt.Tooltip(
            "Giá trị biểu đồ:Q",
            title="Số phiếu",
            format=".0f",
        ),
    ]

    if mobile_mode:

        unique_categories = len(
            df_chart[
                category_col
            ].unique()
        )

        chart_height = max(
            420,
            unique_categories * 52,
        )

        bars = (
            alt.Chart(df_chart)
            .mark_bar(size=30)
            .encode(

                y=alt.Y(
                    f"{category_col}:N",
                    sort=category_sort,
                    title=None,
                    axis=alt.Axis(
                        labelLimit=160
                    ),
                ),

                x=alt.X(
                    "Giá trị biểu đồ:Q",
                    title="Số phiếu đánh giá",
                ),

                color=color_encoding,

                order=alt.Order(
                    "tc_cat_sort:O",
                    sort="ascending",
                ),

                tooltip=tooltip,
            )
        )

        text = (
            alt.Chart(df_text)
            .mark_text(
                baseline="middle",
                align="center",
                fontWeight="bold",
            )
            .encode(

                y=alt.Y(
                    f"{category_col}:N",
                    sort=category_sort,
                ),

                x=alt.X(
                    "Vị trí nhãn:Q"
                ),

                text=alt.Text(
                    "Nhãn phiếu:Q",
                    format="d",
                ),

                color=alt.value(
                    "white"
                ),
            )
        )

        zero_rule = (
            alt.Chart(
                pd.DataFrame(
                    {
                        "Giá trị biểu đồ": [
                            0
                        ]
                    }
                )
            )
            .mark_rule(
                color="#333333"
            )
            .encode(
                x="Giá trị biểu đồ:Q"
            )
        )

        return (
            bars
            + text
            + zero_rule
        ).properties(
            height=chart_height
        ).interactive()

    chart_width = max(
        800,
        len(
            df_chart[
                category_col
            ].unique()
        ) * 90,
    )

    bars = (
        alt.Chart(df_chart)
        .mark_bar(size=40)
        .encode(

            x=alt.X(
                f"{category_col}:N",
                sort=category_sort,
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelOverlap=False,
                    labelExpr=(
                        "split(datum.value, ' ~ ')"
                    ),
                    domain=False,
                    ticks=False,
                ),
            ),

            y=alt.Y(
                "Giá trị biểu đồ:Q",
                title="Số phiếu đánh giá",
            ),

            color=color_encoding,

            order=alt.Order(
                "tc_cat_sort:O",
                sort="ascending",
            ),

            tooltip=tooltip,
        )
    )

    text = (
        alt.Chart(df_text)
        .mark_text(
            baseline="middle",
            align="center",
            fontWeight="bold",
        )
        .encode(

            x=alt.X(
                f"{category_col}:N",
                sort=category_sort,
            ),

            y=alt.Y(
                "Vị trí nhãn:Q"
            ),

            text=alt.Text(
                "Nhãn phiếu:Q",
                format="d",
            ),

            color=alt.value(
                "white"
            ),
        )
    )

    zero_rule = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Giá trị biểu đồ": [
                        0
                    ]
                }
            )
        )
        .mark_rule(
            color="#333333",
            strokeWidth=2,
        )
        .encode(
            y="Giá trị biểu đồ:Q"
        )
    )

    return (
        bars
        + text
        + zero_rule
    ).properties(
        width=chart_width,
        height=500,
    ).interactive()


# ============================================================
# DỮ LIỆU XU HƯỚNG CỦA MỖI THÀNH VIÊN
# ============================================================
def build_member_trend(
    evaluation_sheets,
    month_config,
    selected_member,
):

    records = []

    ordered_weeks = sort_week_names(
        list(
            evaluation_sheets.keys()
        ),
        month_config,
    )

    for sequence, week_name in enumerate(
        ordered_weeks,
        start=1,
    ):

        df_clean = clean_sheet(
            evaluation_sheets[
                week_name
            ]
        )

        if (
            df_clean.empty
            or selected_member
            not in df_clean.columns
        ):
            continue

        criterion_col = (
            df_clean.columns[0]
        )

        member_data = df_clean[
            [
                criterion_col,
                selected_member,
            ]
        ].copy()

        member_data["Số phiếu"] = (
            pd.to_numeric(
                member_data[
                    selected_member
                ],
                errors="coerce",
            )
            .fillna(0)
        )

        member_data[
            "Mã tiêu chí"
        ] = (
            member_data[
                criterion_col
            ]
            .apply(
                get_criterion_number
            )
        )

        positive = (
            member_data.loc[
                member_data[
                    "Mã tiêu chí"
                ].isin(
                    [1, 2]
                ),
                "Số phiếu",
            ]
            .sum()
        )

        warning = (
            member_data.loc[
                member_data[
                    "Mã tiêu chí"
                ].isin(
                    [3, 4]
                ),
                "Số phiếu",
            ]
            .sum()
        )

        configured_order = (
            month_config.get(
                week_name,
                {},
            ).get(
                "order"
            )
        )

        order_value = (
            configured_order
            if configured_order
            is not None
            else sequence
        )

        records.append(
            {
                "Tuần":
                    get_split_week_name(
                        week_name
                    ),

                "Tên sheet":
                    week_name,

                "Thứ tự tuần":
                    order_value,

                "Phiếu đóng góp":
                    float(
                        positive
                    ),

                "Phiếu cảnh báo":
                    float(
                        warning
                    ),

                "Điểm tuần":
                    float(
                        positive
                        - warning
                    ),
            }
        )

    trend = pd.DataFrame(
        records
    )

    if trend.empty:
        return trend

    trend = (
        trend
        .sort_values(
            [
                "Thứ tự tuần",
                "Tên sheet",
            ]
        )
        .reset_index(
            drop=True
        )
    )

    changes = (
        trend[
            "Điểm tuần"
        ]
        .diff()
    )

    comparison = []

    for value in changes:

        if pd.isna(value):

            comparison.append(
                "—"
            )

        elif value > 0:

            comparison.append(
                f"↑ +{value:g}"
            )

        elif value < 0:

            comparison.append(
                f"↓ {value:g}"
            )

        else:

            comparison.append(
                "Không đổi"
            )

    trend[
        "So với tuần trước"
    ] = comparison

    return trend


def plot_member_score_trend(
    member_trend,
    mobile_mode=False,
):

    chart_data = (
        member_trend.copy()
    )

    week_sort = (
        chart_data[
            "Tuần"
        ].tolist()
    )

    line = (
        alt.Chart(
            chart_data
        )
        .mark_line(
            point=True,
            strokeWidth=3,
        )
        .encode(

            x=alt.X(
                "Tuần:N",
                sort=week_sort,
                title=None,
                axis=alt.Axis(
                    labelAngle=(
                        -35
                        if mobile_mode
                        else 0
                    ),
                    labelExpr=(
                        "split(datum.value, ' ~ ')"
                    ),
                ),
            ),

            y=alt.Y(
                "Điểm tuần:Q",
                title="Điểm tuần",
            ),

            tooltip=[
                alt.Tooltip(
                    "Tuần:N"
                ),
                alt.Tooltip(
                    "Phiếu đóng góp:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phiếu cảnh báo:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Điểm tuần:Q",
                    format=".0f",
                ),
            ],
        )
    )

    labels = (
        alt.Chart(
            chart_data
        )
        .mark_text(
            dy=-12,
            fontWeight="bold",
        )
        .encode(

            x=alt.X(
                "Tuần:N",
                sort=week_sort,
            ),

            y=alt.Y(
                "Điểm tuần:Q"
            ),

            text=alt.Text(
                "Điểm tuần:Q",
                format=".0f",
            ),
        )
    )

    zero_rule = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Điểm tuần": [
                        0
                    ]
                }
            )
        )
        .mark_rule(
            color="#666666",
            strokeDash=[
                5,
                5,
            ],
        )
        .encode(
            y="Điểm tuần:Q"
        )
    )

    return (
        line
        + labels
        + zero_rule
    ).properties(
        height=330
    )


# ============================================================
# XẾP HẠNG THEO THÁNG
# ============================================================
def build_monthly_ranking(
    evaluation_sheets,
    month_config,
):

    records = []

    for week_name, sheet in (
        evaluation_sheets.items()
    ):

        config_row = (
            month_config.get(
                week_name,
                {},
            )
        )

        if not config_row.get(
            "include",
            True,
        ):
            continue

        month_key = (
            config_row.get(
                "month"
            )
        )

        if month_key is None:
            continue

        df_clean = clean_sheet(
            sheet
        )

        if df_clean.empty:
            continue

        criterion_col = (
            df_clean.columns[0]
        )

        df_long = (
            df_clean.melt(
                id_vars=[
                    criterion_col
                ],
                var_name=(
                    "Thành viên"
                ),
                value_name=(
                    "Số phiếu"
                ),
            )
        )

        df_long[
            "Số phiếu"
        ] = (
            pd.to_numeric(
                df_long[
                    "Số phiếu"
                ],
                errors="coerce",
            )
            .fillna(0)
        )

        df_long[
            "Mã tiêu chí"
        ] = (
            df_long[
                criterion_col
            ]
            .apply(
                get_criterion_number
            )
        )

        df_long = (
            df_long[
                df_long[
                    "Thành viên"
                ].isin(
                    fixed_names
                )
                &
                df_long[
                    "Mã tiêu chí"
                ].isin(
                    [
                        1,
                        2,
                        3,
                        4,
                    ]
                )
            ]
        )

        positive_votes = (
            df_long[
                df_long[
                    "Mã tiêu chí"
                ].isin(
                    [
                        1,
                        2,
                    ]
                )
            ]
            .groupby(
                "Thành viên"
            )[
                "Số phiếu"
            ]
            .sum()
        )

        warning_votes = (
            df_long[
                df_long[
                    "Mã tiêu chí"
                ].isin(
                    [
                        3,
                        4,
                    ]
                )
            ]
            .groupby(
                "Thành viên"
            )[
                "Số phiếu"
            ]
            .sum()
        )

        for member in fixed_names:

            records.append(
                {
                    "Tháng":
                        month_key,

                    "Thành viên":
                        member,

                    "Phiếu đóng góp":
                        float(
                            positive_votes.get(
                                member,
                                0,
                            )
                        ),

                    "Phiếu cảnh báo":
                        float(
                            warning_votes.get(
                                member,
                                0,
                            )
                        ),

                    "Số tuần":
                        1,
                }
            )

    if not records:
        return pd.DataFrame()

    monthly = pd.DataFrame(
        records
    )

    monthly = (
        monthly
        .groupby(
            [
                "Tháng",
                "Thành viên",
            ],
            as_index=False,
        )
        .agg(
            {
                "Phiếu đóng góp":
                    "sum",

                "Phiếu cảnh báo":
                    "sum",

                "Số tuần":
                    "sum",
            }
        )
    )

    monthly[
        "Điểm xếp hạng"
    ] = (
        monthly[
            "Phiếu đóng góp"
        ]
        -
        monthly[
            "Phiếu cảnh báo"
        ]
    )

    return monthly


def prepare_ranking_table(
    monthly_data,
    selected_month,
):

    ranking = (
        monthly_data[
            monthly_data[
                "Tháng"
            ]
            == selected_month
        ]
        .copy()
    )

    ranking = (
        ranking
        .sort_values(
            by=[
                "Điểm xếp hạng",
                "Phiếu đóng góp",
                "Phiếu cảnh báo",
                "Thành viên",
            ],
            ascending=[
                False,
                False,
                True,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    ranking.insert(
        0,
        "Xếp hạng",
        range(
            1,
            len(ranking)
            + 1,
        ),
    )

    ranking[
        "Hạng"
    ] = (
        ranking[
            "Xếp hạng"
        ]
        .map(
            {
                1: "🥇 1",
                2: "🥈 2",
                3: "🥉 3",
            }
        )
        .fillna(
            ranking[
                "Xếp hạng"
            ]
            .astype(str)
        )
    )

    return ranking


def add_previous_month_comparison(
    ranking,
    monthly_data,
    selected_month,
):

    month_keys = sorted(
        monthly_data[
            "Tháng"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    current_index = (
        month_keys.index(
            selected_month
        )
    )

    if current_index == 0:

        ranking[
            "So với tháng trước"
        ] = "—"

        return (
            ranking,
            None,
        )

    previous_month = (
        month_keys[
            current_index - 1
        ]
    )

    previous_ranking = (
        prepare_ranking_table(
            monthly_data,
            previous_month,
        )
    )

    previous_rank_map = (
        previous_ranking
        .set_index(
            "Thành viên"
        )[
            "Xếp hạng"
        ]
        .to_dict()
    )

    comparison_text = []

    for _, row in (
        ranking.iterrows()
    ):

        member = row[
            "Thành viên"
        ]

        if member not in (
            previous_rank_map
        ):

            comparison_text.append(
                "Mới"
            )

            continue

        rank_change = (
            previous_rank_map[
                member
            ]
            -
            row[
                "Xếp hạng"
            ]
        )

        if rank_change > 0:

            comparison_text.append(
                f"↑ {rank_change} hạng"
            )

        elif rank_change < 0:

            comparison_text.append(
                f"↓ {abs(rank_change)} hạng"
            )

        else:

            comparison_text.append(
                "Giữ hạng"
            )

    ranking[
        "So với tháng trước"
    ] = comparison_text

    return (
        ranking,
        previous_month,
    )


def plot_ranking_chart(
    ranking,
):

    chart_data = (
        ranking.copy()
    )

    chart_data[
        "Nhãn điểm"
    ] = (
        chart_data[
            "Điểm xếp hạng"
        ]
        .map(
            lambda value:
            f"{value:g}"
        )
    )

    bars = (
        alt.Chart(
            chart_data
        )
        .mark_bar(
            cornerRadiusEnd=5
        )
        .encode(

            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(
                    field="Xếp hạng",
                    order="ascending",
                ),
                title=None,
            ),

            x=alt.X(
                "Điểm xếp hạng:Q",
                title="Điểm xếp hạng",
            ),

            color=alt.condition(
                alt.datum[
                    "Điểm xếp hạng"
                ] >= 0,
                alt.value(
                    "#2ecc71"
                ),
                alt.value(
                    "#e74c3c"
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "Xếp hạng:Q"
                ),
                alt.Tooltip(
                    "Thành viên:N"
                ),
                alt.Tooltip(
                    "Phiếu đóng góp:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phiếu cảnh báo:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Điểm xếp hạng:Q",
                    format=".0f",
                ),
            ],
        )
    )

    text = (
        alt.Chart(
            chart_data
        )
        .mark_text(
            dx=5,
            align="left",
            fontWeight="bold",
        )
        .encode(

            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(
                    field="Xếp hạng",
                    order="ascending",
                ),
            ),

            x=alt.X(
                "Điểm xếp hạng:Q"
            ),

            text=(
                "Nhãn điểm:N"
            ),
        )
    )

    zero_rule = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Điểm xếp hạng":
                    [
                        0
                    ]
                }
            )
        )
        .mark_rule(
            color="#333333"
        )
        .encode(
            x="Điểm xếp hạng:Q"
        )
    )

    return (
        bars
        + text
        + zero_rule
    ).properties(
        height=430
    )


# ============================================================
# ĐÁNH GIÁ CẢ QUÁ TRÌNH
# ============================================================
def build_overall_ranking(
    evaluation_sheets,
    month_config,
):

    records = []

    for member in fixed_names:

        trend = build_member_trend(
            evaluation_sheets,
            month_config,
            member,
        )

        if trend.empty:

            positive_votes = 0
            warning_votes = 0
            total_score = 0
            number_of_weeks = 0

        else:

            positive_votes = (
                trend[
                    "Phiếu đóng góp"
                ]
                .sum()
            )

            warning_votes = (
                trend[
                    "Phiếu cảnh báo"
                ]
                .sum()
            )

            total_score = (
                trend[
                    "Điểm tuần"
                ]
                .sum()
            )

            number_of_weeks = (
                len(trend)
            )

        records.append(
            {
                "Thành viên":
                    member,

                "Phiếu đóng góp":
                    float(
                        positive_votes
                    ),

                "Phiếu cảnh báo":
                    float(
                        warning_votes
                    ),

                "Tổng điểm":
                    float(
                        total_score
                    ),

                "Số tuần":
                    int(
                        number_of_weeks
                    ),
            }
        )

    ranking = pd.DataFrame(
        records
    )

    ranking = (
        ranking
        .sort_values(
            by=[
                "Tổng điểm",
                "Phiếu đóng góp",
                "Phiếu cảnh báo",
                "Thành viên",
            ],
            ascending=[
                False,
                False,
                True,
                True,
            ],
        )
        .reset_index(
            drop=True
        )
    )

    ranking.insert(
        0,
        "Xếp hạng",
        range(
            1,
            len(ranking)
            + 1
        ),
    )

    ranking[
        "Hạng"
    ] = (
        ranking[
            "Xếp hạng"
        ]
        .map(
            {
                1: "🥇 1",
                2: "🥈 2",
                3: "🥉 3",
            }
        )
        .fillna(
            ranking[
                "Xếp hạng"
            ].astype(str)
        )
    )

    return ranking


def build_cumulative_trend(
    evaluation_sheets,
    month_config,
):

    all_member_data = []

    for member in fixed_names:

        trend = build_member_trend(
            evaluation_sheets,
            month_config,
            member,
        )

        if trend.empty:
            continue

        member_trend = (
            trend.copy()
        )

        member_trend[
            "Thành viên"
        ] = member

        member_trend[
            "Điểm tích lũy"
        ] = (
            member_trend[
                "Điểm tuần"
            ]
            .cumsum()
        )

        all_member_data.append(
            member_trend
        )

    if not all_member_data:
        return pd.DataFrame()

    return pd.concat(
        all_member_data,
        ignore_index=True,
    )


def plot_overall_ranking_chart(
    ranking,
):

    chart_data = (
        ranking.copy()
    )

    chart_data[
        "Nhãn điểm"
    ] = (
        chart_data[
            "Tổng điểm"
        ]
        .map(
            lambda value:
            f"{value:g}"
        )
    )

    bars = (
        alt.Chart(
            chart_data
        )
        .mark_bar(
            cornerRadiusEnd=5
        )
        .encode(

            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(
                    field="Xếp hạng",
                    order="ascending",
                ),
                title=None,
            ),

            x=alt.X(
                "Tổng điểm:Q",
                title=(
                    "Tổng điểm cả quá trình"
                ),
            ),

            color=alt.condition(
                alt.datum[
                    "Tổng điểm"
                ] >= 0,
                alt.value(
                    "#2ecc71"
                ),
                alt.value(
                    "#e74c3c"
                ),
            ),

            tooltip=[
                alt.Tooltip(
                    "Xếp hạng:Q"
                ),
                alt.Tooltip(
                    "Thành viên:N"
                ),
                alt.Tooltip(
                    "Phiếu đóng góp:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phiếu cảnh báo:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Tổng điểm:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Số tuần:Q",
                    format=".0f",
                ),
            ],
        )
    )

    labels = (
        alt.Chart(
            chart_data
        )
        .mark_text(
            dx=6,
            align="left",
            fontWeight="bold",
        )
        .encode(

            y=alt.Y(
                "Thành viên:N",
                sort=alt.SortField(
                    field="Xếp hạng",
                    order="ascending",
                ),
            ),

            x=alt.X(
                "Tổng điểm:Q"
            ),

            text=(
                "Nhãn điểm:N"
            ),
        )
    )

    zero_rule = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Tổng điểm":
                    [
                        0
                    ]
                }
            )
        )
        .mark_rule(
            color="#333333"
        )
        .encode(
            x="Tổng điểm:Q"
        )
    )

    return (
        bars
        + labels
        + zero_rule
    ).properties(
        height=430
    )


def plot_cumulative_score_trend(
    cumulative_data,
    selected_members,
    mobile_mode=False,
):

    chart_data = (
        cumulative_data[
            cumulative_data[
                "Thành viên"
            ].isin(
                selected_members
            )
        ]
        .copy()
    )

    if chart_data.empty:
        return None

    week_order = (
        chart_data[
            [
                "Tuần",
                "Thứ tự tuần",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            [
                "Thứ tự tuần",
                "Tuần",
            ]
        )[
            "Tuần"
        ]
        .tolist()
    )

    line_chart = (
        alt.Chart(
            chart_data
        )
        .mark_line(
            point=True,
            strokeWidth=2.5,
        )
        .encode(

            x=alt.X(
                "Tuần:N",
                sort=week_order,
                title=None,
                axis=alt.Axis(
                    labelAngle=(
                        -35
                        if mobile_mode
                        else 0
                    ),
                    labelExpr=(
                        "split(datum.value, ' ~ ')"
                    ),
                ),
            ),

            y=alt.Y(
                "Điểm tích lũy:Q",
                title=(
                    "Điểm tích lũy"
                ),
            ),

            color=alt.Color(
                "Thành viên:N",
                title="Thành viên",
            ),

            tooltip=[
                alt.Tooltip(
                    "Thành viên:N"
                ),
                alt.Tooltip(
                    "Tuần:N"
                ),
                alt.Tooltip(
                    "Phiếu đóng góp:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phiếu cảnh báo:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Điểm tuần:Q",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Điểm tích lũy:Q",
                    format=".0f",
                ),
            ],
        )
        .properties(
            height=420
        )
        .interactive()
    )

    zero_rule = (
        alt.Chart(
            pd.DataFrame(
                {
                    "Điểm tích lũy":
                    [
                        0
                    ]
                }
            )
        )
        .mark_rule(
            color="#777777",
            strokeDash=[
                5,
                5,
            ],
        )
        .encode(
            y="Điểm tích lũy:Q"
        )
    )

    return (
        line_chart
        + zero_rule
    )


def format_number(
    value,
):

    if pd.isna(value):
        return "—"

    if float(
        value
    ).is_integer():

        return int(
            value
        )

    return round(
        float(value),
        2,
    )


# ============================================================
# THANH BÊN
# ============================================================
mobile_mode = (
    st.sidebar.checkbox(
        "📱 Chế độ xem trên điện thoại",
        value=False,
    )
)

if st.sidebar.button(
    "🔄 Làm mới dữ liệu",
    use_container_width=True,
):

    st.cache_data.clear()

    st.rerun()

st.sidebar.caption(
    "Dữ liệu được tự làm mới sau tối đa 1 phút."
)


# ============================================================
# CHƯƠNG TRÌNH CHÍNH
# ============================================================
try:

    cache_key = int(
        datetime.datetime.now()
        .timestamp()
        // 60
    )

    all_sheets = load_data(
        cache_key
    )

    if not all_sheets:

        st.warning(
            "File Excel chưa có sheet dữ liệu."
        )

        st.stop()

    config_sheet_name = (
        find_config_sheet(
            all_sheets
        )
    )

    config_sheet = (
        all_sheets.get(
            config_sheet_name
        )
        if config_sheet_name
        else None
    )

    month_config = (
        build_month_config(
            config_sheet
        )
    )

    evaluation_sheets = {
        name: sheet
        for name, sheet
        in all_sheets.items()
        if name
        != config_sheet_name
    }

    if not evaluation_sheets:

        st.warning(
            "Workbook chưa có sheet đánh giá."
        )

        st.stop()

    ordered_week_names = (
        sort_week_names(
            list(
                evaluation_sheets.keys()
            ),
            month_config,
        )
    )

    first_sheet = (
        evaluation_sheets[
            ordered_week_names[
                0
            ]
        ]
    )

    df_first = clean_sheet(
        first_sheet
    )

    if df_first.empty:

        st.warning(
            "Sheet dữ liệu đầu tiên chưa có dữ liệu."
        )

        st.stop()

    global_criterion_col = (
        df_first.columns[0]
    )

    global_criteria = (
        df_first[
            global_criterion_col
        ]
        .dropna()
        .unique()
        .tolist()
    )

    tab1, tab2, tab3, tab4 = (
        st.tabs(
            [
                "📅 Đánh Giá Từng Tuần",
                "📈 Tổng Hợp Cá Nhân Theo Tuần",
                "🏆 Xếp Hạng Theo Tháng",
                "📊 Đánh Giá Cả Quá Trình",
            ]
        )
    )


    # ========================================================
    # TAB 1
    # ========================================================
    with tab1:

        week_options = {
            get_display_name(
                name
            ): name
            for name
            in ordered_week_names
        }

        week_labels = list(
            week_options.keys()
        )

        selected_display_week = (
            st.selectbox(
                "Chọn tuần đánh giá:",
                week_labels,
                index=(
                    len(
                        week_labels
                    ) - 1
                ),
            )
        )

        selected_week = (
            week_options[
                selected_display_week
            ]
        )

        df_raw = clean_sheet(
            evaluation_sheets[
                selected_week
            ]
        )

        criterion_col = (
            df_raw.columns[0]
        )

        df_long = df_raw.melt(
            id_vars=[
                criterion_col
            ],
            var_name=(
                "Thành viên"
            ),
            value_name=(
                "Số phiếu"
            ),
        )

        st.altair_chart(
            plot_stacked_chart(
                df_long,
                criterion_col,
                global_criteria,
                category_col=(
                    "Thành viên"
                ),
                category_sort=(
                    fixed_names
                ),
                mobile_mode=(
                    mobile_mode
                ),
            ),
            use_container_width=True,
        )

        with st.expander(
            "📋 Số liệu chi tiết"
        ):

            st.dataframe(
                df_raw,
                use_container_width=True,
                hide_index=True,
            )


    # ========================================================
    # TAB 2
    # ========================================================
    with tab2:

        selected_member = (
            st.selectbox(
                "🔍 Chọn thành viên:",
                fixed_names,
            )
        )

        stacked_records = []

        week_label_order = []

        for week_name in (
            ordered_week_names
        ):

            df_clean = clean_sheet(
                evaluation_sheets[
                    week_name
                ]
            )

            if df_clean.empty:
                continue

            criterion_col = (
                df_clean.columns[0]
            )

            df_melted = (
                df_clean.melt(
                    id_vars=[
                        criterion_col
                    ],
                    var_name=(
                        "Thành viên"
                    ),
                    value_name=(
                        "Số phiếu"
                    ),
                )
            )

            df_member = (
                df_melted[
                    df_melted[
                        "Thành viên"
                    ]
                    == selected_member
                ]
                .copy()
            )

            display_week = (
                get_split_week_name(
                    week_name
                )
            )

            week_label_order.append(
                display_week
            )

            for _, row in (
                df_member.iterrows()
            ):

                stacked_records.append(
                    {
                        "Tuần":
                            display_week,

                        criterion_col:
                            row[
                                criterion_col
                            ],

                        "Số phiếu":
                            row[
                                "Số phiếu"
                            ],
                    }
                )

        df_stacked_trend = (
            pd.DataFrame(
                stacked_records
            )
        )

        if not (
            df_stacked_trend.empty
        ):

            criterion_col = (
                df_stacked_trend
                .columns[1]
            )

            st.subheader(
                "Số phiếu theo từng tuần"
            )

            st.altair_chart(
                plot_stacked_chart(
                    df_stacked_trend,
                    criterion_col,
                    global_criteria,
                    category_col=(
                        "Tuần"
                    ),
                    category_sort=(
                        week_label_order
                    ),
                    mobile_mode=(
                        mobile_mode
                    ),
                ),
                use_container_width=True,
            )

            member_trend = (
                build_member_trend(
                    evaluation_sheets,
                    month_config,
                    selected_member,
                )
            )

            if not (
                member_trend.empty
            ):

                st.subheader(
                    "Xu hướng điểm qua các tuần"
                )

                st.caption(
                    "Điểm tuần = phiếu đóng góp "
                    "(Tiêu chí 1 + 2) − "
                    "phiếu cảnh báo "
                    "(Tiêu chí 3 + 4)."
                )

                st.altair_chart(
                    plot_member_score_trend(
                        member_trend,
                        mobile_mode,
                    ),
                    use_container_width=True,
                )

                trend_table = (
                    member_trend[
                        [
                            "Tuần",
                            "Phiếu đóng góp",
                            "Phiếu cảnh báo",
                            "Điểm tuần",
                            "So với tuần trước",
                        ]
                    ]
                    .copy()
                )

                for column in [
                    "Phiếu đóng góp",
                    "Phiếu cảnh báo",
                    "Điểm tuần",
                ]:

                    trend_table[
                        column
                    ] = (
                        trend_table[
                            column
                        ]
                        .map(
                            format_number
                        )
                    )

                st.dataframe(
                    trend_table,
                    use_container_width=True,
                    hide_index=True,
                )

        else:

            st.warning(
                "Chưa có dữ liệu cho thành viên này."
            )


    # ========================================================
    # TAB 3
    # ========================================================
    with tab3:

        if (
            config_sheet_name
            is None
        ):

            sheet_list = (
                ", ".join(
                    f"**{name}**"
                    for name
                    in all_sheets.keys()
                )
            )

            st.warning(
                "Ứng dụng chưa đọc thấy sheet **Cấu hình tháng**. "
                f"Các sheet hiện tại: {sheet_list}"
            )

        elif not month_config:

            st.warning(
                "Sheet **Cấu hình tháng** chưa hợp lệ."
            )

        else:

            monthly_data = (
                build_monthly_ranking(
                    evaluation_sheets,
                    month_config,
                )
            )

            unconfigured_weeks = [
                name
                for name
                in ordered_week_names
                if (
                    name
                    not in month_config
                    or
                    month_config[
                        name
                    ].get(
                        "month"
                    )
                    is None
                )
            ]

            if unconfigured_weeks:

                st.warning(
                    "Các tuần sau chưa được tính vào bảng xếp hạng: "
                    + ", ".join(
                        unconfigured_weeks
                    )
                )

            if monthly_data.empty:

                st.warning(
                    "Chưa có dữ liệu xếp hạng theo tháng."
                )

            else:

                month_keys = sorted(
                    monthly_data[
                        "Tháng"
                    ]
                    .unique()
                    .tolist(),
                    reverse=True,
                )

                month_options = {
                    format_month(
                        key
                    ): key
                    for key
                    in month_keys
                }

                selected_display_month = (
                    st.selectbox(
                        "Chọn tháng:",
                        list(
                            month_options.keys()
                        ),
                    )
                )

                selected_month = (
                    month_options[
                        selected_display_month
                    ]
                )

                ranking = (
                    prepare_ranking_table(
                        monthly_data,
                        selected_month,
                    )
                )

                ranking, previous_month = (
                    add_previous_month_comparison(
                        ranking,
                        monthly_data,
                        selected_month,
                    )
                )

                st.caption(
                    "**Điểm xếp hạng = "
                    "tổng phiếu đóng góp "
                    "(Tiêu chí 1 + 2) − "
                    "tổng phiếu cảnh báo "
                    "(Tiêu chí 3 + 4).**"
                )

                top_members = (
                    ranking
                    .head(3)
                    .to_dict(
                        "records"
                    )
                )

                medals = [
                    "🥇",
                    "🥈",
                    "🥉",
                ]

                if mobile_mode:

                    for index, member in enumerate(
                        top_members
                    ):

                        st.metric(
                            label=(
                                f"{medals[index]} "
                                f"Hạng {index + 1}"
                            ),
                            value=(
                                member[
                                    "Thành viên"
                                ]
                            ),
                            delta=(
                                f'{member["Điểm xếp hạng"]:g} điểm'
                            ),
                            delta_color="off",
                        )

                else:

                    columns = st.columns(
                        3
                    )

                    for index, column in enumerate(
                        columns
                    ):

                        with column:

                            if index < len(
                                top_members
                            ):

                                member = (
                                    top_members[
                                        index
                                    ]
                                )

                                st.metric(
                                    label=(
                                        f"{medals[index]} "
                                        f"Hạng {index + 1}"
                                    ),
                                    value=(
                                        member[
                                            "Thành viên"
                                        ]
                                    ),
                                    delta=(
                                        f'{member["Điểm xếp hạng"]:g} điểm'
                                    ),
                                    delta_color="off",
                                )

                st.altair_chart(
                    plot_ranking_chart(
                        ranking
                    ),
                    use_container_width=True,
                )

                display_ranking = (
                    ranking[
                        [
                            "Hạng",
                            "Thành viên",
                            "Phiếu đóng góp",
                            "Phiếu cảnh báo",
                            "Điểm xếp hạng",
                            "Số tuần",
                            "So với tháng trước",
                        ]
                    ]
                    .copy()
                )

                for column in [
                    "Phiếu đóng góp",
                    "Phiếu cảnh báo",
                    "Điểm xếp hạng",
                    "Số tuần",
                ]:

                    display_ranking[
                        column
                    ] = (
                        display_ranking[
                            column
                        ]
                        .map(
                            format_number
                        )
                    )

                st.dataframe(
                    display_ranking,
                    use_container_width=True,
                    hide_index=True,
                )

                number_of_weeks = (
                    int(
                        ranking[
                            "Số tuần"
                        ].max()
                    )
                )

                comparison_note = (
                    f"; so sánh với "
                    f"{format_month(previous_month)}"
                    if previous_month
                    is not None
                    else ""
                )

                st.caption(
                    f"Dữ liệu tháng này gồm "
                    f"{number_of_weeks} tuần đánh giá"
                    f"{comparison_note}."
                )


    # ========================================================
    # TAB 4 - ĐÁNH GIÁ CẢ QUÁ TRÌNH
    # ========================================================
    with tab4:

        overall_ranking = (
            build_overall_ranking(
                evaluation_sheets,
                month_config,
            )
        )

        if overall_ranking.empty:

            st.warning(
                "Chưa có dữ liệu để đánh giá cả quá trình."
            )

        else:

            st.caption(
                "**Tổng điểm cả quá trình = "
                "tổng phiếu đóng góp "
                "(Tiêu chí 1 + 2) − "
                "tổng phiếu cảnh báo "
                "(Tiêu chí 3 + 4) "
                "của tất cả các tuần.**"
            )

            top_members = (
                overall_ranking
                .head(3)
                .to_dict(
                    "records"
                )
            )

            medals = [
                "🥇",
                "🥈",
                "🥉",
            ]

            if mobile_mode:

                for index, member in enumerate(
                    top_members
                ):

                    st.metric(
                        label=(
                            f"{medals[index]} "
                            f"Hạng {index + 1}"
                        ),
                        value=(
                            member[
                                "Thành viên"
                            ]
                        ),
                        delta=(
                            f'{member["Tổng điểm"]:g} điểm'
                        ),
                        delta_color="off",
                    )

            else:

                columns = (
                    st.columns(
                        3
                    )
                )

                for index, column in enumerate(
                    columns
                ):

                    with column:

                        if index < len(
                            top_members
                        ):

                            member = (
                                top_members[
                                    index
                                ]
                            )

                            st.metric(
                                label=(
                                    f"{medals[index]} "
                                    f"Hạng {index + 1}"
                                ),
                                value=(
                                    member[
                                        "Thành viên"
                                    ]
                                ),
                                delta=(
                                    f'{member["Tổng điểm"]:g} điểm'
                                ),
                                delta_color="off",
                            )

            st.subheader(
                "Xếp hạng tổng thể"
            )

            st.altair_chart(
                plot_overall_ranking_chart(
                    overall_ranking
                ),
                use_container_width=True,
            )

            overall_table = (
                overall_ranking[
                    [
                        "Hạng",
                        "Thành viên",
                        "Phiếu đóng góp",
                        "Phiếu cảnh báo",
                        "Tổng điểm",
                        "Số tuần",
                    ]
                ]
                .copy()
            )

            for column in [
                "Phiếu đóng góp",
                "Phiếu cảnh báo",
                "Tổng điểm",
                "Số tuần",
            ]:

                overall_table[
                    column
                ] = (
                    overall_table[
                        column
                    ]
                    .map(
                        format_number
                    )
                )

            st.dataframe(
                overall_table,
                use_container_width=True,
                hide_index=True,
            )

            st.subheader(
                "Diễn biến điểm tích lũy theo từng tuần"
            )

            st.caption(
                "Điểm tích lũy là tổng điểm tuần "
                "từ tuần đầu tiên đến tuần đang xem."
            )

            cumulative_data = (
                build_cumulative_trend(
                    evaluation_sheets,
                    month_config,
                )
            )

            if cumulative_data.empty:

                st.warning(
                    "Chưa có dữ liệu xu hướng tích lũy."
                )

            else:

                default_members = (
                    overall_ranking
                    .head(3)[
                        "Thành viên"
                    ]
                    .tolist()
                )

                selected_overall_members = (
                    st.multiselect(
                        "Chọn thành viên để xem diễn biến:",
                        options=(
                            fixed_names
                        ),
                        default=(
                            default_members
                        ),
                    )
                )

                if selected_overall_members:

                    cumulative_chart = (
                        plot_cumulative_score_trend(
                            cumulative_data,
                            selected_overall_members,
                            mobile_mode,
                        )
                    )

                    if (
                        cumulative_chart
                        is not None
                    ):

                        st.altair_chart(
                            cumulative_chart,
                            use_container_width=True,
                        )

                    detail_table = (
                        cumulative_data[
                            cumulative_data[
                                "Thành viên"
                            ].isin(
                                selected_overall_members
                            )
                        ][
                            [
                                "Thành viên",
                                "Tuần",
                                "Phiếu đóng góp",
                                "Phiếu cảnh báo",
                                "Điểm tuần",
                                "Điểm tích lũy",
                            ]
                        ]
                        .copy()
                    )

                    for column in [
                        "Phiếu đóng góp",
                        "Phiếu cảnh báo",
                        "Điểm tuần",
                        "Điểm tích lũy",
                    ]:

                        detail_table[
                            column
                        ] = (
                            detail_table[
                                column
                            ]
                            .map(
                                format_number
                            )
                        )

                    with st.expander(
                        "📋 Xem chi tiết điểm theo từng tuần"
                    ):

                        st.dataframe(
                            detail_table,
                            use_container_width=True,
                            hide_index=True,
                        )

                else:

                    st.info(
                        "Hãy chọn ít nhất một thành viên "
                        "để xem diễn biến điểm."
                    )


except Exception as error:

    st.error(
        f"Lỗi: {error}"
    )
