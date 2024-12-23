#include <SoftwareSerial.h>

const int buttonA = 5;          
const int buttonB = 6;          
const int buttonReset = 4;      
const int RLED = 3;
const int BLED = 2;

// TX는 라즈베리파이의 RX와 연결, RX는 라즈베리파이의 TX와 연결
SoftwareSerial softSerial(9, 10);  // RX(9), TX(10)

bool lastStateA = HIGH;
bool lastStateB = HIGH;
bool lastStateReset = HIGH;

// 전역 변수 추가
bool ledStateA = false;
bool ledStateB = false;

// 디바운스 관련 변수
unsigned long lastDebounceTimeA = 0;
unsigned long lastDebounceTimeB = 0;
unsigned long lastDebounceTimeReset = 0;
const unsigned long debounceDelay = 50;  // 디바운스 시간 줄임

void setup() {
  softSerial.begin(9600);
  Serial.begin(9600);

  pinMode(buttonA, INPUT_PULLUP);
  pinMode(buttonB, INPUT_PULLUP);
  pinMode(buttonReset, INPUT_PULLUP);
  pinMode(RLED, OUTPUT);
  pinMode(BLED, OUTPUT);
  // 시작할 때 통신 테스트
  delay(1000);  // 라즈베리파이가 준비될 때까지 대기
  softSerial.println("Arduino Ready");
  Serial.println("Arduino Ready");
}

void loop() {
  // A 버튼 처리
  int readingA = digitalRead(buttonA);
  if (readingA != lastStateA) {
    lastDebounceTimeA = millis();
  }
  if ((millis() - lastDebounceTimeA) > debounceDelay) {
    if (readingA == LOW && lastStateA == HIGH) {  // 버튼이 눌렸을 때만
      ledStateA = !ledStateA;  // LED 상태 토글
      digitalWrite(BLED, ledStateA ? HIGH : LOW);
      softSerial.println("toggle_a");
      Serial.println("toggle_a");
    }
  }
  lastStateA = readingA;

  // B 버튼 처리
  int readingB = digitalRead(buttonB);
  if (readingB != lastStateB) {
    lastDebounceTimeB = millis();
  }
  if ((millis() - lastDebounceTimeB) > debounceDelay) {
    if (readingB == LOW && lastStateB == HIGH) {  // 버튼이 눌렸을 때만
      ledStateB = !ledStateB;  // LED 상태 토글
      digitalWrite(RLED, ledStateB ? HIGH : LOW);
      softSerial.println("toggle_b");
      Serial.println("toggle_b");
    }
  }
  lastStateB = readingB;

  // 리셋 버튼 처리
  int readingReset = digitalRead(buttonReset);
  if (readingReset != lastStateReset) {
    lastDebounceTimeReset = millis();
  }
   if (readingReset == LOW && lastStateReset == HIGH) {
      
      Serial.println("Sending reset signal");
      softSerial.println("timers have been reset");
      delay(10);

  }
  lastStateReset = readingReset;

  // 라즈베리파이로부터 데이터 수신
  if (softSerial.available()) {
    String received = softSerial.readStringUntil('\n');
    Serial.println("Received: " + received);  // 수신된 데이터 확인용
  }

  delay(10);
}
