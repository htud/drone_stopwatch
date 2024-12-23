import serial
import pandas as pd
from tabulate import tabulate
import os

# 시리얼 포트 설정 (Arduino 포트와 보드 레이트에 맞게 설정)
ser = serial.Serial('COM8', 9600)  # 실제 포트 이름으로 변경하세요.

# 엑셀 파일 이름 설정
file_name = "timer_data.xlsx"

# 데이터 저장을 위한 빈 데이터프레임 생성
data = {
    "팀": [],
    "A 타임": [],
    "B 타임": []
}

# 초기 DataFrame 생성 및 저장
df = pd.DataFrame(data)
df.to_excel(file_name, index=False, sheet_name="Timer Data")

print("엑셀 파일 초기화 완료: timer_data.xlsx")

# 초기 팀 번호 설정
team_number = 1
time_a = None  # A 타이머 결과
time_b = None  # B 타이머 결과


# 현재 DataFrame을 테이블 형식으로 출력하는 함수 수정
def print_table(df):
    print("\n=== 현재 기록된 데이터 ===")
    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
    print("========================\n")


try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            print(f"\n수신된 데이터: {line}")

            if "Sending reset signal" in line:
                print("➡️ 리셋 신호 수신됨")
                
            elif "Received: A_FINAL:" in line:
                time_a = line.split("Received: A_FINAL:")[1].strip()
                print(f"➡️ A 타이머 정지 - 기록: {time_a}")
                
            elif "Received: B_FINAL:" in line:
                time_b = line.split("Received: B_FINAL:")[1].strip()
                print(f"➡️ B 타이머 정지 - 기록: {time_b}")
                
                if time_a is not None and time_b is not None:
                    data["팀"].append(f"{team_number}팀")
                    data["A 타임"].append(time_a)
                    data["B 타임"].append(time_b)

                    df = pd.DataFrame(data)
                    try:
                        df.to_excel(file_name, index=False)
                        print(f"\n✅ 저장 완료!")
                    except PermissionError:
                        print(f"\n❌ 엑셀 파일이 열려있어 저장할 수 없습니다. 파일을 닫고 다시 시도해주세요.")
                        # 데이터를 다시 제거 (저장 실패)
                        data["팀"].pop()
                        data["A 타임"].pop()
                        data["B 타임"].pop()
                        continue

                    print(f"팀: {team_number}팀")
                    print(f"A 타임: {time_a}")
                    print(f"B 타임: {time_b}")
                    
                    # 테이블 형식으로 전체 데이터 출력
                    print_table(df)

                    team_number += 1
                    time_a = None
                    time_b = None

except KeyboardInterrupt:
    print("프로그램 종료")

finally:
    ser.close()
