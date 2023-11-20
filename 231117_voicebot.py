import streamlit as st
from audiorecorder import audiorecorder
import numpy as np
from openai import OpenAI
import os
from datetime import datetime

# 기능 구현 함수
def STT(audio, client):
    # 파일 저장
    filename = "input.mp3"
    # wav_file = open(filename, "wb")
    # wav_file.write(audio.tobytes())
    # wav_file.close()
    audio.export(filename, format="mp3")

    # 음원 파일 열기
    audio_file = open(filename, "rb")
    # whisper 사용하여 텍스트 얻기
    transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    audio_file.close()

    # 파일 삭제
    os.remove(filename)

    return transcript.text

def ask_gpt(prompt, model, client):
    completion = client.chat.completions.create(model=model, messages=prompt)
    system_message = completion.choices[0].message.content
    return system_message

def main():
    system_setting_content = "당신은 훌륭한 비서입니다. 질문자는 5살입니다. 모든 질문에 대한 답변은 25단어정도의 한국어로 해주세요. 오타가 있어서 내용이 어색하다면 문맥상 추측을 해서 답변해주세요."

    st.set_page_config(page_title="음성 비서 GPT", layout="wide")

    # st.title("title")
    st.header("음성 비서 프로그램")

    st.markdown("---")

    # 기본 설정
    with st.expander("음성 비서 GPT에 관하여", expanded=True):
        st.write(
            """
            - UI 스트림릿 이용
            - 답변 OpenAI GPT            
            """
        )
        st.markdown("")

    flag_start = False

    # session_state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": system_setting_content}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []

    # 사이트바
    with st.sidebar:
        api_key = st.text_input(label="OpenAI API Key", placeholder="Enter Your API Key", value="", type="password")

        client = OpenAI(api_key=api_key)

        st.markdown("---")

        model = st.radio(label="GPT Model", options=["gpt-3.5-turbo-1106", "gpt-4-1106-preview"])
        # gpt-4-1106-preview	$0.01 / 1K tokens	$0.03 / 1K tokens
        # gpt-3.5-turbo-1106    $0.0010 / 1K tokens	$0.0020 / 1K tokens
        st.markdown("---")

        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": system_setting_content}]
            print()
            print("초기화 되었습니다.")
            print(f'st.session_state["chat"]: {st.session_state["chat"]}')
            print(f'st.session_state["messages"]: {st.session_state["messages"]}')
            print()

    # 질문 답변 기능 구현 공간
    col1, col2 = st.columns(2)
    with col1:
        st.header("질문하기")
        # 음성 녹음 아이콘 추가
        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
        if len(audio) > 0 and not np.array_equal(audio, st.session_state["check_audio"]):
            # 음성 재생
            # st.audio(audio.tobytes())
            st.audio(audio.export().read())
            # 음원에서 텍스트 파일 추출
            question = STT(audio, client)

            print(f"question: {question}")

            # 시각화를 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("user", now, question)]
            st.session_state["messages"] = st.session_state["messages"] + [{"role": "user", "content": question}]
            # 오디오 정보 저장
            st.session_state["check_audio"] = audio
            flag_start = True 

            
    with col2:
        st.header("질문/답변")
        if flag_start:
            print(f'st.session_state["messages"]: {st.session_state["messages"]}')
            # GTP에게 답변 받기
            response = ask_gpt(st.session_state["messages"], model, client)

            print(f"response: {response}")

            st.session_state["messages"] = st.session_state["messages"] + [{"role": "system", "content": response}]
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"] + [("bot", now, response)]


            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    with st.chat_message("User", avatar="🧑"):
                        st.write(f"{time}\n{message}")
                else:
                    with st.chat_message("GPT", avatar="💻"):
                        st.write(f"{time}\n{message}")


    print(st.session_state)

if __name__ == "__main__":
    main()
