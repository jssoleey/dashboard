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

def personal_row(df, hparams):
    start_date = pd.to_datetime(hparams['start_date'])
    end_date = pd.to_datetime(hparams['end_date'])
    value_col = hparams['value_type']  # '환산' 또는 '보험료'

    # ========== [카드1] 1인당 일평균 계약건수 ==========
    if hparams['unit'] == '전체':
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    else:
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == hparams['unit'])].copy()
    total_person = df_period['가동인원'].sum()
    total_contract = df_period['건수'].sum()
    avg_contract_per_person = round(total_contract / total_person, 2) if total_person else 0

    fig_gauge_contract = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_contract_per_person,
        number={'suffix': " 건", 'font': {'size': 32}},
        gauge={
            'axis': {'range': [0, 3], 'tickwidth': 0},
            'bar': {'color': "#9baaff"},
            'steps': [
                {'range': [0, 1], 'color': "#f1f7ff"},
                {'range': [1, 2], 'color': "#edf0ff"},
                {'range': [2, 3], 'color': "#dfe3ff"},
            ]
        }
    ))
    fig_gauge_contract.update_layout(height=250, margin=dict(t=30, b=30, l=20, r=20), paper_bgcolor="#fff")

    # 부서별 집계 및 막대
    df_period_all = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    departments = sorted(df_period_all['부서'].unique())
    avg_contract_per_person_list = []
    for dept in departments:
        d = df_period_all[df_period_all['부서'] == dept]
        total_person = d['가동인원'].sum()
        total_contract = d['건수'].sum()
        avg_contract_per_person_list.append(round(total_contract / total_person, 2) if total_person else 0)
    #overall_avg = round(sum(avg_contract_per_person_list) / len(avg_contract_per_person_list), 2) if avg_contract_per_person_list else 0

    selected_unit = hparams['unit']
    
    if selected_unit == "전체":
        colors = ['#9baaff'] * len(departments)
    else:
        colors = ['#d6d9e5'] * len(departments)
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                colors[i] = '#9baaff'
    fig_dept_contract = go.Figure(go.Bar(
        x=departments,
        y=avg_contract_per_person_list,
        text=[f"{v:.2f}" for v in avg_contract_per_person_list],
        textposition='auto',
        marker_color=colors
    ))
    fig_dept_contract.update_layout(
        height=300,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        yaxis_title=None
    )

    # ========== [카드2] 1건당 일평균 환산(보험료) ==========
    if hparams['unit'] == '전체':
        df_period_amt = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    else:
        df_period_amt = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == hparams['unit'])].copy()
    total_contract = df_period_amt['건수'].sum()
    total_amt = df_period_amt[value_col].sum()
    avg_amt_per_contract = round(total_amt / total_contract, 0) if total_contract else 0

    fig_gauge_amt = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_amt_per_contract,
        number={'suffix': " 원", 'font': {'size': 30}, 'valueformat': ',.0f'},
        gauge={
            'axis': {'range': [0, 210000], 'tickwidth': 0},
            'bar': {'color': '#f5bab5'},
            'steps': [
                {'range': [0, 70000], 'color': "#fff4f3"},
                {'range': [70000, 140000], 'color': "#ffeeed"},
                {'range': [140000, 210000], 'color': "#ffe6e4"},
            ]
        }
    ))
    fig_gauge_amt.update_layout(height=250, margin=dict(t=30, b=30, l=20, r=20), paper_bgcolor="#fff")

    df_period_bar = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    departments = sorted(df_period_bar['부서'].unique())
    avg_amt_per_contract_list = []
    for dept in departments:
        d = df_period_bar[df_period_bar['부서'] == dept]
        total_contract = d['건수'].sum()
        total_amt = d[value_col].sum()
        avg_amt_per_contract_list.append(round(total_amt / total_contract, 0) if total_contract else 0)
    #overall_avg_amt = round(sum(avg_amt_per_contract_list) / len(avg_amt_per_contract_list), 0) if avg_amt_per_contract_list else 0
    if selected_unit == "전체":
        colors_amt = ['#f5bab5'] * len(departments)
    else:
        colors_amt = ['#d6d9e5'] * len(departments)
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                colors_amt[i] = '#f5bab5'
    fig_dept_amt = go.Figure(go.Bar(
        x=departments,
        y=avg_amt_per_contract_list,
        text=[f"{int(v):,}원" for v in avg_amt_per_contract_list],
        textposition='auto',
        marker_color=colors_amt
    ))
    fig_dept_amt.update_layout(
        height=300,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        yaxis_title=None
    )

    # ========== [카드3] 1인당 일평균 환산(보험료) ==========
    if hparams['unit'] == '전체':
        df_period_gauge = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    else:
        df_period_gauge = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == hparams['unit'])].copy()
    total_person = df_period_gauge['가동인원'].sum()
    total_amt = df_period_gauge[value_col].sum()
    avg_amt_per_person_per_day = round(total_amt / total_person, 0) if total_person else 0

    fig_gauge_amt_person = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_amt_per_person_per_day,
        number={'suffix': " 원", 'font': {'size': 30}, 'valueformat': ',.0f'},
        gauge={
            'axis': {'range': [0, 390000], 'tickwidth': 0},
            'bar': {'color': "#9cd7bf"},
            'steps': [
                {'range': [0, 130000], 'color': "#f4fffb"},
                {'range': [130000, 260000], 'color': "#ebfff7"},
                {'range': [260000, 390000], 'color': "#ddfff1"},
            ]
        }
    ))
    fig_gauge_amt_person.update_layout(height=250, margin=dict(t=30, b=30, l=20, r=20), paper_bgcolor="#fff")

    avg_amt_per_person_per_day_list = []
    for dept in departments:
        d = df_period_bar[df_period_bar['부서'] == dept]
        total_person = d['가동인원'].sum()
        total_amt = d[value_col].sum()
        avg_amt_per_person_per_day_list.append(round(total_amt / total_person, 0) if total_person else 0)
    #overall_avg_amt_person = round(sum(avg_amt_per_person_per_day_list) / len(avg_amt_per_person_per_day_list), 0) if avg_amt_per_person_per_day_list else 0
    if selected_unit == "전체":
        colors_person = ['#9cd7bf'] * len(departments)
    else:
        colors_person = ['#d6d9e5'] * len(departments)
        for i, dept in enumerate(departments):
            if dept == selected_unit:
                colors_person[i] = '#9cd7bf'
    fig_dept_amt_person = go.Figure(go.Bar(
        x=departments,
        y=avg_amt_per_person_per_day_list,
        text=[f"{int(v):,}원" for v in avg_amt_per_person_per_day_list],
        textposition='auto',
        marker_color=colors_person
    ))
    fig_dept_amt_person.update_layout(
        height=300,
        margin=dict(l=30, r=20, t=20, b=40),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        yaxis_title=None
    )

    # ========== 3분할 카드 반환 ==========
    
    start_str = pd.to_datetime(hparams.get('start_date')).strftime('%y.%m.%d')
    end_str = pd.to_datetime(hparams.get('end_date')).strftime('%y.%m.%d')
    unit_str = hparams.get('unit', '전체')
    
    left_title = f"1인당 하루 평균 계약 건수({unit_str}, {start_str}~{end_str})"
    middle_title = f"계약당 평균 {value_col}({unit_str}, {start_str}~{end_str})"
    right_title = f"1인당 하루 평균 {value_col}({unit_str}, {start_str}~{end_str})"
    
    return html.Div([
        html.Div([
            html.Div(left_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_gauge_contract, config={"displayModeBar": False}, style={"height": "250px"}),
            dcc.Graph(figure=fig_dept_contract, config={"displayModeBar": False}, style={"height": "300px"}),
        ], style={**CARD_STYLE, "width": "32%"}),
        html.Div([
            html.Div(middle_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_gauge_amt, config={"displayModeBar": False}, style={"height": "250px"}),
            dcc.Graph(figure=fig_dept_amt, config={"displayModeBar": False}, style={"height": "300px"}),
        ], style={**CARD_STYLE, "width": "32%"}),
        html.Div([
            html.Div(right_title, style=TITLE_STYLE),
            dcc.Graph(figure=fig_gauge_amt_person, config={"displayModeBar": False}, style={"height": "250px"}),
            dcc.Graph(figure=fig_dept_amt_person, config={"displayModeBar": False}, style={"height": "300px"}),
        ], style={**CARD_STYLE, "width": "32%"}),
    ], style={"width": "100%", "display": "flex", "justifyContent": "space-between", "gap": "2%", "marginBottom": "16px"})

