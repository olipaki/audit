# import streamlit as st
# import pandas as pd
# from datetime import datetime

# st.set_page_config(page_title="Audit 관리 시스템", layout="wide")
# st.title("QA team")

# uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])


# if uploaded_file:
#     # 1. 헤더 없이 데이터를 통째로 가져옵니다.
#     # skiprows를 조정하여 실제 데이터가 시작되는 행 바로 전까지 건너뜁니다.
#     df = pd.read_excel(uploaded_file, header=None, skiprows=2) 

#     # 2. 알려주신 열 위치에 맞춰 이름을 강제로 붙여줍니다. (파이썬은 0부터 숫자를 셉니다)
#     # C열=2, F열=5, J열=9
#     try:
#         df = df[[2, 5, 9]] # 필요한 열만 추출
#         df.columns = ['Buyer', 'Factory', 'Expiry Date'] # 이름 부여
        
#         # 3. 날짜 변환 및 D-Day 계산
#         df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce').dt.date
#         df = df.dropna(subset=['Expiry Date']) # 날짜 없는 행 제거
        
#         today = datetime.now().date()
#         df['D-Day'] = df['Expiry Date'].apply(lambda x: (x - today).days)

#         # 4. 색상 로직 정의
#         def color_expiry(row):
#             d_day = row['D-Day']
#             if d_day < 0: return ['background-color: #FFC0CB'] * len(row) # 핑크
#             elif d_day <= 30: return ['background-color: #FF0000; color: white'] * len(row) # 빨강
#             elif d_day <= 60: return ['background-color: #FFA500'] * len(row) # 주황
#             elif d_day <= 90: return ['background-color: #008000; color: white'] * len(row) # 녹색
#             elif d_day <= 120: return ['background-color: #87CEEB'] * len(row) # 하늘색
#             return [''] * len(row)

#         st.subheader(" 공장별 만기 현황")
#         st.dataframe(df.style.apply(color_expiry, axis=1), use_container_width=True)
        
#         # 데이터 저장 버튼
#         if st.button("현재 데이터 정리하여 저장하기"):
#             df.to_excel("organized_audit_data.xlsx", index=False)
#             st.success("데이터가 성공적으로 저장되었습니다. 이제 mailer.py를 실행할 수 있습니다.")

#     except Exception as e:
#         st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
#         st.info("엑셀의 컬럼 위치가 C, F, J열이 맞는지 다시 한번 확인해주세요.")

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date

st.set_page_config(page_title="Audit Visualizer", layout="wide")
st.title("QA team")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    # 1. 데이터 로드 (J열이 만기일인 구조 반영) / 병합 해제
    df = pd.read_excel(uploaded_file, header=None, skiprows=2)
    df = df[[2, 5, 9]] # C(Buyer), F(Factory), J(Expiry Date)
    df.columns = ['Buyer', 'Factory', 'Expiry Date']
    
    # 데이터 정리
    df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce').dt.date
    df = df.dropna(subset=['Expiry Date'])
    today = date.today()
    df['D-Day'] = df['Expiry Date'].apply(lambda x: (x - today).days)

    # 2. 색상 카테고리 분류 함수
    def get_color_label(d_day):
        if d_day < 0: return '만기 지남 (핑크)'
        elif d_day <= 30: return '30일 이내 (빨강)'
        elif d_day <= 60: return '60일 이내 (주황)'
        elif d_day <= 90: return '90일 이내 (녹색)'
        elif d_day <= 120: return '120일 이내 (하늘)'
        return '여유 (기타)'

    df['Status_Label'] = df['D-Day'].apply(get_color_label)

    # 색상 맵핑 설정 /다시확인필요 / ß
    color_map = {
        '만기 지남 (핑크)': '#FFC0CB',
        '30일 이내 (빨강)': '#FF0000',
        '60일 이내 (주황)': '#FFA500',
        '90일 이내 (녹색)': '#008000',
        '120일 이내 (하늘)': '#87CEEB',
        '여유 (기타)': '#D3D3D3'
    }

    # 3. 간트 차트(Timeline) 생성 / 오류확인필요
    st.subheader("🗓️ 만기 일정 타임라인 그래프")
    
    # 그래프용 데이터 가공 (오늘부터 만기일까지의 막대 생성)
    df['Start'] = today
    
    fig = px.timeline(
        df, 
        x_start="Start", 
        x_end="Expiry Date", 
        y="Factory", 
        color="Status_Label",
        hover_data=["Buyer", "D-Day"],
        color_discrete_map=color_map,
        title="공장별 심사 만기 로드맵"
    )

    # 그래프 확인 필요!!
    fig.update_yaxes(autorange="reversed") # 최신 항목이 위로 오게
    fig.update_layout(
        xaxis_title="날짜 흐름",
        yaxis_title="공장명",
        legend_title="상태 분류",
        height=600 # 그래프 높이 조절
    )

    st.plotly_chart(fig, use_container_width=True)

    # 4. 기존 상세 데이터 표 출력
    st.divider()
    st.subheader("📋 상세 데이터 리스트")
    st.dataframe(df[['Buyer', 'Factory', 'Expiry Date', 'D-Day', 'Status_Label']], use_container_width=True)