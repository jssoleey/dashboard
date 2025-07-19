import dash
from dash import html, dcc
import pandas as pd
import datetime
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State

# ---- 각 행별 컴포넌트 import ----
from components._1_kpi import kpi_row
from components._2_month_target import target_row
from components._3_period_summary import period_summary_row
from components._4_amt import cnt_row
from components._5_cum_amt import amt_row
from components._6_per_one_person import personal_row
from components._7_dept_summary import dept_amt_row
from components._8_dept_amt import dept_compare_row
from components._9_dept_cum_amt import dept_line_row
from components._10_heatmap import dept_heatmap_row


# ---- 테이블 콤포넌트 및 콜백 통합 import ----
from components._11_table_section import register_table_callback

# --- 파일 및 데이터 준비 ---
#url = 'https://docs.google.com/spreadsheets/d/1WZudSUSf4ineO6sFQuaV7nJVmr8CcYH5GwK-WuVNR4A/export?format=csv&gid=939378808'
#df = pd.read_csv(url, encoding='utf-8')

def get_latest_df():
    url_alpha = 'https://docs.google.com/spreadsheets/d/1Rj6DGqEhuCO02rwsi9EQ-nkBs4C7PJcW5s0mqhTFBdE/export?format=csv&gid=0'
    url_dream1 = 'https://docs.google.com/spreadsheets/d/1KpnVeV2f2aSRTiZAl1LSq74C4oQ975r7qtxlYIr-RFs/export?format=csv&gid=0'
    url_dream2 = 'https://docs.google.com/spreadsheets/d/1R-g1y8QRBZMmWaav-cfiCURfox2Hx_2mxet_q3XzB3A/export?format=csv&gid=0'
    url_gold1 = 'https://docs.google.com/spreadsheets/d/1XiILBe6zsQmQs51aIjrvZzH8bHRn43YBt200qTWiCWw/export?format=csv&gid=0'
    url_gold2 = 'https://docs.google.com/spreadsheets/d/1M7-NcP4OVB-0YqkSfy1uGzFgLDjWziJZKo2U4OiRcTA/export?format=csv&gid=0'
    url_legend = 'https://docs.google.com/spreadsheets/d/1MXBvPlB9rlwpDrEP86K2Ya9lOYBc-hp5l6iw__jb2bs/export?format=csv&gid=0'
    df_alpha = pd.read_csv(url_alpha, encoding='utf-8')
    df_dream1 = pd.read_csv(url_dream1, encoding='utf-8')
    df_dream2 = pd.read_csv(url_dream2, encoding='utf-8')
    df_gold1 = pd.read_csv(url_gold1, encoding='utf-8')
    df_gold2 = pd.read_csv(url_gold2, encoding='utf-8')
    df_legend = pd.read_csv(url_legend, encoding='utf-8')
    df = pd.concat([df_alpha, df_dream1, df_dream2, df_gold1, df_gold2, df_legend], axis = 0)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    return df

df = get_latest_df()

# --- Dash 앱 시작 ---
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Goodrich Sales Report"
table_layout = register_table_callback(app)

