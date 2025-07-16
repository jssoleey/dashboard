from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd

DASH_BG = "#FFFFFF"

TITLE_STYLE = {
    "fontSize": "1.07em",
    "marginBottom": "0.7em",
    "textAlign": "left",
    "color": "#454a4f",
}

def target_row(df, hparams):
    base_date = hparams['end_date']
    unit = hparams['unit']
    target_month = base_date.replace(day=1)
    df_month = df[(df['날짜'] >= target_month) & (df['날짜'] <= base_date)].copy()

    # 부서 리스트
    sidebar_depts = ['전체', '알파실', '드림1실', '드림2실', '골드1실', '골드2실', '레전드실']
    all_real_depts = ['알파실', '드림1실', '드림2실', '골드1실', '골드2실', '레전드실']

    summary = {}

    # (1) 개별 부서 집계 (for문 한 번만!)
    for dept in all_real_depts:
        if dept in ['드림1실', '드림2실']:
            dr_sum = df_month[df_month['부서'].isin(['드림1실','드림2실'])]['환산'].sum()
            dept_goal_arr = df_month[df_month['부서'] == dept]['목표환산'].unique()
            goal = dept_goal_arr[0] if len(dept_goal_arr) > 0 else 0
            ratio = round((dr_sum/goal)*100,1) if goal else 0
            remain = goal - dr_sum
            summary[dept] = {
                '부서': dept, '목표환산': goal, '누적환산': dr_sum,
                '달성률': ratio, '남은금액': remain
            }
        else:
            sub_df = df_month[df_month['부서'] == dept]
            goal_arr = sub_df['목표환산'].unique()
            goal = goal_arr[0] if len(goal_arr) > 0 else 0
            _sum = sub_df['환산'].sum()
            ratio = round((_sum/goal)*100,1) if goal else 0
            remain = goal - _sum
            summary[dept] = {
                '부서': dept, '목표환산': goal, '누적환산': _sum,
                '달성률': ratio, '남은금액': remain
            }

    # (2) 전체 목표: 모든 부서 목표 합계 (드림2실 목표도 예외처리)
    goal_per_dept = df_month.groupby('부서')['목표환산'].first()
    # '드림2실'이 없을 경우도 예외처리
    dr2_goal = df_month.query("부서 == '드림2실'")['목표환산'].unique()
    dr2_goal_val = dr2_goal[0] if len(dr2_goal) > 0 else 0

    overall_goal = goal_per_dept.sum() - dr2_goal_val
    overall_sum = df_month['환산'].sum()
    overall_ratio = round((overall_sum / overall_goal) * 100, 1) if overall_goal else 0
    overall_remain = overall_goal - overall_sum
    summary['전체'] = {
        '부서': '전체',
        '목표환산': overall_goal,
        '누적환산': overall_sum,
        '달성률': overall_ratio,
        '남은금액': overall_remain
    }

    # 중앙 표시용 부서 결정
    center_key = unit
    if unit not in sidebar_depts:
        center_key = '전체'
    center = summary[center_key]

    # ------- 중앙 도넛 파이차트 (더 크게, 배경색, 퍼센트만 표시) -------
    donut_val = min(center['달성률'], 100)
    donut_rest = max(100 - donut_val, 0)
    donut_colors = ["#9baaff", "#e4e9f2"]
    donut_fig = go.Figure(go.Pie(
        values=[donut_val, donut_rest],
        labels=["달성", "미달성"],
        marker_colors=donut_colors,
        hole=0.7,
        textinfo="none",
        hoverinfo="skip",
        sort=False,
        direction='clockwise'
    ))
    donut_fig.update_layout(
        height=350, width=350,
        paper_bgcolor=DASH_BG, plot_bgcolor=DASH_BG,
        margin=dict(t=20, b=20, l=12, r=12),
        showlegend=False,
        annotations=[
            dict(
                text=f"<span style='font-size:2em; font-weight:600; color:#2176ff'>{center['달성률']:.1f}%</span>",
                x=0.5, y=0.52, font=dict(size=20), showarrow=False, align="center", valign="middle"
            ),
        ]
    )

    remain = center['남은금액']
    if remain > 0:
        remain_msg = f"목표 달성까지 {remain:,}원 남았습니다!"
        remain_style = {"color": "#636e72", "fontWeight": 500, "fontSize": "1.14em", "marginTop": "5px"}
    else:
        remain_msg = f"{abs(remain):,}원 초과 달성!"
        remain_style = {"color": "#27ae60", "fontWeight": 700, "fontSize": "1.16em", "marginTop": "5px"}
    center_texts = html.Div([
        html.Div(center['부서'], style={"fontWeight": 700, "fontSize": "1.5em", "color": "#2176ff", "textAlign": "center", "marginBottom": "4px"}),
        dcc.Graph(figure=donut_fig, config={"displayModeBar": False}, style={"margin": "0 auto", "height": "350px", "width": "350px", "background": DASH_BG}),
        html.Div(f"{center['누적환산']:,}원 / {center['목표환산']:,}원", style={"color": "#636e72", "fontSize": "1.04em", "textAlign": "center"}),
        html.Div(remain_msg, style={**remain_style, "textAlign": "center", "marginBottom": "0.5em", "fontWeight": 700}),
    ], style={"width": "388px", "margin": "0 24px", "display": "flex", "flexDirection": "column", "alignItems": "center"})

    # ------- 사이드 게이지 바 (가로형, 내부에만 퍼센트 표시) ------
    def side_donut(item):
        val = min(item['달성률'], 100)
        rest = max(100 - val, 0)
        colors = ["#cdd0e3", "#e4e9f2"]
        donut = go.Figure(go.Pie(
            values=[val, rest],
            labels=["달성", "미달성"],
            marker_colors=colors,
            hole=0.7,
            textinfo="none",
            hoverinfo="skip",
            sort=False,
            direction='clockwise'
        ))
        donut.update_layout(
            height=130, width=130,     # 크기 조정
            paper_bgcolor=DASH_BG, plot_bgcolor=DASH_BG,
            margin=dict(t=8, b=8, l=0, r=0),
            showlegend=False,
            annotations=[
                dict(
                    text=f"<span style='font-size:1.2em; font-weight:600; color:#96989c'>{item['달성률']:.1f}%</span>",
                    x=0.5, y=0.52, font=dict(size=12), showarrow=False, align="center", valign="middle"
                ),
            ]
        )
        return html.Div([
            dcc.Graph(figure=donut, config={"displayModeBar": False}, style={"margin": "0 auto", "height": "130px", "width": "130px", "background": DASH_BG}),
            html.Div(item['부서'], style={"fontWeight": 700, "fontSize": "1em", "color": "#858688", "marginTop": "10px", "textAlign": "center"})
        ], style={
            "display": "flex", "flexDirection": "column", "alignItems": "center",  # ⭐️ 세로로 가운데 정렬
            "padding": "0 10px",
            "background": DASH_BG
        })

    # 중앙 제외, 좌3/우3를 리스트로 세로 → 가로로
    other_depts = [d for d in sidebar_depts if d != center_key]
    left_depts = other_depts[:3]
    right_depts = other_depts[3:]
    
    # 좌/우 3개씩
    left_col = html.Div([side_donut(summary[d]) for d in left_depts], style={
        "display": "flex", "flexDirection": "row", "gap": "10px", "background": DASH_BG, "alignItems": "center", "paddingTop": "150px"
    })
    right_col = html.Div([side_donut(summary[d]) for d in right_depts], style={
        "display": "flex", "flexDirection": "row", "gap": "10px", "background": DASH_BG, "alignItems": "center", "paddingTop": "150px"
    })

    # 전체 배치: (왼쪽3) (가운데) (오른쪽3) - 모두 수평 한줄
    year_str = pd.to_datetime(hparams.get('end_date')).strftime('%Y')
    month_str = pd.to_datetime(hparams.get('end_date')).strftime('%m')
    unit_str = hparams.get('unit', '전체')
    
    title = f"{year_str}년 {month_str}월 {unit_str} 목표 달성 현황"
    
    return html.Div([
        html.Div(title, style=TITLE_STYLE),
        html.Div([
            left_col,   # 좌측 bar 3개
            center_texts,  # 중앙 도넛
            right_col,  # 우측 bar 3개
        ], style={
            "display": "flex",
            "width": "90vw",          # 화면 넓이의 90%
            "justifyContent": "center",   # ⭐️ 양쪽 bar와 도넛 전체를 가운데 정렬
            "alignItems": "flex-start",
            "gap": "48px",            # 전체 그룹 사이 여백 (원하는 만큼)
            "margin": "0 auto",
        }),
    ], style={"width": "97%", "margin": "24px auto", "padding": "32px 20px 32px 20px", "background": DASH_BG})
