from fastapi import FastAPI, UploadFile, File
import face_recognition
import os
import shutil
import threading
import schedule
import time
import subprocess
import logging
import datetime

# --- 日志配置 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("/app/logs/backend.log") # Optional: log to file
    ]
)
logger = logging.getLogger(__name__)
app = FastAPI()

# --- 人脸识别初始化 ---
known_encodings = []
known_names = []

def load_faces():
    """加载 /app/data/known_faces 下的照片"""
    face_dir = "/app/data/known_faces"
    if not os.path.exists(face_dir): return
    
    for file in os.listdir(face_dir):
        if file.endswith(('.jpg', '.png')):
            img = face_recognition.load_image_file(os.path.join(face_dir, file))
            encs = face_recognition.face_encodings(img)
            if encs:
                known_encodings.append(encs[0])
                known_names.append(os.path.splitext(file)[0])
    logger.info(f"已加载人脸库: {known_names}")

load_faces()

# --- API 接口 ---

@app.post("/api/recognize")
async def recognize(file: UploadFile = File(...)):
    logger.info(f"Received recognition request: {file.filename}")
    # 保存上传的图片
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 识别
    unknown_image = face_recognition.load_image_file(temp_path)
    # 缩小图片以加速处理 (0.25倍)
    small_frame = unknown_image # 这里可以加 resize 逻辑
    
    locations = face_recognition.face_locations(small_frame)
    encodings = face_recognition.face_encodings(small_frame, locations)
    
    user_id = "guest"
    for encoding in encodings:
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        if True in matches:
            match_index = matches.index(True)
            user_id = known_names[match_index]
            break
            
    
    if user_id == "guest":
        logger.warning(f"Recognition failed for {file.filename}")
    else:
        logger.info(f"Recognized user: {user_id} for {file.filename}")

    return {"user": user_id}

# --- 定时任务线程 ---
def run_scheduler():
def run_content_gen_job():
    logger.info("Starting daily content generation job...")
    try:
        result = subprocess.run(
            ["python", "content_gen.py"], 
            capture_output=True, 
            text=True,
            check=False
        )
        if result.returncode == 0:
            logger.info(f"Content generation success:\n{result.stdout}")
        else:
            logger.error(f"Content generation failed (code {result.returncode}):\n{result.stderr}")
    except Exception as e:
        logger.error(f"Error running content generation job: {e}")

def run_scheduler():
    # 每天凌晨 4 点运行 content_gen.py
    schedule.every().day.at("04:00").do(run_content_gen_job)
    while True:
        schedule.run_pending()
        time.sleep(60)

# 启动定时任务
threading.Thread(target=run_scheduler, daemon=True).start()