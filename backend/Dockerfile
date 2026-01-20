FROM python:3.9-slim

# 安装 face_recognition 所需的系统编译库
RUN apt-get update && apt-get install -y \
    build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# 启动时先生成一次内容，然后启动 API 服务
CMD python content_gen.py && uvicorn main:app --host 0.0.0.0 --port 8098