# ----- 레이아웃 -----
def serve_layout():
    df = get_latest_df()
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    end_date_default = max_date
    start_date_default = max(end_date_default.replace(day=1), min_date)
    dept_list = df['부서'].unique().tolist()

    return html.Div(
        style={"backgroundColor": "#EEEEEE", "minHeight": "100vh", "padding": "10px"},
        children=[
            dcc.Store(id='main-data', data=df.to_json(date_format='iso', orient='split')),
            dcc.Store(id='target-mode', data='auto'),
            html.Div([
                # 좌측: 제목
                html.H1("굿리치플러스 실적 현황", style={
                    'textAlign': 'left',
                    'fontSize': '2.2rem',
                    'margin': 0,
                    'paddingLeft': '10px',
                    'fontWeight': 700,
                    'flex': '1'
                }),
                # 우측: 설정 영역
                html.Div([
                    html.Div([
                        html.Label("시작 일자", style={'marginBottom': '3px'}),
                        dcc.DatePickerSingle(
                            id='start-date',
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=start_date_default,
                            style={'width': '100%'}
                        )
                    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '125px', 'marginRight': '12px'}),
                    html.Div([
                        html.Label("끝 일자", style={'marginBottom': '3px'}),
                        dcc.DatePickerSingle(
                            id='end-date',
                            min_date_allowed=min_date,
                            max_date_allowed=max_date,
                            date=end_date_default,
                            style={'width': '100%'}
                        )
                    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '125px', 'marginRight': '12px'}),
                    html.Button(
                        '기간 초기화', id='reset-date-btn', n_clicks=0,
                        style={'height': '45px', 'marginTop': '25px', 'marginRight': '20px'} 
                    ),
                    html.Div([
                        html.Label("단위(부서)", style={'marginBottom': '10px'}),
                        dcc.Dropdown(
                            id='unit',
                            options=[{'label': x, 'value': x} for x in ['전체'] + dept_list],
                            value='전체',
                            clearable=False,
                            style={'width': '120px', 'fontSize': '0.99rem'}
                        )
                    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '120px', 'height' : '75px', 'marginRight': '20px'}),
                    html.Div([
                        html.Label("보기 기준", style={'marginBottom': '15px'}),
                        dcc.RadioItems(
                            id='value-type',
                            options=[
                                {'label': '환산', 'value': '환산'},
                                {'label': '보험료', 'value': '보험료'}
                            ],
                            value='환산',
                            labelStyle={'display': 'inline-block', 'marginRight': '10px', 'fontSize': '0.98rem'}
                        )
                    ], style={'display': 'flex', 'flexDirection': 'column', 'width': '148px', 'height' : '75px'}),
                ], style={
                    'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center',
                    'justifyContent': 'flex-end',
                    'gap': '0px',
                    'flex': '1'
                }),
            ], style={
                'display': 'flex', 'flexDirection': 'row',
                'alignItems': 'center', 'justifyContent': 'space-between',
                'marginTop': '35px', 'marginBottom': '20px', 'width': '100%'
            }),
            html.Hr(),
            #####
            html.Div(
                id='target-row-container',
                children=[
                    # selectbox를 여기서 미리 정의 (초기 값/option은 dummy라도 괜찮음)
                    html.Div([
                        dcc.Dropdown(id='target-year', options=[], style={'width': '120px'}),
                        dcc.Dropdown(id='target-month', options=[], style={'width': '90px'}),
                    ], style={'display': 'none'})  # 초기엔 안 보이게 해도 됨
                ],
                style={'margin': '32px 0'}
            ),
            html.Div(id='dashboard-content'),
            html.Hr(),
            table_layout,
            html.Div(style={'marginBottom': '36px'})
        ]
    )

app.layout = serve_layout

# ----- 대시보드(상단) 콜백 -----
@app.callback(
    dash.dependencies.Output('dashboard-content', 'children'),
    dash.dependencies.Input('start-date', 'date'),
    dash.dependencies.Input('end-date', 'date'),
    dash.dependencies.Input('unit', 'value'),
    dash.dependencies.Input('value-type', 'value'),
    dash.dependencies.State('main-data', 'data'),
)
def update_dashboard(start_date, end_date, unit, value_type, data_json):
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    hparams = {
        "start_date": pd.to_datetime(start_date),
        "end_date": pd.to_datetime(end_date),
        "unit": unit,
        "value_type": value_type
    }
    return [
        kpi_row(df, hparams),
        #target_row(df, hparams),
        period_summary_row(df, hparams),
        cnt_row(df, hparams),
        amt_row(df, hparams),
        personal_row(df, hparams),
        dept_amt_row(df, hparams),
        dept_compare_row(df, hparams),
        dept_line_row(df, hparams),
        dept_heatmap_row(df, hparams)
    ]

