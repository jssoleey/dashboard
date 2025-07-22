from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import calendar
from dash_iconify import DashIconify

DASH_BG = "#FFFFFF"

TITLE_STYLE = {
    "fontSize": "1.07em",
    "marginBottom": "0.7em",
    "textAlign": "left",
    "color": "#454a4f",
}

DEPT_PALETTE = {
    "골드1실": "#9baaff",
    "골드2실": "#f5bab5",
    "드림1실": "#9cd7bf",
    "드림2실": "#ab9cfe",
    "레전드실": "#f8afcf",
    "알파실": "#f9df8a",
    "전체": "#2176ff"
}

def side_donut(item):
    val = min(item['달성률'], 100)
    rest = max(100 - val, 0)
    color = DEPT_PALETTE.get(item['부서'], "#cdd0e3")
    colors = [color, "#e4e9f2"]
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
        height=130, width=130,
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
        dcc.Graph(figure=donut, config={"displayModeBar": False},
                  style={"margin": "0 auto", "height": "130px", "width": "130px", "background": DASH_BG}),
        html.Div(item['부서'],
                 style={"fontWeight": 700, "fontSize": "1em", "color": "#858688", "marginTop": "10px", "textAlign": "center"})
    ], style={
        "display": "flex", "flexDirection": "column", "alignItems": "center",
        "padding": "0 10px", "background": DASH_BG
    })


def target_row(df, hparams):
    # ---- 1. 연/월 옵션 생성 ----
    end_date = hparams.get('end_date')
    if end_date is None:
        end_date = df['날짜'].max()
    else:
        end_date = pd.to_datetime(end_date)

    # ---- 3. 년/월 드롭다운 값으로 타겟 월 구간 ----
    year = pd.to_datetime(hparams['end_date']).year
    month = pd.to_datetime(hparams['end_date']).month   

    # ① end_date가 명시적으로 넘어온 경우(상단바) → 1일~end_date
    if hparams.get('end_date', None) is not None:
        target_month_start = pd.Timestamp(year=year, month=month, day=1)
        target_month_end = pd.to_datetime(hparams['end_date'])
        # (end_date의 월이 선택 월과 다르면, 말일로 fallback해도 됨)
    else:
        # ② 도넛 selectbox → 1일~말일
        last_day = calendar.monthrange(year, month)[1]
        target_month_start = pd.Timestamp(year=year, month=month, day=1)
        target_month_end = pd.Timestamp(year=year, month=month, day=last_day)

    # ---- 4. 월별 데이터 필터링 ----
    df_month = df[(df['날짜'] >= target_month_start) & (df['날짜'] <= target_month_end)].copy()

    sidebar_depts = ['전체', '알파실', '드림1실', '드림2실', '골드1실', '골드2실', '레전드실']
    all_real_depts = ['알파실', '드림1실', '드림2실', '골드1실', '골드2실', '레전드실']

    summary = {}

    # (1) 개별 부서 집계
    for dept in all_real_depts:
        if dept in ['드림1실', '드림2실']:
            dr_sum = df_month[df_month['부서'].isin(['드림1실', '드림2실'])]['환산'].sum()
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

    # (2) 전체 목표
    goal_per_dept = df_month.groupby('부서')['목표환산'].first()
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
    center_key = hparams.get('unit', '전체')
    if center_key not in sidebar_depts:
        center_key = '전체'
    center = summary[center_key]

    # ------- 중앙 도넛 차트 (부서별 색상 적용) -------
    donut_val = min(center['달성률'], 100)
    donut_rest = max(100 - donut_val, 0)
    center_color = DEPT_PALETTE.get(center['부서'], "#2176ff")
    donut_colors = [center_color, "#e4e9f2"]

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

    # ===== 사이드 도넛 배치 =====
    other_depts = [d for d in sidebar_depts if d != center_key]
    left_depts = other_depts[:3]
    right_depts = other_depts[3:]
    left_col = html.Div([side_donut(summary[d]) for d in left_depts], style={
        "display": "flex", "flexDirection": "row", "gap": "10px", "background": DASH_BG, "alignItems": "center", "paddingTop": "150px"
    })
    right_col = html.Div([side_donut(summary[d]) for d in right_depts], style={
        "display": "flex", "flexDirection": "row", "gap": "10px", "background": DASH_BG, "alignItems": "center", "paddingTop": "150px"
    })

    year_str = pd.to_datetime(hparams['end_date']).year
    month_str = pd.to_datetime(hparams['end_date']).month
    unit_str = hparams.get('unit', '전체')

    # 기간 계산
    start_date = f"{year_str}-0{month_str}-01"
    if hparams.get('mode', 'auto') == 'auto':
        max_date = df['날짜'].max()
        # end_date가 없으면 max_date, 있으면 그것을 사용
        end_date = pd.to_datetime(hparams.get('end_date')) if hparams.get('end_date') is not None else max_date

        # 만약 end_date가 해당 월의 마지막 날(예: 2025-07-31)인데, 실제 데이터의 max_date는 그보다 앞이라면 교체
        last_day = calendar.monthrange(int(year), int(month))[1]
        month_end = pd.Timestamp(year=int(year), month=int(month), day=last_day)
        # 만약 end_date가 month_end와 같고, max_date가 그 이전이라면 max_date로 대체
        if (end_date == month_end) and (max_date < month_end) and (max_date.year == int(year)) and (max_date.month == int(month)):
            end_date = max_date

        period_str = f"({start_date} ~ {end_date.strftime('%Y-%m-%d')})"
    else:
        last_day = calendar.monthrange(int(year), int(month))[1]
        end_date = f"{year_str}-{month_str}-{last_day:02d}"
        period_str = f"({start_date} ~ {end_date})"

    title = html.Div([
        DashIconify(
            icon="mdi:trophy",
            width=26,
            style={"marginRight": "6px", "verticalAlign": "middle", "color": "#888"}
        ),
        html.Span(
            f"{year_str}년 {month_str}월 {unit_str} 목표 달성 현황 {period_str}",
            style={'verticalAlign': 'middle'}
        ),
    ], style={
        'fontSize': '1.07em', 'color': '#454a4f',
        'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center',
        'marginBottom': '0.5em'
    })
    # 최종 반환
    return html.Div([
        html.Div(title, style={}),
        html.Div([
            left_col,
            html.Div(center_texts, style={'position': 'relative', 'display': 'inline-block'}),
            right_col,
        ], style={
            "position": "relative",
            "display": "flex",
            "width": "90vw",
            "justifyContent": "center",
            "alignItems": "flex-start",
            "gap": "48px",
            "margin": "0 auto",
        }),
    ], style={"width": "97%", "margin": "24px auto", "padding": "32px 20px 32px 20px", "background": DASH_BG})
