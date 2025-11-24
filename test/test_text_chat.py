"""
텍스트 입력 + 베이스 모델 대화 테스트 스크립트
(음성 인식 없이 텍스트로만 디너 봇과 대화)
"""
import os
import sys
from dotenv import load_dotenv

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 프로젝트 루트 경로 (test 폴더의 상위 디렉토리)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 환경 변수 로드 (프로젝트 루트의 .env 파일)
load_dotenv(os.path.join(project_root, '.env'))

# 모듈 경로 추가
sys.path.insert(0, project_root)

from ai_module.conversation.dialog_manager import DialogManager


def main():
    """메인 함수"""

    # 대화 관리자 초기화 (베이스 모델 로드)
    try:
        print("\n베이스 모델 로드 중... ")
        dialog_manager = DialogManager()
    except Exception as e:
        print(f"초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return

    print("="*60)

    # 대화 시작
    customer_name = input("고객 이름을 입력하세요: ").strip()
    if not customer_name:
        customer_name = "테스트 고객"

    print("\n" + "="*60)
    greeting = dialog_manager.start_conversation(customer_name)
    print(f"\n시스템: {greeting}\n")
    

    # 대화 루프
    turn = 1
    while True:
        try:
            print(f"\n[ 턴 {turn} ]")

            # 텍스트 입력
            user_input = input("[사용자] 입력: ").strip()

            if not user_input:
                print("[X] 입력이 비어있습니다.")
                continue

            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\n[종료] 대화를 종료합니다.")
                break

            # 베이스 모델 응답 생성
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
