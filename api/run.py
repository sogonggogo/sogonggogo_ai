"""
서버 실행 스크립트
"""
import sys
import os

# 프로젝트 루트 경로 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import uvicorn

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  Starting FastAPI Server...")
    print("="*60)
    print("  URL: http://localhost:8000")
    print("  Docs: http://localhost:8000/docs")
    print("="*60 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
