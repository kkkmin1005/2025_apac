import openai

openai.api_key = ""

# 프롬프트 생성
def build_prompt(context: str, role: str, history: list[str], selected_words: list[str]) -> str:
    selected_text = " ".join(selected_words) if selected_words else "없음"
    return f"""
너는 AAC 사용자에게 단어를 한 개씩 추천해서 문장을 완성할 수 있도록 도와주는 언어 도우미야.
사용자는 '{role}'의 입장이고, 직접 자기 생각을 표현해야 해. 절대로 상대방(점원, 의사 등)의 입장에서 말하면 안 돼.

아래는 좋은 예시와 나쁜 예시야:

[올바른 추천 예시]
- 선택된 단어: "주문"
- 추천 단어: "하겠습니다", "원합니다", "주세요"

[잘못된 추천 예시]
- 선택된 단어: "주문"
- 추천 단어: "하시겠어요?", "도와드릴까요?", "원하시나요?" ← 상대방 입장이므로 절대 추천하지 마

---

❗ 반드시 사용자의 입장에서만 추천하고, 한 단어씩만 추천해줘야 해
❗ 상대방 입장의 표현은 절대 추천하지 마
❗ 문장이 2단어 이상이면 종결 표현도 추천해줘

- 현재 상황: {context}
- 화자(사용자)의 역할: {role}
- 지금까지의 대화 기록: "{history}"
- 지금까지 선택된 단어들: "{selected_text}"

다음에 올 수 있는 단어 4개를 추천해줘.
형식은 반드시 아래와 같아야 해:
1. ~
2. ~
3. ~
4. ~
"""



# GPT에게 요청하고 응답 받기
def suggest_next_keywords_with_history(context: str, role: str, history: list, selected_words: list[str]) -> str:
    prompt = build_prompt(context, role, history, selected_words)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 AAC 사용자에게 자연스럽고 상황에 맞는 단어를 추천하는 언어 도우미야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=150,
    )

    reply = response['choices'][0]['message']['content']
    history.append({"role": "assistant", "content": reply})
    return reply

# 대화 루프
def aac_conversation_loop():
    context = input("상황을 입력하세요 (예: 음식점, 병원): ").strip()
    role = input("화자의 역할을 입력하세요 (예: 고객, 환자): ").strip()
    transcribed_text = input("주변 음성 인식 내용을 입력하세요: ").strip()

    selected_words = []
    message_history = [{"role": "상대방", "content": transcribed_text}]

    print("\n👉 문장을 만들기 위해 단어를 선택해 주세요.\n")

    while True:
        reply = suggest_next_keywords_with_history(context, role, message_history, selected_words)
        print("📌 추천 단어들:\n", reply)

        # 단어 리스트로 파싱
        suggested_words = [line.split(". ", 1)[1] for line in reply.strip().split("\n") if ". " in line]

        while True:
            next_index = input("✅ 선택할 단어 번호 입력 ('다시'로 새 단어 추천, '종료' 입력 시 중단): ").strip()

            if next_index.lower() == "종료":
                print("\n🗣️ 최종 문장:", " ".join(selected_words))
                return

            elif next_index.lower() == "다시":
                print("🔄 새로운 단어들을 추천받는 중입니다...\n")
                break  # 다시 추천 받기 위해 바깥 루프로 빠져나감

            elif next_index.isdigit() and 1 <= int(next_index) <= len(suggested_words):
                selected_word = suggested_words[int(next_index) - 1]
                selected_words.append(selected_word)
                print("📝 현재 문장:", " ".join(selected_words))

                # 종결어미면 종료 유도
                if selected_word in ["하겠습니다", "원합니다", "주세요", "입니다", "해요"]:
                    print("✅ 문장이 마무리된 것 같아요. '종료'를 입력하면 끝낼 수 있어요.")
                break
            else:
                print("⚠️ 잘못된 입력입니다. 숫자나 '다시', '종료' 중 하나를 입력해주세요.")


        print("\n🗣️ 최종 문장:", " ".join(selected_words))
