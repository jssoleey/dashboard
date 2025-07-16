import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go

CARD_STYLE = {
    "background": "#fff",
    "borderRadius": "7px",
    "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)",
    "padding": "1.7em 1.4em 1.6em 1.4em",
    "marginBottom": "10px",
    "minWidth": "220px",
    "textAlign": "center",
    "minHeight": "350px",
    "display": "flex",
    "flexDirection": "column",
    "justifyContent": "flex-start",
}

TITLE_STYLE = {
    "fontSize": "1.07em",
    "marginBottom": "0.7em",
    "textAlign": "left",
    "color": "#454a4f",
}

def cnt_row(df, hparams):
    # ----- 좌측: 건수 -----
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')
    value_type = hparams.get('value_type', '환산')
    
    left_title = f"건수({unit_str}, {start_str}~{end_str})"
    left_card = html.Div([
        html.Div(left_title, style=TITLE_STYLE),
        dcc.Tabs(
            id="cnt-bar-tabs",
            value="day",
            children=[
                dcc.Tab(label='일별', value='day'),
                dcc.Tab(label='주별', value='week'),
                dcc.Tab(label='월별', value='month'),
            ],
            style={"marginBottom": "14px"}
        ),
        dcc.Loading(
            id="cnt-bar-loading",
            children=[dcc.Graph(id="cnt-bar-graph", config={"displayModeBar": False}, style={"height": "320px"})],
            type="circle"
        ),
    ], style={**CARD_STYLE, "width": "49%"})

    # ----- 우측: 환산 or 보험료 -----
    value_type = hparams.get("value_type", "환산")
    # label도 상태바에서 선택한 값에 따라 바뀜
    right_title = f"{value_type}({unit_str}, {start_str}~{end_str})"
    right_card = html.Div([
        html.Div(right_title, style=TITLE_STYLE),
        dcc.Tabs(
            id="amt-bar-tabs",
            value="day",
            children=[
                dcc.Tab(label='일별', value='day'),
                dcc.Tab(label='주별', value='week'),
                dcc.Tab(label='월별', value='month'),
            ],
            style={"marginBottom": "14px"}
        ),
        dcc.Loading(
            id="amt-bar-loading",
            children=[dcc.Graph(id="amt-bar-graph", config={"displayModeBar": False}, style={"height": "320px"})],
            type="circle"
        ),
    ], style={**CARD_STYLE, "width": "49%"})

    # ======= Dash 레이아웃 반환 (카드형 2분할) =======
    return html.Div([
        left_card,
        right_card,
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})
