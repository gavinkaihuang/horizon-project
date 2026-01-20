import google.generativeai as genai
import edge_tts
import asyncio
import json
import os
import datetime

API_KEY = os.getenv("GEMINI_API_KEY")
DATA_DIR = "/app/data"

async def generate_daily_content():
    print("开始生成今日内容...")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')
    
    # Prompt (此处省略详细 Prompt，参考之前的对话)
    prompt = "Generate a daily quote JSON for a high school student learning English..."
    
    import re
    try:
        response = model.generate_content(prompt)
        print(f"DEBUG: Raw response: {response.text}")
        
        # Robustly extract JSON block
        match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
        if match:
             json_str = match.group(1)
        else:
             # Fallback: try to find the first { and last }
             json_str = response.text[response.text.find('{'):response.text.rfind('}')+1]
             
        content = json.loads(json_str)
        
        # 1. 保存 JSON
        with open(f"{DATA_DIR}/daily.json", "w") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
            
        # 2. 生成 TTS 音频 (使用 edge-tts)
        text_to_speak = content['english_sentence']
        communicate = edge_tts.Communicate(text_to_speak, "en-US-ChristopherNeural")
        await communicate.save(f"{DATA_DIR}/daily_audio.mp3")
        
        print("内容生成完毕！")
        
    except Exception as e:
        print(f"生成失败: {e}")

if __name__ == "__main__":
    asyncio.run(generate_daily_content())