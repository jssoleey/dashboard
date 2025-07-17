import pandas as pd
from dash import html, dcc, dash_table
import dash
from dash.dependencies import Input, Output, State
import io
import base64

def register_table_callback(app, get_latest_df):
    df = get_latest_df()

    dept_list = df['부서'].unique().tolist()
    min_date = df['날짜'].min().date()
    max_date = df['날짜'].max().date()

    # ---- Layout (Dash의 children 요소로 사용) ----
    table_layout = html.Div([
        html.H3("일별 실적 상세 테이블"),
        html.Div([
            dcc.Dropdown(
                id='table-dept-dropdown',
                options=[{'label': d, 'value': d} for d in dept_list],
                value=dept_list,  # 전체 선택 default
                multi=True,
                style={'marginBottom': '1rem'}
            ),
            dcc.DatePickerRange(
                id='table-date-picker',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                display_format='YYYY-MM-DD',
                style={'marginBottom': '1rem'}
            ),
            html.Div(
                html.Button("엑셀 다운로드", id="table-download-btn"),
                style={'marginLeft': '30px', 'display': 'inline-block', 'verticalAlign': 'middle'}
            ),
            dcc.Download(id="table-download-excel"),
        ]),
        html.Div(id='table-dataframe-container'),
    ], style={'margin': '2rem 0'})

    # ---- 콜백 1: 데이터 필터링 및 테이블 표시 ----
    @app.callback(
        Output('table-dataframe-container', 'children'),
        Input('table-dept-dropdown', 'value'),
        Input('table-date-picker', 'start_date'),
        Input('table-date-picker', 'end_date'),
        State('main-data', 'data')
    )
    def update_table(selected_dept, start_date, end_date, data_json):
        df = pd.read_json(data_json, orient='split')
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
        if not selected_dept or not start_date or not end_date:
            return "필터를 선택하세요."
        filtered_df = df[
            (df['부서'].isin(selected_dept)) &
            (df['날짜'] >= pd.to_datetime(start_date)) &
            (df['날짜'] <= pd.to_datetime(end_date))
        ].copy()
        filtered_df = filtered_df.sort_values(by=['날짜', '부서'], ascending=[True, True])
        # 표시
        return dash_table.DataTable(
            data=filtered_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in filtered_df.columns],
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
        )

    # ---- 콜백 2: 엑셀 다운로드 ----
    @app.callback(
        Output("table-download-excel", "data"),
        Input("table-download-btn", "n_clicks"),
        Input('table-dept-dropdown', 'value'),
        Input('table-date-picker', 'start_date'),
        Input('table-date-picker', 'end_date'),
        prevent_initial_call=True
    )
    def download_excel(n_clicks, selected_dept, start_date, end_date):
        df = get_latest_df()
        if n_clicks is None or not selected_dept:
            return dash.no_update
        filtered_df = df[
            (df['부서'].isin(selected_dept)) &
            (df['날짜'] >= pd.to_datetime(start_date)) &
            (df['날짜'] <= pd.to_datetime(end_date))
        ].copy()
        filtered_df = filtered_df.sort_values(by=['날짜', '부서'], ascending=[True, True])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='실적')
        processed_data = output.getvalue()
        # b64 인코딩 → 다운로드용 반환
        return dcc.send_bytes(processed_data, filename="실적_상세_테이블.xlsx")

    return table_layout
