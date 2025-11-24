"""
음성 인식 + 베이스 모델 대화 테스트 스크립트
마이크로 음성 입력 받아서 디너 봇과 대화
"""
import os
import sys
from dotenv import load_dotenv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'ignore')

# 프로젝트 루트 경로 (test 폴더의 상위 디렉토리)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 환경 변수 로드 (프로젝트 루트의 .env 파일)
load_dotenv(os.path.join(project_root, '.env'))

# 모듈 경로 추가
sys.path.insert(0, project_root)

from ai_module.voice.speech_recognizer import SpeechRecognizer
from ai_module.conversation.dialog_manager import DialogManager


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("    [음성 인식 + Groq API 대화 테스트]")
    print("="*60 + "\n")

    print("[알림] Groq API 사용")
    print("       - 음성 인식: Groq Whisper API (whisper-large-v3-turbo)")
    print("       - 대화 모델: Llama 3.3 70B (Groq API)")
    print("       - GPU 불필요 (클라우드 기반)\n")

    # 음성 인식기 초기화 (Groq Whisper API)
    try:
        speech_recognizer = SpeechRecognizer()
        print("[OK] Groq Whisper API 음성 인식 초기화 완료")
    except Exception as e:
        print(f"[X] 음성 인식기 초기화 실패: {e}")
        print("\n[해결 방법]")
        print("1. .env 파일에 GROQ_API_KEY가 설정되어 있는지 확인")
        print("2. https://console.groq.com/keys 에서 API 키 발급")
        return

    # 대화 관리자 초기화 (Groq API)
    try:
        print("[로딩] Groq API 연결 중...")
        dialog_manager = DialogManager()
        print("[OK] Groq 디너 봇 초기화 완료\n")
    except Exception as e:
        print(f"[X] 대화 관리자 초기화 실패: {e}")
        print("\n[해결 방법]")
        print("1. .env 파일에 GROQ_API_KEY가 설정되어 있는지 확인")
        print("2. 인터넷 연결 확인")
        return

    # 마이크 테스트
    print("[TEST] 마이크 테스트 중...")
    if not speech_recognizer.test_microphone():
        print("\n[X] 마이크 테스트 실패. 프로그램을 종료합니다.")
        return

    print("\n" + "="*60)

    # 대화 시작
    customer_name = input("고객 이름을 입력하세요: ").strip()
    if not customer_name:
        customer_name = "테스트 고객"

    print("\n" + "="*60, flush=True)
    greeting = dialog_manager.start_conversation(customer_name)
    print(f"\n시스템: {greeting}\n", flush=True)
    print("="*60, flush=True)

    print("\n[사용 방법]")
    print("   - 각 턴마다 v (음성) / t (텍스트) / q (종료) 선택")
    print("   - 음성 입력 시 녹음 시간 입력 (예: 5)")
    print("   - Ctrl+C로 종료")
    print("\n" + "="*60 + "\n")

    # 대화 루프
    turn = 1
    while True:
        try:
            print(f"\n[ 턴 {turn} ]")

            # 입력 모드 선택
            mode = input("입력 방법 선택 (v=음성 / t=텍스트 / q=종료): ").strip().lower()

            if mode == 'q':
                print("\n[종료] 사용자가 종료했습니다.")
                break

            elif mode == 'v':
                # 녹음 시간 입력
                duration_input = input("녹음 시간 (초, 기본 5초): ").strip()
                duration = int(duration_input) if duration_input.isdigit() else 5

                # 음성 입력
                user_input = speech_recognizer.recognize_from_microphone(duration=duration)

                if not user_input:
                    print("[X] 음성을 인식할 수 없습니다. 다시 시도하세요.")
                    continue

            elif mode == 't':
                # 텍스트 입력
                user_input = input("\n사용자 입력: ").strip()
                if not user_input:
                    print("[X] 입력이 비어있습니다. 다시 시도하세요.")
                    continue

            else:
                print("[X] 잘못된 입력입니다. v, t, q 중 하나를 선택하세요.")
                continue

            print(f"\n[사용자] {user_input}")

            # AI 응답 생성
            print("\n[처리중] AI가 생각하는 중...")
            response, order_data = dialog_manager.process_user_input(user_input)

            print(f"\n시스템: {response}")

            # 주문 데이터 표시
            if order_data:
                print(f"\n[주문 정보 업데이트]")
                for key, value in order_data.items():
                    if value is not None:
                        print(f"   - {key}: {value}")

                # 배달 날짜까지 확정되면 주문 완료로 간주하고 종료
                if "delivery_date" in order_data and order_data["delivery_date"]:
                    print("\n" + "="*60)
                    print("[주문 완료] 주문이 성공적으로 접수되었습니다!")
                    print("="*60)
                    break

            print("\n" + "-"*60)
            turn += 1

        except KeyboardInterrupt:
            print("\n\n[종료] 사용자가 종료했습니다.")
            break

        except Exception as e:
            print(f"\n[X] 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            print("\n계속 진행하려면 Enter를 누르세요...")
            input()

    # 최종 주문 요약
    print("\n" + "="*60)
    print("[최종 주문 요약]")
    print("="*60)
    summary = dialog_manager.get_order_summary()
    print(f"\n{summary}\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[X] 프로그램 오류: {e}")
        import traceback
        traceback.print_exc()