@app.callback(
    Output('cnt-bar-graph', 'figure'),
    Input('cnt-bar-tabs', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('unit', 'value'),
    State('main-data', 'data'),
)
def update_cnt_bar(tab, start_date, end_date, unit, data_json):
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if unit == '전체':
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    else:
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == unit)].copy()
    value_col = '건수'

    if tab == 'day':
        all_days = pd.date_range(start_date, end_date, freq="D")
        daily_df = (df_period.groupby('날짜')[value_col].sum()
                    .reindex(all_days, fill_value=0)
                    .rename_axis('날짜').reset_index())
        fig = go.Figure(go.Bar(
            x=daily_df['날짜'], y=daily_df[value_col], marker_color='#9baaff', name='일별'
        ))
        fig.update_layout(xaxis=dict(tickformat='%m-%d'))
    elif tab == 'week':
        df_week = df_period[df_period['날짜'].dt.weekday < 5].copy()
        df_week['주월요일'] = df_week['날짜'] - pd.to_timedelta(df_week['날짜'].dt.weekday, unit='d')
        df_week['주월요일'] = pd.to_datetime(df_week['주월요일'])
        week_sum = df_week.groupby('주월요일')[value_col].sum().reset_index()
        week_sum = week_sum.sort_values('주월요일')

        tick_vals = week_sum['주월요일'] + pd.Timedelta(hours=12)
        tick_text = week_sum['주월요일'].dt.strftime('%m-%d')
        fig = go.Figure(go.Bar(
            x=tick_vals,
            y=week_sum[value_col],
            marker_color='#9baaff',
            name='주별'
        ))

        # ---- 티커 표시 조건 분기 ----
        if len(week_sum) <= 10:
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=tick_vals,
                    ticktext=tick_text,
                    type='date'
                )
            )
        else:
            fig.update_layout(
                xaxis=dict(
                    tickformat='%m-%d',
                    type='date'
                )
            )
    else:  # tab == 'month'
        # ===== 월별 집계 =====
        df_period['연도'] = df_period['날짜'].dt.year
        df_period['월'] = df_period['날짜'].dt.month
        month_df = (
            df_period.groupby(['연도', '월'])[value_col]
            .sum().reset_index()
        )
        # x축 라벨 생성: 연도가 바뀌는 1월만 'YYYY-1', 나머지는 'M'
        # x축 라벨: 항상 'YY-MM'로 표기 (예: 25-04, 25-05)
        x_tick = month_df.apply(lambda row: f"{str(row['연도'])[2:]}-{row['월']:02d}", axis=1)
        fig = go.Figure(go.Bar(
            x=x_tick,
            y=month_df[value_col],
            marker_color='#9baaff',
            name='월별'
        ))
        fig.update_layout(
            xaxis=dict(tickvals=x_tick, ticktext=x_tick)
        )

    fig.update_layout(
        height=320, margin=dict(l=25, r=20, t=30, b=25),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
    )
    return fig

@app.callback(
    Output('amt-bar-graph', 'figure'),
    Input('amt-bar-tabs', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('unit', 'value'),
    Input('value-type', 'value'),
    State('main-data', 'data'),
)
def update_amt_bar(tab, start_date, end_date, unit, value_type, data_json):
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    if unit == '전체':
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date)].copy()
    else:
        df_period = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == unit)].copy()
    # 컬럼명 동적으로
    value_col = value_type

    if tab == 'day':
        all_days = pd.date_range(start_date, end_date, freq="D")
        daily_df = (df_period.groupby('날짜')[value_col].sum()
                    .reindex(all_days, fill_value=0)
                    .rename_axis('날짜').reset_index())
        fig = go.Figure(go.Bar(
            x=daily_df['날짜'], y=daily_df[value_col], marker_color="#9cd7bf", name='일별'
        ))
        fig.update_layout(xaxis=dict(tickformat='%m-%d'))
    elif tab == 'week':
        df_week = df_period[df_period['날짜'].dt.weekday < 5].copy()
        df_week['주월요일'] = df_week['날짜'] - pd.to_timedelta(df_week['날짜'].dt.weekday, unit='d')
        df_week['주월요일'] = pd.to_datetime(df_week['주월요일'])
        week_sum = df_week.groupby('주월요일')[value_col].sum().reset_index()
        week_sum = week_sum.sort_values('주월요일')

        tick_vals = week_sum['주월요일'] + pd.Timedelta(hours=12)
        tick_text = week_sum['주월요일'].dt.strftime('%m-%d')
        fig = go.Figure(go.Bar(
            x=tick_vals,
            y=week_sum[value_col],
            marker_color='#9cd7bf',
            name='주별'
        ))

        # --- 티커 표시 방식 분기 ---
        if len(week_sum) <= 10:
            xaxis_opts = dict(
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_text,
                type='date'
            )
        else:
            xaxis_opts = dict(
                tickformat='%m-%d',
                type='date'
            )

        fig.update_layout(
            xaxis=xaxis_opts
        )
    else:  # tab == 'month'
        df_period['연도'] = df_period['날짜'].dt.year
        df_period['월'] = df_period['날짜'].dt.month
        month_df = (
            df_period.groupby(['연도', '월'])[value_col]
            .sum().reset_index()
        )
        x_tick = month_df.apply(lambda row: f"{str(row['연도'])[2:]}-{row['월']:02d}", axis=1)
        fig = go.Figure(go.Bar(
            x=x_tick,
            y=month_df[value_col],
            marker_color='#9cd7bf',
            name='월별'
        ))
        fig.update_layout(
            xaxis=dict(tickvals=x_tick, ticktext=x_tick)
        )

    fig.update_layout(
        height=320, margin=dict(l=25, r=20, t=30, b=25),
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0"),
    )
    return fig

