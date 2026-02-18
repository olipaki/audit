import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from datetime import datetime
import schedule
import time

def send_audit_report():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 메일 발송 프로세스를 시작합니다.")
    
    try:
        # 1. 저장된 엑셀 데이터 불러오기
        file_path = "organized_audit_data.xlsx"
        df = pd.read_excel(file_path)
        
        # 2. 오늘 날짜 기준으로 D-Day 다시 계산 (매일 날짜가 흐르기 때문)
        today = datetime.now()
        df['Expiry Date'] = pd.to_datetime(df['Expiry Date'])
        df['Days_Left'] = (df['Expiry Date'] - today).dt.days
        
        # 3. 구간별 데이터 추출
        urgent_30 = df[(df['Days_Left'] >= 0) & (df['Days_Left'] <= 30)]
        urgent_60 = df[(df['Days_Left'] > 30) & (df['Days_Left'] <= 60)]
        urgent_90 = df[(df['Days_Left'] > 60) & (df['Days_Left'] <= 90)]
        urgent_120 = df[(df['Days_Left'] > 90) & (df['Days_Left'] <= 120)]
        overdue = df[df['Days_Left'] < 0]

        # 4. 메일 본문(HTML) 작성 - 한눈에 보기 좋게 구성
        subject = f"[정기알림] {today.strftime('%Y-%m-%d')} 공장 심사 만기 임박 리포트"
        
        body = f"""
        <h3>🏭 주간 공장 심사(Audit) 현황 보고서</h3>
        <p>본 메일은 매주 금요일 발송되는 자동 알림입니다.</p>
        <hr>
        <p><b>🔴 30일 이내 임박:</b> {len(urgent_30)}건</p>
        <p><b>🟠 60일 이내 임박:</b> {len(urgent_60)}건</p>
        <p><b>🟢 90일 이내 임박:</b> {len(urgent_90)}건</p>
        <p><b>🔵 120일 이내 임박:</b> {len(urgent_120)}건</p>
        <p><b>⚠️ 만기 지남:</b> <span style='color:red;'>{len(overdue)}건</span></p>
        <hr>
        <h4>[상세 리스트 - 60일 이내 핵심 관리 대상]</h4>
        """
        
        # 60일 이내 데이터가 있다면 표 형태로 추가
        top_urgency = pd.concat([overdue, urgent_30, urgent_60])
        if not top_urgency.empty:
            body += top_urgency[['Buyer', 'Factory', 'Expiry Date', 'Days_Left']].to_html(index=False)
        else:
            body += "<p>현재 60일 이내 임박 건이 없습니다. 관리 상태 양호합니다.</p>"

        # 5. 메일 발송 설정
        sender_email = "본인메일@gmail.com"  # 본인 Gmail 주소
        app_password = "xxxx xxxx xxxx xxxx" # 구글 앱 비밀번호 16자리
        receiver_email = "받는사람@company.com" # 수신자 메일 주소

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.attach(MIMEText(body, 'html'))

        # SMTP 서버 연결 및 발송
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.send_message(msg)
            
        print("✅ 메일 발송 성공!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

# --- 스케줄러 설정 ---

# [테스트용] 즉시 발송을 확인하고 싶다면 아래 코드 한 줄의 주석(#)을 풀고 실행해 보세요.
# send_audit_report() 

# [실제 운영용] 매주 금요일 오전 9시 정각에 실행
schedule.every().friday.at("09:00").do(send_audit_report)

print("🚀 스케줄러가 가동되었습니다. 이 터미널 창을 끄지 마세요.")
while True:
    schedule.run_pending()
    time.sleep(60) # 1분마다 조건 확인