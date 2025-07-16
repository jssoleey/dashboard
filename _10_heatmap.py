import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def dept_heatmap_row(df, hparams):
    # ----- 날짜 처리 -----
    df['날짜'] = pd.to_datetime(df['날짜'])
    end_date = pd.to_datetime(hparams['end_date'])
    start_date = pd.to_datetime(hparams['start_date'])

    # == 요일 한글 매핑 ==
    eng2kor = {
        'Monday': '월요일',
        'Tuesday': '화요일',
        'Wednesday': '수요일',
        'Thursday': '목요일',
        'Friday': '금요일',
    }
    dow_order = ['월요일', '화요일', '수요일', '목요일', '금요일']

    # --- [1] 부서별 요일 평균 "건수" (정규화, 0 제외) ---
    df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    df_period['요일'] = df_period['날짜'].dt.day_name().map(eng2kor)
    df_period = df_period[df_period['요일'].isin(dow_order)]

    # 0인 값 NaN으로 처리
    df_period['건수'] = df_period['건수'].replace(0, np.nan)
    cnt_mean = (
        df_period.groupby(['부서', '요일'])['건수'].mean()
        .unstack(fill_value=np.nan)
        .reindex(columns=dow_order)
    ).fillna(0)  # 실적 전무인 요일만 0으로

    # 부서별 Min-Max 정규화
    cnt_norm = cnt_mean.sub(cnt_mean.min(axis=1), axis=0)
    cnt_norm = cnt_norm.div(cnt_mean.max(axis=1) - cnt_mean.min(axis=1) + 1e-8, axis=0)

    # --- [2] 부서별 요일 평균 "환산(보험료)" (정규화, 0 제외) ---
    value_col = hparams.get('value_type', '환산')
    df_period[value_col] = df_period[value_col].replace(0, np.nan)
    amt_mean = (
        df_period.groupby(['부서', '요일'])[value_col].mean()
        .unstack(fill_value=np.nan)
        .reindex(columns=dow_order)
    ).fillna(0)

    amt_norm = amt_mean.sub(amt_mean.min(axis=1), axis=0)
    amt_norm = amt_norm.div(amt_mean.max(axis=1) - amt_mean.min(axis=1) + 1e-8, axis=0)

    # plotly.express imshow (좌: 건수, 우: 환산/보험료)
    fig_cnt = px.imshow(
        cnt_norm,
        aspect="auto",
        color_continuous_scale="Blues",
        zmin=0, zmax=1,
        labels=dict(color="정규화<br>건수"),
    )
    fig_cnt.update_layout(
        title=None,
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(title=None, showticklabels=True, ticks=""),
        yaxis=dict(title=None, showticklabels=True, ticks="")
    )

    fig_amt = px.imshow(
        amt_norm,
        aspect="auto",
        color_continuous_scale="Blues",
        zmin=0, zmax=1,
        labels=dict(color="정규화<br>"+value_col),
    )
    fig_amt.update_layout(
        title=None,
        height=320,
        margin=dict(l=40, r=20, t=20, b=40),
        xaxis=dict(title=None, showticklabels=True, ticks=""),
        yaxis=dict(title=None, showticklabels=True, ticks="")
    )

    # ===== 레이아웃 반환 =====
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')
    value_type = hparams.get('value_type', '환산')
    
    left_title = f"부서별 요일별 정규화 건수({start_str}~{end_str})"
    right_title = f"부서별 요일별 정규화 {value_type}({start_str}~{end_str})"
    
    return html.Div([
        html.Div([
            html.Div(left_title, style={
                "fontSize": "1.1em", "marginBottom": "0.4em", "textAlign": "left"
            }),
            dcc.Graph(figure=fig_cnt, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={"background": "#fff", "borderRadius": "7px", "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)", "padding": "1.7em 1.4em 1.6em 1.4em", "width": "49%"}),
        html.Div([
            html.Div(right_title, style={
                "fontSize": "1.1em", "marginBottom": "0.4em", "textAlign": "left"
            }),
            dcc.Graph(figure=fig_amt, config={"displayModeBar": False}, style={"height": "320px"}),
        ], style={"background": "#fff", "borderRadius": "7px", "boxShadow": "0 2px 7px 0 rgba(60,60,70,0.07)", "padding": "1.7em 1.4em 1.6em 1.4em", "width": "49%"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})