@app.callback(
    Output('dept-cnt-graph', 'figure'),
    Input('dept-cnt-tabs', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    State('main-data', 'data'),
)
def update_dept_cnt(tab, start_date, end_date, data_json):
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    depts = df['부서'].unique()
    value_col = '건수'

    if tab == 'day':
        x_range = pd.date_range(start_date, end_date, freq="D")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)]
            y = data.groupby('날짜')[value_col].sum().reindex(x_range, fill_value=0)
            # 선형 보간
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=x_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=dict(showticklabels=True, tickformat='%m-%d'),
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    elif tab == 'week':
        # 1. 시작일이 속한 주의 월요일 구하기
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        start_week_mon = start_date - pd.Timedelta(days=start_date.weekday())  # 항상 월요일로
        x_range = pd.date_range(start_week_mon, end_date, freq="W-MON")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)].copy()
            data = data[data['날짜'].dt.weekday < 5]
            data['주월요일'] = data['날짜'] - pd.to_timedelta(data['날짜'].dt.weekday, unit='d')
            y = data.groupby('주월요일')[value_col].sum().reindex(x_range, fill_value=0)
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=x_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        
        # 핵심: x축 tick 표시 방식 조건 분기
        if len(x_range) <= 10:
            xaxis_dict = dict(tickvals=x_range, tickformat='%m-%d', type='date')
        else:
            xaxis_dict = dict(tickformat='%m-%d', type='date')
        
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=xaxis_dict,
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    else:  # 'month'
        # 1. 시작일이 포함된 월의 1일로 보정
        start_month = pd.to_datetime(start_date).replace(day=1)
        month_range = pd.date_range(start_month, end_date, freq="MS")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)].copy()
            data['연월'] = data['날짜'].dt.to_period('M').dt.to_timestamp()
            y = data.groupby('연월')[value_col].sum().reindex(month_range, fill_value=0)
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=month_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=dict(tickvals=month_range, tickformat='%y-%m', type='date'),
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    return fig

@app.callback(
    Output('dept-amt-graph', 'figure'),
    Input('dept-amt-tabs', 'value'),
    Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('value-type', 'value'),
    State('main-data', 'data'),
)
def update_dept_amt(tab, start_date, end_date, value_type, data_json):
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    depts = df['부서'].unique()
    value_col = value_type

    if tab == 'day':
        x_range = pd.date_range(start_date, end_date, freq="D")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)]
            y = data.groupby('날짜')[value_col].sum().reindex(x_range, fill_value=0)
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=x_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=dict(showticklabels=True, tickformat='%m-%d'),
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    elif tab == 'week':
        # 1. 시작일이 속한 주의 월요일을 구해서 x_range 생성
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        start_week_mon = start_date - pd.Timedelta(days=start_date.weekday())
        x_range = pd.date_range(start_week_mon, end_date, freq="W-MON")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)].copy()
            data = data[data['날짜'].dt.weekday < 5]
            data['주월요일'] = data['날짜'] - pd.to_timedelta(data['날짜'].dt.weekday, unit='d')
            y = data.groupby('주월요일')[value_col].sum().reindex(x_range, fill_value=0)
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=x_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        # -- xaxis 옵션 분기 처리 --
        if len(x_range) <= 10:
            xaxis_opts = dict(tickvals=x_range, tickformat='%m-%d', type='date')
        else:
            xaxis_opts = dict(tickformat='%m-%d', type='date')
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=xaxis_opts,
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    else:  # 'month'
        # 시작일이 포함된 월의 1일로 보정
        start_month = pd.to_datetime(start_date).replace(day=1)
        month_range = pd.date_range(start_month, end_date, freq="MS")
        traces = []
        for dept in depts:
            data = df[(df['날짜'] >= start_date) & (df['날짜'] <= end_date) & (df['부서'] == dept)].copy()
            data['연월'] = data['날짜'].dt.to_period('M').dt.to_timestamp()
            y = data.groupby('연월')[value_col].sum().reindex(month_range, fill_value=0)
            y = y.replace(0, pd.NA).interpolate(method='linear').fillna(0)
            traces.append(go.Scatter(
                x=month_range, y=y, mode='lines+markers', name=dept, line_shape='spline'
            ))
        fig = go.Figure(traces)
        fig.update_layout(
            height=320, margin=dict(l=25, r=20, t=30, b=25),
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            xaxis=dict(tickvals=month_range, tickformat='%y-%m', type='date'),
            yaxis=dict(title=None, showgrid=True, gridcolor="#e0e0e0")
        )
    return fig

