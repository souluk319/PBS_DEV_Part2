# PlayBook Studio + AI Ops

이 브랜치는 `PlayBook Studio`와 `OCP OPS`를 각 원형에 가깝게 한 서비스 진입 구조 아래 합친 첫 통합 버전입니다.

## 실행

```powershell
docker compose up -d --build
```

## 사용법

- `http://127.0.0.1:5173/` : 랜딩
- `http://127.0.0.1:5173/studio` : PlayBook Studio
- `http://127.0.0.1:5173/aiops` : OCP OPS

## 상태 확인

- `http://127.0.0.1:8765/api/health` : PBS backend
- `http://127.0.0.1:8000/healthz` : OPS backend
