#Importing required packages
import streamlit as st
import anthropic
import uuid

INIT_PROMPT = """
\n\nHuman: You are MapMentor a trainer in Wardley Mapping. You will help the users learn about Wardley Mapping
"""

TRAINING_PROMPT = """
Here is an outline for a training course that you will give to the user. It covers the key principles of Wardley Mapping:
"""

INTRO_PROMPT = """
Hello, I'm DarijaBot 

"""

REG_PROMPT = """
\n\nHuman: Here is the user's question about Wardley Mapping:
<question>
{QUESTION}
</question>
\n\nAssistant: [MapMentor] <response>
"""

MODEL = "claude-3-5-sonnet-20240620"

new_prompt = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.set_page_config(page_title="Anthropic - ChatBot")
st.sidebar.title("Anthropic - ChatBot")
st.sidebar.title("Wardley Mapping Mentor")
st.sidebar.divider()
st.sidebar.markdown("Developed by Bahae Eddine HALIM](https://linkedin.com/in/halimbahae)", unsafe_allow_html=True)
st.sidebar.markdown("Current Version: 0.0.4")
st.sidebar.markdown("Using claude-2 API")
st.sidebar.markdown(st.session_state.session_id)
st.sidebar.divider()

# Check if the user has provided an API key, otherwise default to the secret
user_claude_api_key = st.sidebar.text_input("Enter your Anthropic API Key:", placeholder="sk-...", type="password")

if "claude_model" not in st.session_state:
    st.session_state["claude_model"] = MODEL

if "messages" not in st.session_state:
    st.session_state["messages"] = []
    st.session_state.messages.append({"role": "assistant", "content": INTRO_PROMPT})

if "all_prompts" not in st.session_state:
    st.session_state["all_prompts"] = INIT_PROMPT + TRAINING_PROMPT

if user_claude_api_key:
    # If the user has provided an API key, use it
    client=anthropic.Anthropic(
      # defaults to os.environ.get("ANTHROPIC_API_KEY")
      api_key=user_claude_api_key,
    )
else:
    st.warning("Please enter your Anthropic Claude API key", icon="⚠️")

for message in st.session_state.messages:
    if message["role"] in ["user", "assistant"]:
        with st.chat_message(message["role"]):
            new_prompt.append(message["content"])
            st.markdown(message["content"])

if user_claude_api_key:
    if user_input := st.chat_input("How can I help with Wardley Mapping?"):
        prompt = REG_PROMPT.format(QUESTION = user_input)
        st.session_state.all_prompts += prompt
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
        full_response = ""
        try:
            for response in client.completions.create(
                prompt=st.session_state.all_prompts,
                stop_sequences=["</response>"],
                model=MODEL,
                max_tokens_to_sample=500,
                stream=True,
            ):
                full_response += response.completion
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        except anthropic.APIConnectionError as e:
            st.error("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except anthropic.RateLimitError as e:
            st.error("A 429 status code was received; we should back off a bit.")
        except anthropic.APIStatusError as e:
            st.error("Another non-200-range status code was received\nTry again later.")
            st.error(e.status_code)
            st.error(e.response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.all_prompts += full_response
