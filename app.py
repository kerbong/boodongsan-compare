import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import platform

# 페이지를 넓게 사용하도록 설정
st.set_page_config(layout="wide")

# OS에 따라 적절한 한글 폰트 설정
if platform.system() == 'Windows':
    matplotlib.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin': # Mac OS
    matplotlib.rc('font', family='AppleGothic')
else: # Colab, Linux 등
    # 나눔고딕 폰트 경로 설정 (코랩 등 환경에 맞게 설치 필요)
    matplotlib.rc('font', family='NanumGothic')
# 마이너스 부호 깨짐 방지
matplotlib.rcParams['axes.unicode_minus'] = False


# --- CSS 및 JavaScript 스타일링 ---
st.markdown("""
<style>
/* 전체 페이지의 여백 제거 */
body {
    margin: 0;
    padding: 0;
}
/* 고정 헤더 컨테이너 */
.fixed-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
/* 선택 정보 표시 바 */
.selected-info-bar {
    padding: 10px 20px;
    border-bottom: 1px solid #e0e0e0;
    font-size: 14px;
    line-height: 1.5;
}
/* 단지 선택 버튼들을 감싸는 컨테이너 */
.button-container {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 2px !important;
    padding: 10px 20px;
    max-height: 300px; 
    overflow-y: auto;
    align-items: flex-start !important;
}
/* Streamlit이 각 버튼을 감싸는 컨테이너를 강제로 flex 아이템처럼 동작하게 함 */
.button-container > div {
    width: auto !important;
    flex: 0 0 auto !important;
    margin: 0 !important;
}
/* Streamlit 컬럼 컨테이너 무력화 */
.button-container .element-container,
.button-container .stButton,
.button-container > div[data-testid="stElementContainer"],
.button-container > div[data-testid="column"] {
    width: auto !important;
    flex: none !important;
    margin: 0 !important;
    padding: 0 !important;
}
/* Streamlit 버튼 기본 스타일 */
.stButton > button {
    min-width: 120px !important;
    max-width: 180px !important;
    height: 35px !important;
    font-size: 11px !important;
    padding: 4px 12px !important;
    border-radius: 4px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    text-align: left !important;
    margin: 0 !important;
    border: 1px solid rgba(49, 51, 63, 0.2) !important;
    display: inline-block !important;
}
/* 선택되지 않은 버튼 (secondary) */
.stButton > button[kind="secondary"] {
    background-color: #f0f2f6 !important;
    color: rgba(49, 51, 63, 0.8) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #ff4b4b !important;
    color: #ff4b4b !important;
}
/* 선택된 버튼 (primary) */
.stButton > button[kind="primary"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border-color: #ff4b4b !important;
}
/* 메인 콘텐츠 영역: JS가 동적으로 상단 여백을 설정 */
.main-content {
    padding-left: 20px;
    padding-right: 20px;
}
/* 그래프를 감싸는 컨테이너 스타일 */
.graph-container {
    width: 100%;
    margin-top: 20px;
}
.graph-box {
    margin-bottom: 30px;
}
/* 네비게이션 링크 스타일 */
.nav-links a {
    margin-right: 20px;
    text-decoration: none;
    font-weight: bold;
    color: #1f77b4;
}
</style>

<script>
    function adjustMainContentPadding() {
        const header = document.querySelector('.fixed-header');
        const mainContent = document.querySelector('.main-content');
        if (header && mainContent) {
            const headerHeight = header.offsetHeight;
            mainContent.style.paddingTop = headerHeight + 20 + 'px';
        }
    }
    const observer = new MutationObserver((mutations) => {
        window.requestAnimationFrame(adjustMainContentPadding);
    });
    observer.observe(document.body, { childList: true, subtree: true });
    window.addEventListener('load', adjustMainContentPadding);
    window.addEventListener('resize', adjustMainContentPadding);
</script>
""", unsafe_allow_html=True)


# --- 데이터 로딩 ---
sheet_id = '1cUZ9-bMzeokaAGb84YAh--KngCM0U0-9pJgXHXrJ0U8'
sheet_names = [
    '24.06.07', '24.06.26', '24.07.18', '24.07.31', '24.08.22',
    '24.09.25', '24.10.22', '24.11.14', '24.12.10',
    '25.01.13', '25.02.03', '25.04.19', '25.05.23', '25.06.09'
]

def convert_date(date_str):
    return pd.to_datetime('20' + date_str, format='%Y.%m.%d')

