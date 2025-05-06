from keywords_recommend.keywords_recommend import suggest_next_keywords_with_history
from voice_recognition.voice_recognize import voiceRecognize


def main():
    context = input("상황을 입력하세요 (예: 음식점, 병원): ").strip()
    role = input("화자의 역할을 입력하세요 (예: 고객, 환자): ").strip()

    message_history = []

    while True:
        voice_path = "test.m4a"

        transcribed_text = voiceRecognize(voice_path)
        print(f"\n🗣️ 인식된 음성 내용: {transcribed_text}")
        message_history.append({"role": "user", "content": transcribed_text})

        print("\n👉 문장을 만들기 위해 단어를 선택해 주세요.\n")

        selected_words = []

        while True:
            reply = suggest_next_keywords_with_history(context, role, message_history, selected_words)
            print("📌 추천 단어들:\n", reply)

            suggested_words = [line.split(". ", 1)[1] for line in reply.strip().split("\n") if ". " in line]

            next_input = input("✅ 선택할 단어 번호 ('다시'=새 추천, '종료'=문장 끝): ").strip()

            if next_input.lower() == "종료":
                sentence = " ".join(selected_words)
                print("\n🗣️ 완성된 문장:", sentence)
                message_history.append({"role": "assistant", "content": sentence})
                break

            elif next_input.lower() == "다시":
                print("🔄 새로운 단어들을 추천받는 중입니다...\n")
                continue

            elif next_input.isdigit() and 1 <= int(next_input) <= len(suggested_words):
                selected_word = suggested_words[int(next_input) - 1]
                selected_words.append(selected_word)
                print("📝 현재 문장:", " ".join(selected_words))
            else:
                print("⚠️ 잘못된 입력입니다. 숫자나 '다시', '종료' 중 하나를 입력해주세요.")

if __name__ == "__main__":
    main()
