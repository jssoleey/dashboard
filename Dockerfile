# 1. 공식 Python 이미지를 사용 (3.10 권장)
FROM python:3.10-slim

# 2. 작업 디렉토리 지정
WORKDIR /app

# 3. 의존성 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스코드 복사
COPY . .

# 5. Gunicorn으로 앱 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--workers=3"]