@st.cache_data
def load_data():
    all_data = []
    for sheet in sheet_names:
        try:
            url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet}'
            df = pd.read_csv(url)
            df['날짜'] = convert_date(sheet)
            all_data.append(df)
        except Exception as e:
            st.error(f"시트 '{sheet}' 로딩 중 오류 발생: {e}")
    
    if not all_data:
        return pd.DataFrame(), pd.DataFrame()
        
    merged_df = pd.concat(all_data, ignore_index=True)
    merged_df.sort_values('날짜', inplace=True)
    merged_df['단지명_정제'] = merged_df['단지명'].str.replace(" ", "").str.strip()

    # 숫자형으로 변환해야 할 모든 열을 처리
    # '매매가', '전세가' 등은 '억' 단위의 실수(e.g., 15.2)로 가정
    for col in ['매매가', '전고점', '전세가']:
        if col in merged_df.columns:
            merged_df[col] = pd.to_numeric(merged_df[col].astype(str).str.replace(',', ''), errors='coerce')

    # 그래프에 필요한 모든 데이터 컬럼 계산
    # '매매가'가 '억' 단위이므로 '평단가'를 '만원' 단위로 계산
    merged_df['평단가'] = (merged_df['매매가'] * 10000) / 24
    # '갭가격'은 '억' 단위로 계산됨
    merged_df['갭가격'] = merged_df['매매가'] - merged_df['전세가']
    merged_df['하락/상승률'] = ((merged_df['매매가'] / merged_df['전고점'] * 100) - 100).round(1)

    # 가장 최신 데이터 추출
    latest_date = merged_df['날짜'].max()
    latest_df = merged_df[merged_df['날짜'] == latest_date].copy()
    
    return merged_df, latest_df

merged_df, latest_df = load_data()

if latest_df.empty:
    st.error("데이터를 불러오지 못했습니다. 구글 시트 ID나 네트워크 연결을 확인해주세요.")
    st.stop()

# 세션 상태 초기화
if 'selected' not in st.session_state:
    st.session_state.selected = set()
if 'sort_option' not in st.session_state:
    st.session_state.sort_option = "평단가"

# --- 상단 고정 헤더 영역 ---
st.markdown("<div class='fixed-header'>", unsafe_allow_html=True)

# 선택된 단지 정보 표시
selected_display_names = [
    latest_df[latest_df['단지명_정제'] == name_refined].iloc[0]['단지명']
    for name_refined in st.session_state.selected
    if not latest_df[latest_df['단지명_정제'] == name_refined].empty
]
selected_info_text = f"<strong>선택된 단지: {len(st.session_state.selected)}개</strong>"
if selected_display_names:
    selected_info_text += f" - {', '.join(selected_display_names)}"
st.markdown(f"<div class='selected-info-bar'>{selected_info_text}</div>", unsafe_allow_html=True)


# 단지 선택 버튼 목록
st.markdown("<div class='button-container'>", unsafe_allow_html=True)

# 정렬 기준에 따라 데이터프레임 정렬
sort_map = {
    "평단가": ("평단가", False),
    "이름순": ("단지명_정제", True),
    "갭가격": ("갭가격", False),
    "총세대수": ("총세대수", False)
}
sort_key, ascending = sort_map.get(st.session_state.sort_option, ("평단가", False))
if sort_key in latest_df.columns:
    sortable_df = latest_df.dropna(subset=[sort_key]).copy()
    sortable_df.sort_values(by=sort_key, ascending=ascending, inplace=True)
else:
    sortable_df = latest_df.copy()

# 버튼들을 컬럼으로 감싸서 가로 배열 강제
num_buttons = len(sortable_df)
cols_per_row = 8  # 한 줄에 표시할 버튼 수
num_rows = (num_buttons + cols_per_row - 1) // cols_per_row

button_idx = 0
for row in range(num_rows):
    cols = st.columns(cols_per_row)
    for col_idx in range(cols_per_row):
        if button_idx < num_buttons:
            row_data = sortable_df.iloc[button_idx]
            name_refined = row_data.단지명_정제
            display_name = row_data.단지명
            value = ""
            if st.session_state.sort_option == "평단가" and pd.notna(row_data.평단가):
                value = f"({row_data.평단가:,.0f})"
            elif st.session_state.sort_option == "갭가격" and pd.notna(row_data.갭가격):
                value = f"({row_data.갭가격:,.1f})" # 갭가격은 소수점 표시
            elif st.session_state.sort_option == "총세대수" and pd.notna(row_data.총세대수):
                value = f"({int(row_data.총세대수):,}세대)"
            
            button_label = f"{display_name} {value}"
            button_key = f"btn_{name_refined}"
            is_selected = name_refined in st.session_state.selected
            button_type = "primary" if is_selected else "secondary"
            
            with cols[col_idx]:
                if st.button(button_label, key=button_key, type=button_type):
                    if is_selected:
                        st.session_state.selected.remove(name_refined)
                    else:
                        st.session_state.selected.add(name_refined)
                    st.rerun()
            button_idx += 1

