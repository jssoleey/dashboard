import pandas as pd
from dash import html, dcc, dash_table
import dash
from dash.dependencies import Input, Output, State
import io
import base64

def register_table_callback(app):
    # 테이블 필터 및 컴포넌트 레이아웃만 정의 (데이터는 사용하지 않음!)
    table_layout = html.Div([
        html.H3("일별 실적 상세 테이블"),
        html.Div([
            dcc.Dropdown(
                id='table-dept-dropdown',
                multi=True,
                style={'marginBottom': '1rem'}
            ),
            dcc.DatePickerRange(
                id='table-date-picker',
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

    # --- 콜백1: 부서 리스트/날짜 초기값 자동 세팅
    @app.callback(
        Output('table-dept-dropdown', 'options'),
        Output('table-dept-dropdown', 'value'),
        Output('table-date-picker', 'min_date_allowed'),
        Output('table-date-picker', 'max_date_allowed'),
        Output('table-date-picker', 'start_date'),
        Output('table-date-picker', 'end_date'),
        Input('main-data', 'data')
    )
    def set_table_filter_options(data_json):
        df = pd.read_json(data_json, orient='split')
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
        dept_list = df['부서'].unique().tolist()
        min_date = df['날짜'].min().date()
        max_date = df['날짜'].max().date()
        return (
            [{'label': d, 'value': d} for d in dept_list],
            dept_list,  # 전체 선택 default
            min_date, max_date, min_date, max_date
        )

    # --- 콜백2: 데이터 필터링 및 테이블 표시
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
        if filtered_df.empty:
            return "조회 결과가 없습니다."
        return dash_table.DataTable(
            data=filtered_df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in filtered_df.columns],
            page_size=20,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center'},
        )

    # --- 콜백3: 엑셀 다운로드
    @app.callback(
        Output("table-download-excel", "data"),
        Input("table-download-btn", "n_clicks"),
        Input('table-dept-dropdown', 'value'),
        Input('table-date-picker', 'start_date'),
        Input('table-date-picker', 'end_date'),
        State('main-data', 'data'),
        prevent_initial_call=True
    )
    def download_excel(n_clicks, selected_dept, start_date, end_date, data_json):
        df = pd.read_json(data_json, orient='split')
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce').dt.tz_localize(None)
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
        return dcc.send_bytes(processed_data, filename="실적_상세_테이블.xlsx")

    return table_layout
