import google.generativeai as genai
import edge_tts
import asyncio
import json
import os
import datetime

API_KEY = os.getenv("GEMINI_API_KEY")
MODULE = os.getenv("MODULE")
DATA_DIR = "/app/data"

async def generate_daily_content():
    print("开始生成今日内容...")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODULE)
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    prompt = f"""
    Generate a JSON object for daily English learning. The date should be "{today_str}".
    Target audience: High school student.
    Content: An inspiring quote, its author, a simplified explanation, and key vocabulary.
    Format:
    {{
      "daily_quote_data": {{
        "date": "{today_str}",
        "topic": "Topic here",
        "content": {{
          "quote": "Quote text",
          "author": "Author Name",
          "simplified_version": "Simple explanation"
        }},
        "vocabulary": [
           {{"word": "word1", "definition": "def1"}},
           {{"word": "word2", "definition": "def2"}}
        ]
      }}
    }}
    Ensure the response is valid JSON.
    """
    
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
        text_to_speak = content.get('quote', content.get('english_sentence', ''))
        if not text_to_speak:
            print("Warning: No 'quote' or 'english_sentence' found in JSON.")
            text_to_speak = "Content generation error. Please check logs."
        communicate = edge_tts.Communicate(text_to_speak, "en-US-ChristopherNeural")
        await communicate.save(f"{DATA_DIR}/daily_audio.mp3")
        
        print("内容生成完毕！")
        
    except Exception as e:
        print(f"生成失败: {e}")

if __name__ == "__main__":
    asyncio.run(generate_daily_content())