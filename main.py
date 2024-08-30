import os
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
from gemini_utility import (load_gemini_pro_model,
                            gemini_pro_response,
                            gemini_pro_vision_response,
                            embeddings_model_response)

working_dir = os.path.dirname(os.path.abspath(__file__))
st.set_page_config(
    page_title="MEDBOT",
    page_icon="🧠",
    layout="centered",
)

with st.sidebar:
    selected = option_menu('MEDBOT',
                           ['ChatBot',
                            'Image Captioning',
                            'Speak to ChatBot',
                            'Ask me anything'],
                           menu_icon='robot', icons=['chat-dots-fill', 'image-fill', 'mic-fill', 'patch-question-fill'],
                           default_index=0
                           )

# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# chatbot page
if selected == 'ChatBot':
    model = load_gemini_pro_model()

    # Initialize chat session in Streamlit if not already present
    if "chat_session" not in st.session_state:  # Renamed for clarity
        st.session_state.chat_session = model.start_chat(history=[])

    # Display the chatbot's title on the page
    st.title("🤖 ChatBot")

    # Display the chat history
    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    # Input field for user's message
    user_prompt = st.chat_input("Ask Gemini-Pro...")  # Renamed for clarity
    if user_prompt:
        # Add user's message to chat and display it
        st.chat_message("user").markdown(user_prompt)

        # Send user's message to Gemini-Pro and get the response
        gemini_response = st.session_state.chat_session.send_message(user_prompt)  # Renamed for clarity

        # Display Gemini-Pro's response
        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)


# Image captioning page
if selected == "Image Captioning":

    st.title("📷 Snap Narrate")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if st.button("Generate Caption"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 500))
            st.image(resized_img)

        default_prompt = "write a short caption for this image"  # change this prompt as per your requirement

        # get the caption of the image from the gemini-pro-vision LLM
        caption = gemini_pro_vision_response(default_prompt, image)

        with col2:
            st.info(caption)


# text embedding model
if selected == "Ask me anything":

    st.title("❓ Ask me a question")

    # text box to enter prompt
    user_prompt = st.text_area(label='', placeholder="Ask me anything...")

    if st.button("Get Response"):
        response = gemini_pro_response(user_prompt)
        st.markdown(response)
def recognize_speech_from_mic():
    recognizer = Recognizer()
    mic = Microphone()

    with mic as source:
        st.info("Say something!")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except UnknownValueError:
        st.error("Could not understand the audio")
        return None
    except RequestError as e:
        st.error(f"Could not request results; {e}")
        return None

# Handle different selected options here...

if selected == "Speak to ChatBot":
    st.title("🎙 Speak to ChatBot")

    if st.button("Speak"):
        spoken_text = recognize_speech_from_mic()
        if spoken_text:
            model = load_gemini_pro_model()
            if "chat_session" not in st.session_state:
                st.session_state.chat_session = model.start_chat(history=[])

            st.chat_message("user").markdown(spoken_text)
            gemini_response = st.session_state.chat_session.send_message(spoken_text)
            with st.chat_message("assistant"):
                st.markdown(gemini_response.text)

# Include other selected options as needed...