st.markdown("</div>", unsafe_allow_html=True) # button-container 닫기
st.markdown("</div>", unsafe_allow_html=True) # fixed-header 닫기

# --- 메인 콘텐츠 영역 ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🏠 네이버 부동산 매물(전용59㎡) 단지별 가격 비교</h1>", unsafe_allow_html=True)

# 정렬 기준 선택 라디오 버튼
st.markdown("#### 정렬 기준 선택")
sort_options = ["평단가", "이름순", "갭가격", "총세대수"]
new_sort_option = st.radio(
    "정렬 기준", 
    options=sort_options, 
    horizontal=True, 
    label_visibility="collapsed", 
    key='sort_radio_button',
    index=sort_options.index(st.session_state.sort_option)
)

if new_sort_option != st.session_state.sort_option:
    st.session_state.sort_option = new_sort_option
    st.rerun()

# 네비게이션 링크
st.markdown("### [그래프 바로가기]")
st.markdown("""
<div class="nav-links">
    <a href="#pyeongdan">📊 평단가</a>
    <a href="#maemega">📊 매매가</a>
    <a href="#jeonsega">📊 전세가</a>
    <a href="#gapga">📊 갭가격</a>
    <a href="#rate">📊 하락/상승률</a>
</div>
""", unsafe_allow_html=True)

# --- 그래프 그리는 함수 ---
def draw_graph(df, subject, selected_list, anchor_id):
    plt.close('all')
    st.markdown(f"<div id='{anchor_id}'></div>", unsafe_allow_html=True)
    st.subheader(f"📈 {subject} 변화 그래프")
    
    if not selected_list:
        st.info("비교할 단지를 선택해주세요.")
        return
        
    fig, ax = plt.subplots(figsize=(12, 5))
    has_data = False
    
    # subject에 따른 단위 설정
    unit_label = ""
    if subject in ['매매가', '전세가', '갭가격']:
        unit_label = "(억)"
    elif subject == '평단가':
        unit_label = "(만원)"
    elif subject == '하락/상승률':
        unit_label = "(%)"
    
    for name_refined in selected_list:
        data = df[df['단지명_정제'] == name_refined].copy()
        if not data.empty and subject in data.columns:
            data.dropna(subset=['날짜', subject], inplace=True)
            if not data.empty:
                display_name = data.iloc[0]['단지명']
                ax.plot(data['날짜'], data[subject], marker='o', linestyle='-', label=display_name)
                has_data = True
    
    if has_data:
        ax.set_xlabel("날짜")
        ax.set_ylabel(f"{subject} {unit_label}")
        ax.set_title(f"단지별 {subject} 변화 추이", pad=20)
        ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.tick_params(axis='x', rotation=30)
        
        # y축 포맷터 설정
        if subject in ['매매가', '전세가', '갭가격']:
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.1f}'))
        else: # 평단가, 하락/상승률
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
        
        plt.tight_layout(rect=[0, 0, 0.85, 1]) # 범례 공간 확보
        st.pyplot(fig)
    else:
        st.warning(f"선택된 단지에 대한 '{subject}' 데이터가 없습니다.")

# --- 그래프 출력 ---
if st.session_state.selected:
    st.markdown("<div class='graph-container'>", unsafe_allow_html=True)
    
    draw_graph(merged_df, "평단가", list(st.session_state.selected), "pyeongdan")
    draw_graph(merged_df, "매매가", list(st.session_state.selected), "maemega")
    draw_graph(merged_df, "전세가", list(st.session_state.selected), "jeonsega")
    draw_graph(merged_df, "갭가격", list(st.session_state.selected), "gapga")
    draw_graph(merged_df, "하락/상승률", list(st.session_state.selected), "rate")

    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("상단 목록에서 그래프에 표시할 단지를 1개 이상 선택해주세요.")

st.markdown("</div>", unsafe_allow_html=True) # main-content 닫기