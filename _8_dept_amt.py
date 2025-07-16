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

def dept_compare_row(df, hparams):
    # 공통 파라미터
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    value_type = hparams.get('value_type', '환산')

    # 좌측: 부서별 건수 (Line chart)
    left_title = f"부서별 건수({start_str}~{end_str})"
    left_card = html.Div([
        html.Div(left_title, style=TITLE_STYLE),
        dcc.Tabs(
            id="dept-cnt-tabs",
            value="day",
            children=[
                dcc.Tab(label='일별', value='day'),
                dcc.Tab(label='주별', value='week'),
                dcc.Tab(label='월별', value='month'),
            ],
            style={"marginBottom": "14px"}
        ),
        dcc.Loading(
            id="dept-cnt-loading",
            children=[dcc.Graph(id="dept-cnt-graph", config={"displayModeBar": False}, style={"height": "320px"})],
            type="circle"
        ),
    ], style={**CARD_STYLE, "width": "49%"})

    # 우측: 부서별 환산/보험료 (Line chart)
    right_title = f"부서별 {value_type}({start_str}~{end_str})"
    right_card = html.Div([
        html.Div(right_title, style=TITLE_STYLE),
        dcc.Tabs(
            id="dept-amt-tabs",
            value="day",
            children=[
                dcc.Tab(label='일별', value='day'),
                dcc.Tab(label='주별', value='week'),
                dcc.Tab(label='월별', value='month'),
            ],
            style={"marginBottom": "14px"}
        ),
        dcc.Loading(
            id="dept-amt-loading",
            children=[dcc.Graph(id="dept-amt-graph", config={"displayModeBar": False}, style={"height": "320px"})],
            type="circle"
        ),
    ], style={**CARD_STYLE, "width": "49%"})

    return html.Div([
        left_card,
        right_card,
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})
