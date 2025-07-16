import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go
import matplotlib.colors as mcolors   # hex to rgba 변환

def hex_to_rgba(hex_color, alpha=0.2):
    """Hex 색상을 RGBA 포맷으로 변환"""
    rgb = mcolors.to_rgb(hex_color)
    return f"rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {alpha})"

def dept_line_row(df, hparams):
    start_date = pd.to_datetime(hparams['start_date'])
    end_date = pd.to_datetime(hparams['end_date'])
    value_col = hparams['value_type']
    selected_unit = hparams['unit']

    # 부서/날짜 범위 필터
    df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    dept_list = ['알파실', '드림1실', '드림2실', '골드1실', '골드2실', '레전드실']
    all_days = pd.date_range(start_date, end_date, freq="D")

    # 파란 계열 팔레트 (부서 수만큼 늘려 사용)
    color_palette = [
        "#636efa",
        "#ef553b",
        "#00cc96",
        "#ab63fa",
        "#ffa15a",
        "#19d3f3"     
    ]
    line_colors = color_palette[:len(dept_list)]

    # ----- 부서별 누적 건수 Line Chart -----
    fig_line_count = go.Figure()
    for idx, dept in enumerate(dept_list):
        sub = df_period[df_period['부서'] == dept]
        day_count = sub.groupby('날짜')['건수'].sum().reindex(all_days, fill_value=0).cumsum()
        fig_line_count.add_trace(go.Scatter(
            x=all_days, y=day_count,
            mode='lines+markers',
            name=dept,
            line=dict(color=line_colors[idx], width=2),
            line_shape='spline',
            marker=dict(size=5),
            fill=None
        ))

    fig_line_count.update_layout(
        height=320,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        xaxis=dict(tickformat='%m-%d'),
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ----- 부서별 누적 실적(환산/보험료) Line Chart -----
    fig_line_amt = go.Figure()
    for idx, dept in enumerate(dept_list):
        sub = df_period[df_period['부서'] == dept]
        day_amt = sub.groupby('날짜')[value_col].sum().reindex(all_days, fill_value=0).cumsum()
        fig_line_amt.add_trace(go.Scatter(
            x=all_days, y=day_amt,
            mode='lines+markers',
            name=dept,
            line=dict(color=line_colors[idx], width=2),
            line_shape='spline',
            marker=dict(size=5),
            fill=None
        ))

    fig_line_amt.update_layout(
        height=320,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        xaxis=dict(tickformat='%m-%d'),
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ----- Dash 레이아웃 반환 -----
    
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')
    value_type = hparams.get('value_type', '환산')
    
    left_title = f"부서별 누적 건수({start_str}~{end_str})"
    right_title = f"부서별 누적 {value_type}({start_str}~{end_str})"
    
    return html.Div([
        html.Div([
            html.Div(left_title, style={
                "fontSize": "1.07em", "marginBottom": "0.7em", "textAlign": "left", "color": "#454a4f",
            }),
            dcc.Graph(figure=fig_line_count, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={"background": "#fff", "borderRadius": "7px", "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)", "padding": "1.7em 1.4em 1.6em 1.4em", "width": "49%"}),
        html.Div([
            html.Div(right_title, style={
                "fontSize": "1.07em", "marginBottom": "0.7em", "textAlign": "left", "color": "#454a4f",
            }),
            dcc.Graph(figure=fig_line_amt, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={"background": "#fff", "borderRadius": "7px", "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)", "padding": "1.7em 1.4em 1.6em 1.4em", "width": "49%"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})