@app.callback(
    Output('target-mode', 'data'),
    Input('end-date', 'date'),
    Input('target-year', 'value'),
    Input('target-month', 'value'),
    State('target-mode', 'data'),
    prevent_initial_call=True
)
def set_target_mode(end_date, year, month, mode):
    ctx = dash.callback_context
    if not ctx.triggered:
        return 'auto'
    trig = ctx.triggered[0]['prop_id']
    if trig == 'end-date.date':
        return 'auto'
    elif trig in ['target-year.value', 'target-month.value']:
        return 'manual'
    return mode

@app.callback(
    Output('target-year', 'options'),
    Output('target-month', 'options'),
    Output('target-year', 'value'),
    Output('target-month', 'value'),
    Input('main-data', 'data'),
    Input('end-date', 'date'),
    Input('target-year', 'value'),      # ← input으로 변경!
    Input('target-month', 'value'),     # ← input으로 변경!
)
def sync_target_date_options(data_json, end_date, cur_year, cur_month):
    import pandas as pd
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    years = sorted(df['날짜'].dt.year.unique())
    months = sorted(df['날짜'].dt.month.unique())

    # end_date 기준으로 디폴트 설정
    if end_date:
        d = pd.to_datetime(end_date)
        default_year, default_month = d.year, d.month
    else:
        default_year, default_month = years[-1], months[-1]

    years_option = [{'label': str(y), 'value': y} for y in years]
    months_option = [{'label': f"{m:02d}", 'value': m} for m in months]

    # 트리거 확인
    ctx = dash.callback_context
    if not ctx.triggered:
        # 최초 진입
        return years_option, months_option, default_year, default_month

    changed_id = ctx.triggered[0]['prop_id']

    if changed_id == 'end-date.date':
        # 달력에서 끝 일자 바꾸면 → 디폴트로 리셋
        return years_option, months_option, default_year, default_month
    elif changed_id in ['target-year.value', 'target-month.value']:
        # 사용자가 직접 selectbox 바꾸면 → 그대로 유지
        y = cur_year if cur_year in years else default_year
        m = cur_month if cur_month in months else default_month
        return years_option, months_option, y, m
    else:
        # 데이터가 바뀌면 → 디폴트
        return years_option, months_option, default_year, default_month
    
@app.callback(
    Output('target-row-container', 'children'),
    Input('target-year', 'value'),
    Input('target-month', 'value'),
    Input('end-date', 'date'),
    Input('target-mode', 'data'),
    Input('unit', 'value'),
    State('main-data', 'data'),
    State('value-type', 'value')
)
def update_target_row(year, month, end_date, mode, unit, data_json, value_type):
    import calendar
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
    year = int(year)
    month = int(month)
    if mode == 'auto':
        # end_date 기준(단, end_date가 같은 월인지 체크!)
        end_dt = pd.to_datetime(end_date)
        if end_dt.year == year and end_dt.month == month:
            target_end = end_dt
        else:
            # 만약 end_date가 다른 월/년이라면 해당 월의 말일!
            last_day = calendar.monthrange(year, month)[1]
            target_end = pd.Timestamp(year=year, month=month, day=last_day)
    else:
        # manual 모드: 무조건 그 월 말일
        last_day = calendar.monthrange(year, month)[1]
        target_end = pd.Timestamp(year=year, month=month, day=last_day)
    hparams = {
        "unit": unit,
        "value_type": value_type,
        "target_year": year,
        "target_month": month,
        "end_date": target_end
    }
    return target_row(df, hparams)

@app.callback(
    Output('start-date', 'date'),
    Output('end-date', 'date'),
    Input('reset-date-btn', 'n_clicks'),
    State('main-data', 'data'),
    prevent_initial_call=True
)
def reset_dates(n_clicks, data_json):
    # df로부터 디폴트값 동적으로 다시 가져옴
    df = pd.read_json(data_json, orient='split')
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()
    end_date_default = max_date
    start_date_default = max(end_date_default.replace(day=1), min_date)
    return start_date_default, end_date_default


if __name__ == '__main__':
    app.run_server(debug=True)
