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
import logging
import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 依赖项：获取 DB 会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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

# --- 人脸识别初始化 & 同步 ---
known_encodings = []
known_names = []

def sync_faces_to_db():
    """
    1. 从 DB 加载人脸数据到内存 (known_encodings, known_names)
    2. 扫描 /app/data/known_faces，如果有新文件但 DB 没有，则处理并存入 DB
    """
    global known_encodings, known_names
    db = SessionLocal()
    
    # 1. Load from DB
    face_records = db.query(models.FaceEncoding).all()
    known_encodings = [rec.encoding for rec in face_records]
    known_names = [rec.user.name for rec in face_records]
    logger.info(f"Loaded {len(known_names)} faces from database: {known_names}")

    # 2. Sync from File System
    face_dir = "/app/data/known_faces"
    if not os.path.exists(face_dir):
        logger.warning(f"Face directory {face_dir} not found.")
        db.close()
        return

    new_faces_count = 0
    for file in os.listdir(face_dir):
        if file.endswith(('.jpg', '.png')):
            name = os.path.splitext(file)[0]
            
            # Check if user/face already exists in memory (simple check)
            if name in known_names:
                continue

            logger.info(f"New face file found: {file}. Processing...")
            try:
                img = face_recognition.load_image_file(os.path.join(face_dir, file))
                encs = face_recognition.face_encodings(img)
                if encs:
                    encoding = encs[0]
                    
                    # Create User if not exists
                    user = db.query(models.User).filter(models.User.name == name).first()
                    if not user:
                        user = models.User(name=name)
                        db.add(user)
                        db.commit()
                        db.refresh(user)
                    
                    # Create FaceEncoding
                    face_entry = models.FaceEncoding(user_id=user.id, encoding=encoding)
                    db.add(face_entry)
                    db.commit()
                    
                    # Update memory
                    known_encodings.append(encoding)
                    known_names.append(name)
                    new_faces_count += 1
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")

    if new_faces_count > 0:
        logger.info(f"Imported {new_faces_count} new faces to database.")
    
    db.close()

sync_faces_to_db()

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
            
    
    # Log to DB
    db = SessionLocal()
    try:
        log_entry = models.RecognitionLog(
            user_name_snapshot=user_id,
            timestamp=datetime.datetime.now(),
            image_path=None # We are not saving recognized images permanently yet
        )
        
        if user_id != "guest":
            logger.info(f"Recognized user: {user_id} for {file.filename}")
            # Identify User object
            user_obj = db.query(models.User).filter(models.User.name == user_id).first()
            if user_obj:
                log_entry.user_id = user_obj.id
        else:
            logger.warning(f"Recognition failed for {file.filename}")

        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log recognition to DB: {e}")
    finally:
        db.close()

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