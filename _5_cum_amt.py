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

def amt_row(df, hparams):
    start_date = pd.to_datetime(hparams['start_date'])
    end_date = pd.to_datetime(hparams['end_date'])
    value_col = hparams['value_type']

    # ===== col6. 누적 건수 Line Chart =====
    # (value_col은 '건수'로 고정)
    value_col_cnt = '건수'
    if hparams['unit'] == '전체':
        df_this_cnt = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
        df_prev_cnt = df[(df['날짜'] < start_date) & (df['날짜'] >= (start_date - (end_date - start_date + pd.Timedelta(days=1))))].copy()
    else:
        df_this_cnt = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == hparams['unit'])].copy()
        df_prev_cnt = df[(df['날짜'] < start_date) & (df['날짜'] >= (start_date - (end_date - start_date + pd.Timedelta(days=1)))) & (df['부서'] == hparams['unit'])].copy()

    x_dates = pd.date_range(start_date, end_date, freq='D')
    n_days = len(x_dates)

    this_daily_cnt = df_this_cnt.groupby('날짜')[value_col_cnt].sum().reindex(x_dates, fill_value=0)
    this_cum_cnt = this_daily_cnt.cumsum().values

    # 직전 기간 계산 (기존 방식과 일치)
    period_length = (end_date - start_date).days + 1
    prev_end = start_date - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=period_length-1)
    prev_dates = pd.date_range(prev_start, prev_end, freq='D')
    prev_daily_cnt = df_prev_cnt.groupby('날짜')[value_col_cnt].sum().reindex(prev_dates, fill_value=0)
    prev_cum_cnt = prev_daily_cnt.cumsum().values
    prev_cum_cnt_aligned = [prev_cum_cnt[i] if i < len(prev_cum_cnt) else None for i in range(n_days)]

    fig_col6 = go.Figure()
    # 1. 설정 기간 누적 (라인+면적)
    fig_col6.add_trace(go.Scatter(
        x=x_dates, y=this_cum_cnt,
        mode='lines+markers',
        name='설정 기간 누적',
        line=dict(color='#f5bab5', width=3),
        fill='tozeroy',
        fillcolor='rgba(245,186,181,0.1)',
        line_shape='spline',
        marker=dict(size=5)
    ))
    # 2. 직전 기간 누적 (라인+면적)
    fig_col6.add_trace(go.Scatter(
        x=x_dates, y=prev_cum_cnt_aligned,
        mode='lines+markers',
        name='직전 기간 누적',
        line=dict(color='#d6d9e5', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(214,217,229,0.3)',
        line_shape='spline',
        marker=dict(size=5)
    ))
    fig_col6.update_layout(
        height=300,
        margin=dict(l=25, r=20, t=30, b=25),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        xaxis=dict(tickformat='%m-%d', tickmode="auto", showgrid=True),
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ===== col7. 누적 환산실적(보험료) Line Chart =====
    if hparams['unit'] == '전체':
        df_this = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
        df_prev = df[(df['날짜'] >= prev_start) & (df['날짜'] <= prev_end)].copy()
    else:
        df_this = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == hparams['unit'])].copy()
        df_prev = df[(df['날짜'] >= prev_start) & (df['날짜'] <= prev_end) & (df['부서'] == hparams['unit'])].copy()

    this_daily_amt = df_this.groupby('날짜')[value_col].sum().reindex(x_dates, fill_value=0)
    this_cum_amt = this_daily_amt.cumsum().values

    prev_daily_amt = df_prev.groupby('날짜')[value_col].sum().reindex(prev_dates, fill_value=0)
    prev_cum_amt = prev_daily_amt.cumsum().values
    prev_cum_amt_aligned = [prev_cum_amt[i] if i < len(prev_cum_amt) else None for i in range(n_days)]

    fig_col7 = go.Figure()
    # 1. 설정 기간 누적 (라인+면적)
    fig_col7.add_trace(go.Scatter(
        x=x_dates, y=this_cum_amt,
        mode='lines+markers',
        name='설정 기간 누적',
        line=dict(color='#9cd7bf', width=3),
        fill='tozeroy',
        fillcolor='rgba(165,238,209,0.1)',
        line_shape='spline',
        marker=dict(size=5)
    ))
    # 2. 직전 기간 누적 (라인+면적)
    fig_col7.add_trace(go.Scatter(
        x=x_dates, y=prev_cum_amt_aligned,
        mode='lines+markers',
        name='직전 기간 누적',
        line=dict(color='#d6d9e5', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(214,217,229,0.3)',
        line_shape='spline',
        marker=dict(size=5)
    ))
    fig_col7.update_layout(
        height=300,
        margin=dict(l=25, r=20, t=30, b=25),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        xaxis=dict(tickformat='%m-%d', tickmode="auto", showgrid=True),
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # ======= Dash 레이아웃 반환 (카드형 2분할) =======
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')
    value_type = hparams.get('value_type', '환산')
    
    left_title = f"누적 건수({unit_str}, {start_str}~{end_str})"
    right_title = f"누적 {value_type}({unit_str}, {start_str}~{end_str})"
    
    return html.Div([
        html.Div([
            html.Div(left_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_col6, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "49%"}),
        html.Div([
            html.Div(right_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_col7, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={**CARD_STYLE, "width": "49%"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})
