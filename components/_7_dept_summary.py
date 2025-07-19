import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go
import plotly

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

def dept_amt_row(df, hparams):
    start_date = pd.to_datetime(hparams['start_date'])
    end_date = pd.to_datetime(hparams['end_date'])
    value_col = hparams['value_type']
    selected_unit = hparams['unit']

    # 기간 필터링
    df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    departments = sorted(df_period['부서'].unique())

    # --- 11. 부서별 계약 건수 Bar ---
    counts = [df_period[df_period['부서'] == dept]['건수'].sum() for dept in departments]
    highlight_color = "#9baaff"
    pale_color = '#d6d9e5'
    
    blue_palette = [
        "#9baaff", "#f5bab5", "#9cd7bf", "#ab9cfe", "#f8afcf", "#f9df8a"
    ] 
    
    if selected_unit == '전체':
        colors = [highlight_color] * len(departments)
    else:
        colors = [pale_color] * len(departments)
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                colors[i] = highlight_color
    fig_bar_count = go.Figure(go.Bar(
        x=departments,
        y=counts,
        text=[f"{v:,}건" for v in counts],
        textposition='auto',
        marker_color=colors
    ))
    if selected_unit != "전체" and len(counts) > 0:
        overall_avg = round(sum(counts) / len(counts), 1)
    fig_bar_count.update_layout(
        height=320,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
    )

    # --- 12. 부서별 계약 건수 Pie ---
    gray_palette = [
        "#cbcdd7", "#dfe1eb", "#d2d7df",
        "#c7cad2", "#c9cdd7", "#b9bfc7"
    ]
    if selected_unit == "전체":
        pie_colors = blue_palette[:len(departments)]
    else:
        pie_colors = gray_palette[:len(departments)]
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                pie_colors[i] = highlight_color
    fig_pie_count = go.Figure(go.Pie(
        labels=departments,
        values=counts,
        marker_colors=pie_colors,
        textinfo='label+percent',
        hole=0.25
    ))
    fig_pie_count.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=40)
    )

    # --- 13. 부서별 환산/보험료 Bar ---
    amts = [df_period[df_period['부서'] == dept][value_col].sum() for dept in departments]
    highlight_color = "#9cd7bf"
    if selected_unit == "전체":
        bar_colors = [highlight_color] * len(departments)
    else:
        bar_colors = [pale_color] * len(departments)
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                bar_colors[i] = highlight_color
    fig_bar_amt = go.Figure(go.Bar(
        x=departments,
        y=amts,
        text=[f"{int(v):,}원" for v in amts],
        textposition='auto',
        marker_color=bar_colors
    ))
    if selected_unit != "전체" and len(amts) > 0:
        avg_amt = round(sum(amts) / len(amts), 0)
    fig_bar_amt.update_layout(
        height=320,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
    )

    # --- 14. 부서별 환산/보험료 Pie ---
    if selected_unit == "전체":
        pie_colors_amt = blue_palette[:len(departments)]
    else:
        pie_colors_amt = gray_palette[:len(departments)]
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                pie_colors_amt[i] = highlight_color
    fig_pie_amt = go.Figure(go.Pie(
        labels=departments,
        values=amts,
        marker_colors=pie_colors_amt,
        textinfo='label+percent',
        hole=0.25
    ))
    fig_pie_amt.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=40)
    )

    # ----- Dash 4분할 카드 반환 -----
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    
    left_title = f"부서별 총 건수({start_str}~{end_str})"
    right_title = f"부서별 총 {value_col}({start_str}~{end_str})"
    
    return html.Div([
        html.Div([
            html.Div(left_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_bar_count, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "24%"}),
        html.Div([
            html.Div(" ", style=TITLE_STYLE),  # 파이 차트 타이틀 생략(디자인 동일)
            dcc.Graph(figure=fig_pie_count, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "24%"}),
        html.Div([
            html.Div(right_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_bar_amt, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "24%"}),
        html.Div([
            html.Div(" ", style=TITLE_STYLE),
            dcc.Graph(figure=fig_pie_amt, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "24%"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "1.5%", "marginBottom": "18px"})
