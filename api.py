from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

from voice_recognition.voice_recognize import voiceRecognize
from keywords_recommend.keywords_recommend import suggest_next_keywords_with_history

app = FastAPI()

# CORS 설정 (프론트 연동을 위한 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사용자 상태를 임시 저장 (실제로는 세션/DB로 처리 가능)
user_state = {
    "context": "",
    "role": "",
    "history": [],
    "selected_words": []
}

# 초기 상태 설정하는 코드
@app.post("/start")
async def start_conversation(context: str = Form(...), role: str = Form(...)):
    user_state["context"] = context
    user_state["role"] = role
    user_state["history"] = []
    user_state["selected_words"] = []
    return {"message": "상황과 역할 저장 완료"}

# 음성 파일을 받은 후 단어 추천해주는 코드
@app.post("/voice")
async def process_voice(file: UploadFile):
    temp_path = f"temp_audio.{file.filename.split('.')[-1]}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    transcribed = voiceRecognize(temp_path)
    os.remove(temp_path)

    user_state["history"].append({"role": "user", "content": transcribed})
    user_state["selected_words"] = []

    # 첫 추천
    reply = suggest_next_keywords_with_history(
        user_state["context"],
        user_state["role"],
        user_state["history"],
        user_state["selected_words"]
    )

    options = [line.split(". ", 1)[1] for line in reply.strip().split("\n") if ". " in line]
    return {"transcribed_text": transcribed, "options": options}

# 단어 선택후 다음 단어를 추천해주는 코드
@app.post("/select")
async def select_word(choice: str = Form(...)):
    user_state["selected_words"].append(choice)

    # 다음 단어 추천
    reply = suggest_next_keywords_with_history(
        user_state["context"],
        user_state["role"],
        user_state["history"],
        user_state["selected_words"]
    )

    options = [line.split(". ", 1)[1] for line in reply.strip().split("\n") if ". " in line]

    return {
        "current_sentence": " ".join(user_state["selected_words"]),
        "options": options
    }

# 문장 완성시 실행할 코드
@app.post("/end")
async def end_sentence():
    sentence = " ".join(user_state["selected_words"])
    user_state["history"].append({"role": "assistant", "content": sentence})
    user_state["selected_words"] = []
    return {"final_sentence": sentence}
