import pandas as pd
from dash import html
import dash_iconify

def kpi_card(title, value, icon, accent="#2176ff"):
    return html.Div([
        html.Div(style={
            "position": "absolute", "top": "10px", "bottom": "10px",
            "left": "0", "width": "4px",
            "background": accent,
            "borderRadius": "5px"
        }),
        html.Div([
            dash_iconify.DashIconify(
                icon=icon,
                width=26,
                style={"marginRight": "6px", "verticalAlign": "middle", "color": "#888"}
            ),
            html.Span(title, style={
                "fontSize": "1.07em", "color": "#454a4f", "marginBottom": "2px"
            }),
            html.Div(str(value), style={
                "fontSize": "2em", "fontWeight": 700, "marginTop": "6px", "color": "#464646"
            }),
        ], style={"marginLeft": "30px", "padding": "7px 0 7px 0"})
    ],
    style={
        "background": "#fff",
        "borderRadius": "7px",
        "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)",
        "padding": "18px 0 14px 18px",
        "position": "relative",
        "height": "92px",
        "width": "97%",
        "display": "flex",
        "flexDirection": "column",
        "justifyContent": "center"
    })

def kpi_row(df, hparams):
    start_date = hparams["start_date"]
    end_date = hparams["end_date"]
    unit = hparams["unit"]
    value_col = hparams["value_type"]

    # 부서 필터링
    if unit == "전체":
        dff = df[(df["날짜"] >= start_date) & (df["날짜"] <= end_date)]
    else:
        dff = df[(df["날짜"] >= start_date) & (df["날짜"] <= end_date) & (df["부서"] == unit)]
        
    if dff.empty:
        return html.Div("해당 기간에 데이터가 없습니다.", style={"padding": "2em", "textAlign": "center"})

    total_count = int(dff['건수'].sum()) if not dff.empty else 0

    total_count = int(dff['건수'].sum())
    total_amt = int(dff[value_col].sum())
    
    # *** 실근무일(데이터 존재 날짜)로 나누기 ***
    unique_work_days = dff['날짜'].nunique()  # 데이터가 존재하는 날짜의 개수
    avg_count = round(total_count / unique_work_days, 2) if unique_work_days else 0
    avg_amt = round(total_amt / unique_work_days, 0) if unique_work_days else 0
    
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')

    kpi_boxes = html.Div([
        html.Div(kpi_card(f"총 건수({start_str}~{end_str})", f"{total_count:,}", "mdi:account-group", "#2176ff"), style={"width": "24%", "display": "inline-block"}),
        html.Div(kpi_card(f"일평균 건수({start_str}~{end_str})", f"{avg_count:,}", "mdi:calendar-today", "#eb974b"), style={"width": "24%", "display": "inline-block"}),
        html.Div(kpi_card(f"총 {value_col}({start_str}~{end_str})", f"{total_amt:,}원", "mdi:cash-multiple", "#4eb5c7"), style={"width": "24%", "display": "inline-block"}),
        html.Div(kpi_card(f"일평균 {value_col}({start_str}~{end_str})", f"{avg_amt:,}원", "mdi:calculator-variant", "#f75467"), style={"width": "24%", "display": "inline-block"}),
    ], style={
        "display": "flex", "width": "99%",
        "justifyContent": "space-between", "marginBottom": "30px"
    })
    return kpi_boxes
