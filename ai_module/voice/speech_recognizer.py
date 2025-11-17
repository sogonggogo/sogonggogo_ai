"""
음성인식 모듈 (Faster-Whisper - 오픈소스)
마이크 입력을 받아 텍스트로 변환
"""
import os
import io
import wave
import tempfile
import pyaudio
from typing import Optional
from faster_whisper import WhisperModel


class SpeechRecognizer:
    """
    음성 인식 클래스 (Faster-Whisper - 오픈소스)
    """

    def __init__(self, model_size: str = "base"):
        """
        초기화
        Args:
            model_size: Whisper 모델 크기 (tiny, base, small, medium, large)
                       - tiny: 가장 빠름, 정확도 낮음
                       - base: 빠름, 정확도 괜찮음 (추천)
                       - small: 중간 속도, 정확도 좋음
                       - medium/large: 느림, 정확도 높음
        """
        print(f"🔄 Whisper 모델 로딩 중 ({model_size})...")

        # CPU 또는 GPU 자동 선택
        device = "cpu"  # GPU 있으면 "cuda"로 변경 가능
        compute_type = "int8"  # CPU에서는 int8, GPU에서는 float16

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print(f"✅ Whisper 모델 로딩 완료!")

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

        # Whisper로 인식
        try:
            # 임시 WAV 파일 생성
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name

                # WAV 파일로 저장
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.RATE)
                    wf.writeframes(audio_data)

            # Whisper로 인식
            segments, info = self.model.transcribe(
                temp_path,
                language="ko",
                beam_size=5,
                vad_filter=True  # 음성 구간만 인식
            )

            # 결과 추출
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            # 임시 파일 삭제
            os.unlink(temp_path)

            if text_parts:
                text = " ".join(text_parts)
                print(f"✅ [인식 완료] {text}")
                return text
            else:
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
            audio_file_path: 오디오 파일 경로 (.wav, .mp3 등)
        Returns:
            인식된 텍스트 또는 None
        """
        try:
            # Whisper로 인식
            segments, info = self.model.transcribe(
                audio_file_path,
                language="ko",
                beam_size=5,
                vad_filter=True
            )

            # 결과 추출
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            if text_parts:
                text = " ".join(text_parts)
                print(f"✅ [파일 인식 완료] {text}")
                return text
            else:
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
