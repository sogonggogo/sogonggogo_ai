"""
음성인식 모듈 (Google Cloud Speech-to-Text)
마이크 입력을 받아 텍스트로 변환
"""
import os
import io
import pyaudio
from typing import Optional
from google.cloud import speech


class SpeechRecognizer:
    """
    음성 인식 클래스 (Google Cloud Speech-to-Text)
    """

    def __init__(self, credentials_path: Optional[str] = None):
        """
        초기화
        Args:
            credentials_path: Google Cloud JSON 인증 파일 경로
        """
        # 환경변수에서 인증 파일 경로 가져오기
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        elif "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            # .env에서 설정 안했으면 경고
            print("⚠️  GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다.")
            print("   .env 파일에 다음을 추가하세요:")
            print("   GOOGLE_APPLICATION_CREDENTIALS=config/your-google-key.json")

        self.client = speech.SpeechClient()

        # 오디오 설정
        self.RATE = 16000
        self.CHUNK = int(self.RATE / 10)  # 100ms

    def recognize_from_microphone(self, duration: int = 5) -> Optional[str]:
        """
        마이크에서 음성 인식
        Args:
            duration: 녹음 시간 (초)
        Returns:
            인식된 텍스트 또는 None
        """
        print(f"\n🎤 [음성 입력 대기중...] {duration}초간 말씀하세요!")

        # 마이크에서 오디오 녹음
        audio_data = self._record_audio(duration)

        if not audio_data:
            return None

        print("🔄 [음성 인식 중...]")

        # Google Cloud STT로 인식
        try:
            audio = speech.RecognitionAudio(content=audio_data)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.RATE,
                language_code="ko-KR",
                enable_automatic_punctuation=True,
            )

            response = self.client.recognize(config=config, audio=audio)

            # 결과 추출
            for result in response.results:
                text = result.alternatives[0].transcript
                print(f"✅ [인식 완료] {text}")
                return text

            print("❌ 음성을 인식할 수 없습니다.")
            return None

        except Exception as e:
            print(f"❗ 인식 오류: {e}")
            return None

    def _record_audio(self, duration: int) -> Optional[bytes]:
        """
        마이크에서 오디오 녹음
        Args:
            duration: 녹음 시간 (초)
        Returns:
            오디오 바이트 데이터 또는 None
        """
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            print("🔴 녹음 중...")
            frames = []

            for i in range(0, int(self.RATE / self.CHUNK * duration)):
                data = stream.read(self.CHUNK)
                frames.append(data)

            print("⏹️  녹음 완료!")

            stream.stop_stream()
            stream.close()
            p.terminate()

            return b''.join(frames)

        except Exception as e:
            print(f"❗ 녹음 오류: {e}")
            return None

    def recognize_from_file(self, audio_file_path: str) -> Optional[str]:
        """
        오디오 파일에서 음성 인식
        Args:
            audio_file_path: 오디오 파일 경로 (.wav)
        Returns:
            인식된 텍스트 또는 None
        """
        try:
            with io.open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()

            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.RATE,
                language_code="ko-KR",
            )

            response = self.client.recognize(config=config, audio=audio)

            for result in response.results:
                text = result.alternatives[0].transcript
                print(f"✅ [파일 인식 완료] {text}")
                return text

            return None

        except Exception as e:
            print(f"❗ 파일 인식 오류: {e}")
            return None

    def test_microphone(self) -> bool:
        """
        마이크 테스트
        Returns:
            True: 마이크 정상, False: 마이크 오류
        """
        print("\n🔧 마이크 테스트 중...")

        try:
            p = pyaudio.PyAudio()

            # 마이크 장치 확인
            info = p.get_default_input_device_info()
            print(f"✅ 마이크가 감지되었습니다: {info['name']}")
            print(f"   최대 입력 채널: {info['maxInputChannels']}")
            print(f"   기본 샘플레이트: {int(info['defaultSampleRate'])} Hz")

            p.terminate()
            return True

        except Exception as e:
            print(f"❌ 마이크 오류: {e}")
            print("\n해결 방법:")
            print("1. 마이크가 연결되어 있는지 확인")
            print("2. Windows 설정 > 개인정보 > 마이크 > 앱 접근 허용")
            print("3. 다른 프로그램이 마이크를 사용 중인지 확인")
            return False
