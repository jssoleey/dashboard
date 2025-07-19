import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go

def period_summary_row(df, hparams):
    """
    오늘의 실적, 이번 주 실적, 이번 달 실적 카드 3개(1행)
    """
    # 공통 스타일
    card_style = {
        "background": "#fff",
        "borderRadius": "0px",
        "boxShadow": "0 4px 16px rgba(30,60,90,0.07)",
        "padding": "1.7em 1.4em 1.6em 1.4em",
        "marginBottom": "10px",
        "minWidth": "220px",
        "textAlign": "center",
        "minHeight": "250px"
    }

    # --------- 1. 오늘의 실적 카드 ---------
    base_date = hparams["end_date"]
    unit = hparams["unit"]
    value_col = hparams["value_type"]

    df['날짜'] = pd.to_datetime(df['날짜'])
    yesterday = base_date
    day_before = base_date - pd.Timedelta(days=1)

    if unit == "전체":
        yesterday_df = df[df['날짜'] == yesterday]
        day_before_df = df[df['날짜'] == day_before]
    else:
        yesterday_df = df[(df['날짜'] == yesterday) & (df['부서'] == unit)]
        day_before_df = df[(df['날짜'] == day_before) & (df['부서'] == unit)]

    y_count = int(yesterday_df['건수'].sum())
    db_count = int(day_before_df['건수'].sum())
    diff_count = y_count - db_count
    y_amt = int(yesterday_df[value_col].sum())
    db_amt = int(day_before_df[value_col].sum())
    diff_amt = y_amt - db_amt

    def diff_text_html(diff):
        if diff > 0:
            return html.Span(f"▲ {diff:,}", style={"color": "#e74c3c", "fontSize": "1em"})
        elif diff < 0:
            return html.Span(f"▼ {abs(diff):,}", style={"color": "#2176ff", "fontSize": "1em"})
        else:
            return html.Span("-", style={"color": "#888", "fontSize": "1em"})
        
    end_date = pd.to_datetime(hparams.get('end_date'))
    week_start = end_date - pd.Timedelta(days=end_date.weekday())
    week_start_str = week_start.strftime('%y.%m.%d')     
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    month_start = end_date.replace(day=1)
    month_start_str = month_start.strftime('%y.%m.%d')

    card1 = html.Div([
        html.Div(f"오늘의 실적({unit}, {end_str})", style={"fontSize": "1.07em", "marginBottom": "0.7em", "textAlign": "left", "color": "#454a4f"}),
        html.Div([
            html.Div(f"{y_count:,}건", style={
                "fontSize": "2.0em", "fontWeight": 700, "color": "#464646", "marginBottom": "0.3em"
            }),
            html.Div(diff_text_html(diff_count), style={
                "fontSize": "1em", "marginBottom": "0.5em", "marginTop": "0em"
            }),
            html.Div(style={"height": "1px", "background": "#d3d5db", "margin": "0.7em 0"}),
            html.Div(f"{y_amt:,}원", style={
                "fontSize": "1.7em", "fontWeight": 700, "color": "#464646", "marginBottom": "0.2em"
            }),
            html.Div(diff_text_html(diff_amt), style={
                "fontSize": "1em", "marginTop": "0em"
            }),
        ], style={"textAlign": "center"})
    ], style=card_style)

    # --------- 2. 이번 주 실적 카드 ---------
    week_start = base_date - pd.Timedelta(days=base_date.weekday())
    last_week_start = week_start - pd.Timedelta(days=7)
    last_week_end = week_start - pd.Timedelta(days=1)
    if unit == '전체':
        df_this_week = df[(df['날짜'] >= week_start) & (df['날짜'] <= base_date)]
        df_last_week = df[(df['날짜'] >= last_week_start) & (df['날짜'] <= last_week_end)]
    else:
        df_this_week = df[(df['날짜'] >= week_start) & (df['날짜'] <= base_date) & (df['부서'] == unit)]
        df_last_week = df[(df['날짜'] >= last_week_start) & (df['날짜'] <= last_week_end) & (df['부서'] == unit)]
    count_this = int(df_this_week['건수'].sum())
    count_last = int(df_last_week['건수'].sum())
    amt_this = int(df_this_week[value_col].sum())
    amt_last = int(df_last_week[value_col].sum())

    bar_data = {
        '구분': ['지난 주', '이번 주'],
        '건수': [count_last, count_this],
        value_col: [amt_last, amt_this]
    }
    fig_count = go.Figure(go.Bar(
        x=bar_data['건수'],
        y=bar_data['구분'],
        orientation='h',
        text=[f"{v:,}건" for v in bar_data['건수']],
        textposition='inside',
        marker_color=['#d6d9e5', '#9baaff']
    ))
    fig_count.update_layout(
        height=100, margin=dict(l=35, r=15, t=15, b=10),
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=True)
    )
    fig_count.update_traces(hoverinfo='skip')

    fig_amt = go.Figure(go.Bar(
        x=bar_data[value_col],
        y=bar_data['구분'],
        orientation='h',
        text=[f"{v:,}원" for v in bar_data[value_col]],
        textposition='inside',
        marker_color=['#d6d9e5', '#9baaff']
    ))
    fig_amt.update_layout(
        height=100, margin=dict(l=35, r=15, t=15, b=10),
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=True)
    )
    fig_amt.update_traces(hoverinfo='skip')

    card2 = html.Div([
        html.Div(f"이번 주 실적({unit}, {week_start_str}~{end_str})", style={"fontSize": "1.07em", "marginBottom": "0.4em", "textAlign": "left", "color": "#454a4f"}),
        dcc.Graph(figure=fig_count, config={"displayModeBar": False}, style={"marginBottom": "1.2em"}),
        dcc.Graph(figure=fig_amt, config={"displayModeBar": False})
    ], style=card_style)

    # --------- 3. 이번 달 실적 카드 ---------
    today = base_date
    this_month = today.replace(day=1)
    last_month_last = this_month - pd.Timedelta(days=1)
    last_month = last_month_last.replace(day=1)
    if unit == '전체':
        df_this_month = df[(df['날짜'] >= this_month) & (df['날짜'] <= today)]
        df_last_month = df[(df['날짜'] >= last_month) & (df['날짜'] <= last_month_last)]
    else:
        df_this_month = df[(df['날짜'] >= this_month) & (df['날짜'] <= today) & (df['부서'] == unit)]
        df_last_month = df[(df['날짜'] >= last_month) & (df['날짜'] <= last_month_last) & (df['부서'] == unit)]
    count_this_month = int(df_this_month['건수'].sum())
    count_last_month = int(df_last_month['건수'].sum())
    amt_this_month = int(df_this_month[value_col].sum())
    amt_last_month = int(df_last_month[value_col].sum())

    bar_data_month = {
        '구분': ['지난 달', '이번 달'],
        '건수': [count_last_month, count_this_month],
        value_col: [amt_last_month, amt_this_month]
    }
    fig_count_month = go.Figure(go.Bar(
        x=bar_data_month['건수'],
        y=bar_data_month['구분'],
        orientation='h',
        text=[f"{v:,}건" for v in bar_data_month['건수']],
        textposition='inside',
        marker_color=['#d6d9e5', '#9baaff']
    ))
    fig_count_month.update_layout(
        height=100, margin=dict(l=35, r=15, t=15, b=10),
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=True)
    )
    fig_count_month.update_traces(hoverinfo='skip')

    fig_amt_month = go.Figure(go.Bar(
        x=bar_data_month[value_col],
        y=bar_data_month['구분'],
        orientation='h',
        text=[f"{v:,}원" for v in bar_data_month[value_col]],
        textposition='inside',
        marker_color=['#d6d9e5', '#9baaff']
    ))
    fig_amt_month.update_layout(
        height=100, margin=dict(l=35, r=15, t=15, b=10),
        xaxis=dict(showticklabels=False, visible=False),
        yaxis=dict(showticklabels=True)
    )
    fig_amt_month.update_traces(hoverinfo='skip')

    card3 = html.Div([
        html.Div(f"이번 달 실적({unit}, {month_start_str}~{end_str})", style={"fontSize": "1.07em", "marginBottom": "0.4em", "textAlign": "left", "color": "#454a4f"}),
        dcc.Graph(figure=fig_count_month, config={"displayModeBar": False}, style={"marginBottom": "1.2em"}),
        dcc.Graph(figure=fig_amt_month, config={"displayModeBar": False})
    ], style=card_style)

    # ----- 3분할(1행)로 반환 -----
    return html.Div([
        html.Div(card1, style={"width": "33.3%", "display": "inline-block", "verticalAlign": "top", "padding": "4px"}),
        html.Div(card2, style={"width": "33.3%", "display": "inline-block", "verticalAlign": "top", "padding": "4px"}),
        html.Div(card3, style={"width": "33.3%", "display": "inline-block", "verticalAlign": "top", "padding": "4px"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "center", "marginBottom": "14px"})
