import whisper

model = whisper.load_model("tiny")

# voiceFile 파라미터에 음성 파일을 넣으면 텍스트로 전환

def voiceRecognize(voiceFile):
    result = model.transcribe(voiceFile, language = "ko")
    return result["text"]
