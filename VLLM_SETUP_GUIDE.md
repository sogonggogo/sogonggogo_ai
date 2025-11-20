# vLLM 로컬 서버 설정 가이드

## 개요
이 가이드는 RTX 4060 8GB VRAM에서 vLLM을 사용하여 완전 무료 로컬 LLM 서버를 구축하는 방법을 설명합니다.

**중요:** OpenAI API를 사용하지만, 실제로는 로컬에서만 실행되며 외부 API 호출 및 비용이 전혀 발생하지 않습니다.

---

## 1단계: 필수 패키지 설치

### Python 환경 확인
- Python 3.8 이상 필요
- CUDA 11.8 이상 권장 (GPU 사용 시)

### 패키지 설치
```bash
pip install -r requirements.txt
```

또는 개별 설치:
```bash
pip install vllm==0.6.3.post1
pip install openai==1.54.3
```

---

## 2단계: 한국어 모델 선택 (RTX 4060 8GB 최적화)

### 추천 모델

| 모델 | 크기 | VRAM (4bit) | 한국어 | 속도 | 추천도 |
|------|------|-------------|--------|------|--------|
| **beomi/Llama-3-Open-Ko-8B** | 8B | ~6GB | ⭐⭐⭐ | 빠름 | ✅✅ 최고 |
| yanolja/EEVE-Korean-10.8B | 10.8B | ~7GB | ⭐⭐⭐ | 보통 | ✅ 좋음 |
| Qwen/Qwen2.5-7B-Instruct | 7B | ~5GB | ⭐⭐ | 빠름 | ✅ 좋음 |

---

## 3단계: vLLM 서버 실행

### 방법 1: 기본 실행 (권장)

```bash
vllm serve beomi/Llama-3-Open-Ko-8B \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 2048 \
  --gpu-memory-utilization 0.9
```

**파라미터 설명:**
- `--host 0.0.0.0`: 모든 네트워크 인터페이스에서 접속 가능
- `--port 8000`: API 서버 포트
- `--dtype half`: FP16 사용 (메모리 절약)
- `--max-model-len 2048`: 최대 시퀀스 길이 (메모리에 맞게 조정)
- `--gpu-memory-utilization 0.9`: GPU 메모리 사용률 (90%)

### 방법 2: CPU 전용 (GPU 없을 때)

```bash
vllm serve beomi/Llama-3-Open-Ko-8B \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 2048 \
  --device cpu
```

⚠️ **경고:** CPU 모드는 매우 느립니다 (응답에 10-30초 소요 가능)

### 방법 3: 4bit 양자화 (메모리 더 절약)

AWQ 양자화 모델 사용:
```bash
vllm serve TheBloke/Llama-2-7B-Chat-AWQ \
  --host 0.0.0.0 \
  --port 8000 \
  --quantization awq \
  --dtype half \
  --max-model-len 2048
```

---

## 4단계: 서버 확인

### API 서버가 정상 작동하는지 확인

```bash
curl http://localhost:8000/v1/models
```

정상이면 다음과 같이 출력됩니다:
```json
{
  "object": "list",
  "data": [
    {
      "id": "beomi/Llama-3-Open-Ko-8B",
      "object": "model",
      "created": 1234567890,
      "owned_by": "vllm"
    }
  ]
}
```

### 간단한 채팅 테스트

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "beomi/Llama-3-Open-Ko-8B",
    "messages": [
      {"role": "user", "content": "안녕하세요"}
    ]
  }'
```

---

## 5단계: FastAPI 서버와 연결

### 환경 변수 설정 (선택사항)

`.env` 파일 생성:
```bash
VLLM_BASE_URL=http://localhost:8000/v1
```

### FastAPI 서버 실행

```bash
uvicorn main:app --reload
```

이제 FastAPI 서버가 vLLM 로컬 서버와 통신합니다!

---

## 트러블슈팅

### 문제 1: CUDA Out of Memory

**해결 방법:**
1. `--max-model-len` 줄이기 (2048 → 1024)
2. `--gpu-memory-utilization` 낮추기 (0.9 → 0.7)
3. 더 작은 모델 사용 (3B 모델)

```bash
vllm serve beomi/Llama-3-Open-Ko-8B \
  --max-model-len 1024 \
  --gpu-memory-utilization 0.7
```

### 문제 2: 모델 다운로드 실패

**해결 방법:**
Hugging Face에서 수동 다운로드:
```bash
huggingface-cli download beomi/Llama-3-Open-Ko-8B
```

### 문제 3: 응답이 너무 느림

**해결 방법:**
1. GPU 사용 확인 (`nvidia-smi`로 확인)
2. 더 작은 모델 사용
3. `--max-model-len` 줄이기

---

## 성능 최적화 팁

### RTX 4060 8GB 최적 설정

```bash
vllm serve beomi/Llama-3-Open-Ko-8B \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 1536 \
  --gpu-memory-utilization 0.85 \
  --max-num-seqs 4 \
  --enable-prefix-caching
```

**파라미터 설명:**
- `--max-num-seqs 4`: 동시 처리 요청 수 (메모리에 맞게 조정)
- `--enable-prefix-caching`: 시스템 프롬프트 캐싱으로 속도 향상

---

## 비용 및 외부 연결 확인

### ✅ 완전 무료 확인 사항

1. **외부 API 호출 없음**
   - `base_url="http://localhost:8000"` → 로컬 주소
   - 인터넷 연결 없이도 작동

2. **OpenAI API 키 불필요**
   - 코드에서 `api_key="not-needed"` 사용
   - 실제 OpenAI 서비스와 무관

3. **데이터 외부 전송 없음**
   - 모든 데이터가 본인 컴퓨터에만 존재
   - 프라이버시 100% 보장

---

## 백그라운드 실행 (서버 자동 시작)

### Linux/Mac

```bash
nohup vllm serve beomi/Llama-3-Open-Ko-8B \
  --host 0.0.0.0 \
  --port 8000 \
  --dtype half \
  --max-model-len 2048 > vllm.log 2>&1 &
```

### Windows (PowerShell)

```powershell
Start-Process -NoNewWindow -FilePath "vllm" -ArgumentList "serve", "beomi/Llama-3-Open-Ko-8B", "--host", "0.0.0.0", "--port", "8000"
```

---

## 요약

1. ✅ **완전 무료**: OpenAI/Groq 등 유료 API 사용 안 함
2. ✅ **로컬 실행**: 모든 추론이 본인 컴퓨터에서만 실행
3. ✅ **RTX 4060 최적화**: 8GB VRAM에서 7B-10B 모델 실행 가능
4. ✅ **교수님 요구사항 충족**: 상용 LLM 미사용, 외부 API 미사용

---

## 다음 단계

1. vLLM 서버 실행 테스트
2. FastAPI 서버 연동 확인
3. 음성 주문 시스템 전체 테스트
4. (선택) 파인튜닝으로 성능 개선
