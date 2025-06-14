import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import platform

# 페이지 설정
st.set_page_config(layout="wide")

# 한글 폰트 설정
if platform.system() == 'Windows':
    matplotlib.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    matplotlib.rc('font', family='AppleGothic')
else:
    matplotlib.rc('font', family='NanumGothic')
matplotlib.rcParams['axes.unicode_minus'] = False

# 스타일 커스터마이징
st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        cursor: pointer;
    }
    .graph-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }
    .graph-box {
        width: 90%;
        height: 60vh;
        margin-bottom: 20px;
    }
    .nav-links {
        margin-bottom: 20px;
    }
    .nav-links a {
        margin-right: 20px;
        text-decoration: none;
        font-weight: bold;
        color: #1f77b4;
    }
    .complex-buttons {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 2px;  /* 버튼 간 간격 조정 */
        margin-bottom: 20px;
        padding: 2px;  /* 전체 패딩 추가 */
    }
    .sort-buttons {
        display: flex;
        gap: 10px;
        margin-bottom: 10px;
    }
    .stButton > button {
        width: auto;
        max-width: 160px;
        height: 35px;
        text-align: left;
        font-size: 10px;  /* 11px에서 10px로 줄임 */
        padding: 4px 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin: 0;  /* margin 제거 */
    }
    .button-container {
        position: fixed;
        top: 60px;  /* selected-info 높이 + 여유공간 */
        left: 0;
        right: 0;
        background-color: white;
        z-index: 998;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
   .selected-info {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: white;
        z-index: 999;
        padding: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
        .stHorizontalBlock {
        position: fixed !important;
        top: 60px;
        left: 0;
        right: 0;
        background: white;
        z-index: 998;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 스크롤 가능한 영역을 위한 여백 추가 */
    .main-content {
        padding-top: 250px !important;  /* 버튼 컨테이너 높이에 따라 조정 */
    }
    .selected-button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: 2px solid #ff4b4b !important;
    }
    </style>
""", unsafe_allow_html=True)

# 시트 ID 및 목록
sheet_id = '1cUZ9-bMzeokaAGb84YAh--KngCM0U0-9pJgXHXrJ0U8'
sheet_names = [
    '24.06.07', '24.06.26', '24.07.18', '24.07.31', '24.08.22',
    '24.09.25', '24.10.22', '24.11.14', '24.12.10',
    '25.01.13', '25.02.03', '25.04.19', '25.05.23', '25.06.09'
]

# 날짜 변환 함수 추가
def convert_date(date_str):
    year = int('20' + date_str[:2])
    month = int(date_str[3:5])
    day = int(date_str[6:])
    return pd.to_datetime(f'{year}-{month}-{day}')

# 데이터 불러오기
all_data = []
for sheet in sheet_names:
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet}'
        df = pd.read_csv(url)
        df['날짜'] = convert_date(sheet)  # 날짜 변환
        all_data.append(df)
    except:
        pass

merged_df = pd.concat(all_data, ignore_index=True)
merged_df = merged_df.sort_values('날짜')  # 날짜순 정렬
merged_df['단지명_정제'] = merged_df['단지명'].str.replace(" ", "").str.strip()

# 가장 최신 데이터 기준
latest_date = merged_df['날짜'].max()
latest_df = merged_df[merged_df['날짜'] == latest_date]

# 평단가 계산 (매매가 / 24)
if '매매가' in latest_df.columns:
    latest_df = latest_df.copy()
    # 매매가를 24로 나누어 평단가 계산
    latest_df['계산된평단가'] = latest_df['매매가'] / 24


# 메인 컨텐츠 시작 전에 div 추가
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

# 정렬 기준 선택
st.markdown("#### 정렬 기준 선택")
sort_option = st.radio("정렬 기준", options=["평단가", "이름순", "갭가격", "총세대수"], horizontal=True, label_visibility="collapsed")

# 갭가격 계산
if '매매가' in latest_df.columns and '전세가' in latest_df.columns:
    latest_df = latest_df.copy()
    latest_df['갭가격'] = latest_df['매매가'] - latest_df['전세가']

# 단지 정보 정리
def get_sort_value(row, key):
    try:
        return float(row[key])
    except:
        return -1

sort_key = "단지명_정제"
ascending = True
if sort_option == "평단가":
    sort_key = "계산된평단가"  # 계산된 평단가 사용
    ascending = False
elif sort_option == "이름순":
    sort_key = "단지명_정제"
elif sort_option == "갭가격":
    sort_key = "갭가격"
    ascending = False
elif sort_option == "총세대수":
    sort_key = "총세대수"
    ascending = False

latest_df = latest_df.copy()
latest_df = latest_df[latest_df[sort_key].notnull()]
latest_df = latest_df.sort_values(by=sort_key, ascending=ascending)

# 단지 선택 상태
if 'selected' not in st.session_state:
    st.session_state.selected = set()

# 단지 버튼 UI
st.markdown("#### 비교할 단지를 선택하세요")

# 선택된 단지 개수 표시 (실시간 업데이트) - Fixed 영역
selected_display_names = []
for name in st.session_state.selected:
    row = latest_df[latest_df['단지명_정제'] == name]
    if not row.empty:
        selected_display_names.append(row.iloc[0]['단지명'])

st.markdown(f"""
<div class='selected-info'>
    <strong>선택된 단지: {len(st.session_state.selected)}개</strong> - {', '.join(selected_display_names) if selected_display_names else '없음'}
</div>
""", unsafe_allow_html=True)

# 단지 목록을 반응형으로 나열 - Fixed 영역
st.markdown("<div class='button-container'>", unsafe_allow_html=True)

# 반응형 컬럼 계산 (화면 너비에 따라 자동 조정)
import math
total_complexes = len(latest_df)
# 버튼 너비 180px + gap 2px = 약 182px per button
# 기본적으로 많은 컬럼을 만들어서 flexbox가 자동으로 wrap하도록 함
max_cols = min(20, total_complexes)  # 최대 20개 컬럼까지
button_cols = st.columns(max_cols)

for i, row in enumerate(latest_df.itertuples()):
    name = row.단지명_정제
    display_name = row.단지명
    
    # 정렬 기준에 따른 값 표시
    value = ""
    if sort_key == "계산된평단가" and hasattr(row, '계산된평단가'):
        try:
            value = f"({float(row.계산된평단가):,.0f})"
        except:
            value = ""
    elif sort_key == "갭가격" and hasattr(row, '갭가격'):
        try:
            value = f"({float(row.갭가격):,.0f})"
        except:
            value = ""
    elif sort_key == "총세대수" and hasattr(row, '총세대수'):
        try:
            value = f"({float(row.총세대수):,.0f}세대)"
        except:
            value = ""
    
    # 기본값으로 계산된 평단가 항상 표시
    if not value and hasattr(row, '계산된평단가'):
        try:
            value = f"({float(row.계산된평단가):,.0f})"
        except:
            value = ""
    
    label = f"{display_name} {value}"
    is_selected = name in st.session_state.selected
    
    # 선택된 단지는 다른 스타일로 표시
    button_type = "primary" if is_selected else "secondary"
    
    col_idx = i % max_cols
    with button_cols[col_idx]:
        if st.button(label, key=f"btn_{name}", type=button_type):
            if is_selected:
                st.session_state.selected.remove(name)
            else:
                st.session_state.selected.add(name)

st.markdown("</div>", unsafe_allow_html=True)

selected_complexes = list(st.session_state.selected)

# 선택된 단지 표시
if selected_complexes:
    st.markdown("#### 선택된 단지 목록")
    st.markdown(f"**{', '.join(selected_display_names)}**")

# 네비게이션 링크
st.markdown("### 단지별 가격 비교 그래프")
st.markdown("""
<div class="nav-links">
    <a href="#pyeongdan">📊 평단가</a>
    <a href="#maemega">📊 매매가</a>
    <a href="#jeonsega">📊 전세가</a>
    <a href="#gapga">📊 갭가격</a>
</div>
""", unsafe_allow_html=True)

def draw_graph(df, subject, selected_list, anchor_id):
    plt.close('all')
    st.markdown(f"<div id='{anchor_id}' class='graph-box'>", unsafe_allow_html=True)
    st.subheader(f"📈 {subject} 변화 그래프")
    
    if not selected_list:
        st.write("단지를 선택해주세요.")
        return
    
    fig, ax = plt.subplots(figsize=(12, 4))
    has_data = False
    
    for name in selected_list:
        data = df[df['단지명_정제'] == name]
        if not data.empty and subject in data.columns:
            # 데이터 타입 체크 및 변환
            try:
                if data[subject].dtype == 'object':
                    # 문자열인 경우 콤마 제거 후 숫자로 변환
                    values = pd.to_numeric(data[subject].astype(str).str.replace(',', ''), errors='coerce')
                else:
                    # 이미 숫자형인 경우 직접 사용
                    values = data[subject]
                
                ax.plot(data['날짜'], values, marker='o', label=name)
                has_data = True
            except Exception as e:
                st.error(f"데이터 변환 중 오류 발생: {name} - {e}")
                continue
    
    if has_data:
        ax.set_xlabel("날짜")
        ax.set_ylabel(subject)
        ax.set_title(f"{subject} 변화 추이")
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # y축 포맷 설정
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.write(f"선택된 단지들의 {subject} 데이터가 없습니다.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# 그래프 출력
if selected_complexes:
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    draw_graph(merged_df, "평단가", selected_complexes, "pyeongdan")
    draw_graph(merged_df, "매매가", selected_complexes, "maemega")
    draw_graph(merged_df, "전세가", selected_complexes, "jeonsega")
    
    # 갭가격 계산 및 출력
    gap_df = merged_df.copy()
    if "매매가" in gap_df.columns and "전세가" in gap_df.columns:
        gap_df["갭가격"] = gap_df["매매가"] - gap_df["전세가"]
        draw_graph(gap_df, "갭가격", selected_complexes, "gapga")
    else:
        st.warning("갭가격 계산을 위한 매매가/전세가 데이터가 없습니다.")
    
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("비교할 단지를 선택해주세요.")