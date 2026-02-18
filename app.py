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
###################################################버전22

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# from datetime import datetime

# st.set_page_config(page_title="월별 Audit 현황", layout="wide")
# st.title("📅 월별 심사 만기 공장 수 현황")

# uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요", type=["xlsx"])

# if uploaded_file:
#     # 1. 데이터 읽기 (C:Buyer, F:Factory, J:Expiry Date)
#     # 엑셀 구조에 따라 skiprows와 usecols를 조정하여 깔끔하게 가져옵니다.
#     try:
#         df = pd.read_excel(uploaded_file, header=None, skiprows=2)
#         df = df[[2, 5, 9]] 
#         df.columns = ['Buyer', 'Factory', 'Expiry Date']
        
#         # 날짜 데이터 정제
#         df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce')
#         df = df.dropna(subset=['Expiry Date']) # 날짜 없는 데이터 삭제
        
#         # 2. '월(Month)' 정보 추출 및 D-Day 계산
#         df['Month'] = df['Expiry Date'].dt.month
#         df['Month_Name'] = df['Expiry Date'].dt.strftime('%m월') # '01월', '02월' 형태
        
#         today = datetime.now()
#         df['D-Day'] = (df['Expiry Date'] - today).dt.days

#         # 3. 색상 카테고리 분류 (기존 규칙)
#         def get_color(d_day):
#             if d_day < 0: return '만기 지남 (핑크)'
#             elif d_day <= 30: return '30일 이내 (빨강)'
#             elif d_day <= 60: return '60일 이내 (주황)'
#             elif d_day <= 90: return '90일 이내 (녹색)'
#             elif d_day <= 120: return '120일 이내 (하늘)'
#             return '여유 (기타)'

#         df['Status'] = df['D-Day'].apply(get_color)

#         # 4. 월별 공장 수 집계 (시각화용 데이터프레임 생성)
#         # 월별로 상태별 공장 개수를 셉니다.
#         summary_df = df.groupby(['Month_Name', 'Status']).size().reset_index(name='Factory_Count')
        
#         # 월 순서 정렬 (1월~12월)
#         month_order = [f"{i:02d}월" for i in range(1, 13)]

#         # 5. 가로 바 차트 생성
#         st.subheader("📊 월별 만기 예정 공장 수 (1월-12월)")
        
#         color_map = {
#             '만기 지남 (핑크)': '#FFC0CB',
#             '30일 이내 (빨강)': '#FF0000',
#             '60일 이내 (주황)': '#FFA500',
#             '90일 이내 (녹색)': '#008000',
#             '120일 이내 (하늘)': '#87CEEB',
#             '여유 (기타)': '#D3D3D3'
#         }

#         fig = px.bar(
#             summary_df, 
#             x="Factory_Count", # 공장 숫자 (가로 길이)
#             y="Month_Name",    # 월 (세로 축)
#             color="Status", 
#             orientation='h',   # 가로 형태 바
#             category_orders={"Month_Name": month_order},
#             color_discrete_map=color_map,
#             text="Factory_Count", # 바 위에 숫자 표시
#             title="월별/상태별 공장 만기 현황"
#         )

#         fig.update_layout(
#             xaxis_title="공장 수 (개)",
#             yaxis_title="해당 월",
#             legend_title="상태",
#             height=600
#         )

#         st.plotly_chart(fig, use_container_width=True)

#         # 6. 상세 목록
#         st.divider()
#         st.subheader("📋 선택된 월의 상세 데이터")
#         st.dataframe(df[['Month_Name', 'Factory', 'Buyer', 'Expiry Date', 'Status']], use_container_width=True)

#     except Exception as e:
#         st.error(f"데이터 처리 중 오류가 발생했습니다: {e}")
################################
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Audit 임박 현황", layout="wide")
st.title("마감 임박 현황")
st.write(f"기준일: {datetime.now().strftime('%Y-%m-%d')}")

uploaded_file = st.file_uploader("엑셀 파일을 업로드하세요(병합해체필수)", type=["xlsx"])

if uploaded_file:
    try:
        # 1. 데이터 추출 (C=2, F=5, J=9)
        raw_df = pd.read_excel(uploaded_file, header=None)
        df = raw_df.iloc[:, [2, 5, 9]].copy()
        df.columns = ['Buyer', 'Factory', 'Expiry Date']

        # 2. 데이터 정제 및 날짜 변환
        df['Expiry Date'] = pd.to_datetime(df['Expiry Date'], errors='coerce')
        df = df.dropna(subset=['Expiry Date']) # 날짜 없는 행 제거
        df = df.drop_duplicates() # 중복 행 제거

        # 3. 오늘 기준 남은 일수 계산
        today = datetime.now()
        df['Days_Left'] = (df['Expiry Date'] - today).dt.days

        # 4. 요청하신 구간별 카테고리 분류 (D-Day 기준)
        def classify_urgency(days):
            if days < 0: return '0. 만기 지남'
            elif days <= 30: return '1. 30일 이내'
            elif days <= 60: return '2. 60일 이내'
            elif days <= 90: return '3. 90일 이내'
            elif days <= 120: return '4. 120일 이내'
            else: return '5. 120일 초과'

        df['Urgency'] = df['Days_Left'].apply(classify_urgency)

        # 5. 시각화용 데이터 집계 (구간별 공장 수)
        summary = df.groupby('Urgency').size().reset_index(name='Factory_Count')

        # [중요] 사용자가 원하는 정렬 순서 정의
        # order_list = ['30일 이내', '60일 이내', '90일 이내', '120일 이내', '만기지남', '120일 초과']

        # 6. 상단 요약 차트 (바 형태)
        st.subheader("📊 임박 구간별 공장 수")
        
        # 색상 설정
        color_map = {
            '0. 만기 지남': '#FFC0CB', # 핑크
            '1. 30일 이내': '#FF0000', # 빨강
            '2. 60일 이내': '#FFA500', # 주황
            '3. 90일 이내': '#008000', # 녹색
            '4. 120일 이내': '#87CEEB', # 하늘
            '5. 120일 초과': '#D3D3D3'  # 회색
        }

        fig = px.bar(
            summary, 
            x="Factory_Count", 
            y="Urgency", 
            color="Urgency",
            orientation='h',
            text="Factory_Count",
            color_discrete_map=color_map,
            title="오늘로부터 남은 기간별 공장 분포"
        )
        fig.update_layout(showlegend=False, yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig, use_container_width=True)

        # 7. 하단 상세 데이터 (가장 임박한 순서대로 정렬)
        st.divider()
        st.subheader("🔍 임박 항목 리스트 (가장 빠른 날짜순)")
        
        # 임박한 순서대로 정렬 (만기 지난 것부터)
        display_df = df.sort_values(by='Days_Left', ascending=True)
        
        # 보기 좋게 날짜 형식 변경
        display_df['Expiry Date'] = display_df['Expiry Date'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df[['Urgency', 'Buyer', 'Factory', 'Expiry Date', 'Days_Left']],
            use_container_width=True,
            hide_index=True
        )

        # 8. 데이터 저장 버튼 (메일 발송용)
        if st.button("현재 리스트 저장 (organized_audit_data.xlsx)"):
            display_df.to_excel("organized_audit_data.xlsx", index=False)
            st.success("데이터가 저장되었습니다. 이제 mailer.py에서 이 파일을 읽어 발송합니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다. 엑셀의 C, F, J열을 확인해주세요. (상세: {e})")