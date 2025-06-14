import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import requests
from io import BytesIO

# ✅ 구글 드라이브 공유 파일 ID
FILE_ID = '여기에_ID_넣기'
url = f'https://drive.google.com/uc?export=download&id={FILE_ID}'

# 📥 엑셀 파일 다운로드 및 pandas로 로딩
res = requests.get(url)
xls = pd.read_excel(BytesIO(res.content), sheet_name=None)

# 📊 시트(날짜)별로 단지/가격 정보 정리
all_data = []
for sheet_name, df in xls.items():
    try:
        df.columns = [c.strip() for c in df.columns]
        df = df[["단지명", "매매가", "전세가"]].dropna(subset=["단지명"])
        df["날짜"] = pd.to_datetime(sheet_name)
        df["매매가"] = df["매매가"].astype(str).str.replace(",", "").str.replace("-", "").replace("", None).astype(float)
        df["전세가"] = df["전세가"].astype(str).str.replace(",", "").str.replace("-", "").replace("", None).astype(float)
        df["갭가격"] = df["매매가"] - df["전세가"]
        all_data.append(df)
    except Exception as e:
        print(f"{sheet_name} 처리 실패:", e)
        continue

df_all = pd.concat(all_data)
df_all = df_all.dropna(subset=["날짜", "단지명"])

# Dash 앱 설정
app = dash.Dash(__name__)
단지목록 = sorted(df_all["단지명"].unique())

app.layout = html.Div([
    html.H2("단지별 가격 변화 추이"),
    
    html.Div([
        html.Label("단지 선택:"),
        dcc.Dropdown(
            options=[{"label": name, "value": name} for name in 단지목록],
            value=단지목록[:1],
            multi=True,
            id="apt-selector"
        ),
    ], style={"margin": "10px"}),

    html.Div([
        html.Label("가격 종류 선택:"),
        dcc.RadioItems(
            options=[
                {"label": "매매가", "value": "매매가"},
                {"label": "전세가", "value": "전세가"},
                {"label": "갭가격", "value": "갭가격"},
            ],
            value="매매가",
            inline=True,
            id="price-type"
        ),
    ], style={"margin": "10px"}),

    dcc.Graph(id="price-graph")
])

@app.callback(
    Output("price-graph", "figure"),
    Input("apt-selector", "value"),
    Input("price-type", "value"),
)
def update_graph(selected_apts, price_type):
    if not selected_apts:
        return px.line(title="단지를 선택해주세요.")

    filtered = df_all[df_all["단지명"].isin(selected_apts)]
    fig = px.line(
        filtered,
        x="날짜",
        y=price_type,
        color="단지명",
        markers=True,
        title=f"{price_type} 변화 추이"
    )
    fig.update_layout(legend_title_text="단지명", xaxis_title="날짜", yaxis_title=price_type)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
