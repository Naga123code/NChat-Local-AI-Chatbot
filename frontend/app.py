
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="NChat Local AI",
    page_icon="🤖",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

if "token" not in st.session_state:
    st.session_state.token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_error_message(response, default_message="Something went wrong"):
    """
    Safely extract an error message from FastAPI response.
    Prevents JSONDecodeError when the response is not JSON.
    """

    try:
        data = response.json()

        if isinstance(data, dict):
            return data.get("detail", default_message)

        return str(data)

    except ValueError:
        # Response is not valid JSON
        if response.text:
            return response.text

        return f"{default_message} (HTTP {response.status_code})"


# ============================================================
# LOGIN / REGISTER PAGE
# ============================================================

if st.session_state.token is None:

    st.title("🤖 NChat")

    st.caption(
        "Local AI Chatbot using FastAPI + Ollama"
    )

    option = st.radio(
        "Select",
        ["Login", "Register"],
        horizontal=True
    )

    username = st.text_input(
        "Username",
        placeholder="Enter username"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter password"
    )

    # ========================================================
    # REGISTER
    # ========================================================

    if option == "Register":

        if st.button(
            "Create Account",
            use_container_width=True
        ):

            if not username or not password:

                st.warning(
                    "Enter username and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/auth/register",
                        json={
                            "username": username,
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code in [200, 201]:

                        st.success(
                            "Registration successful. "
                            "Please login."
                        )

                    else:

                        error = get_error_message(
                            response,
                            "Registration failed"
                        )

                        st.error(error)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI. "
                        "Make sure FastAPI is running on "
                        "http://127.0.0.1:8000"
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Registration request timed out."
                    )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Request error: {str(e)}"
                    )

    # ========================================================
    # LOGIN
    # ========================================================

    else:

        if st.button(
            "Login",
            use_container_width=True
        ):

            if not username or not password:

                st.warning(
                    "Enter username and password."
                )

            else:

                try:

                    response = requests.post(
                        f"{API_URL}/auth/login",
                        data={
                            "username": username,
                            "password": password
                        },
                        timeout=30
                    )

                    if response.status_code == 200:

                        try:

                            data = response.json()

                        except ValueError:

                            st.error(
                                "FastAPI returned an invalid "
                                "login response."
                            )

                            st.code(response.text)

                            st.stop()

                        access_token = data.get(
                            "access_token"
                        )

                        if not access_token:

                            st.error(
                                "Login response does not contain "
                                "access_token."
                            )

                            st.code(response.text)

                        else:

                            st.session_state.token = access_token

                            st.session_state.username = username

                            st.session_state.messages = []

                            st.rerun()

                    else:

                        error = get_error_message(
                            response,
                            "Login failed"
                        )

                        st.error(error)

                except requests.exceptions.ConnectionError:

                    st.error(
                        "Cannot connect to FastAPI. "
                        "Make sure FastAPI is running."
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "Login request timed out."
                    )

                except requests.exceptions.RequestException as e:

                    st.error(
                        f"Request error: {str(e)}"
                    )

    st.stop()


# ============================================================
# AUTHORIZATION HEADER
# ============================================================

headers = {
    "Authorization": f"Bearer {st.session_state.token}"
}


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚙️ Settings")

    st.write(
        f"User: **{st.session_state.username}**"
    )

    st.divider()

    # ========================================================
    # CLEAR CHAT
    # ========================================================

    if st.button(
        "🗑️ Clear Chat",
        use_container_width=True
    ):

        try:

            response = requests.delete(
                f"{API_URL}/chat/history",
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:

                st.session_state.messages = []

                st.success(
                    "Chat history cleared."
                )

                st.rerun()

            elif response.status_code == 401:

                st.session_state.token = None
                st.session_state.username = None
                st.session_state.messages = []

                st.warning(
                    "Session expired. Please login again."
                )

                st.rerun()

            else:

                error = get_error_message(
                    response,
                    "Unable to clear chat."
                )

                st.error(error)

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to FastAPI."
            )

        except requests.exceptions.Timeout:

            st.error(
                "Clear chat request timed out."
            )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Request error: {str(e)}"
            )

    # ========================================================
    # LOGOUT
    # ========================================================

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.token = None

        st.session_state.username = None

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🤖 NChat")

st.caption(
    "Streamlit + FastAPI + SQLModel + Ollama"
)


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

if not st.session_state.messages:

    try:

        response = requests.get(
            f"{API_URL}/chat/history",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:

            try:

                history = response.json()

                if isinstance(history, list):

                    for item in history:

                        if (
                            isinstance(item, dict)
                            and "role" in item
                            and "content" in item
                        ):

                            st.session_state.messages.append(
                                {
                                    "role": item["role"],
                                    "content": item["content"]
                                }
                            )

            except ValueError:

                st.warning(
                    "FastAPI returned invalid chat history."
                )

        elif response.status_code == 401:

            st.session_state.token = None

            st.session_state.username = None

            st.session_state.messages = []

            st.warning(
                "Session expired. Please login again."
            )

            st.rerun()

        else:

            error = get_error_message(
                response,
                "Unable to load chat history."
            )

            st.warning(error)

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to FastAPI. "
            "Make sure the backend is running."
        )

    except requests.exceptions.Timeout:

        st.warning(
            "Loading chat history timed out."
        )

    except requests.exceptions.RequestException as e:

        st.error(
            f"Request error: {str(e)}"
        )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

prompt = st.chat_input(
    "Ask anything..."
)


if prompt:

    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # ========================================================
    # SEND MESSAGE TO FASTAPI
    # ========================================================

    try:

        response = requests.post(
            f"{API_URL}/chat/",
            headers=headers,
            json={
                "message": prompt
            },
            timeout=120
        )

        # ====================================================
        # SUCCESS
        # ====================================================

        if response.status_code == 200:

            try:

                data = response.json()

            except ValueError:

                st.error(
                    "FastAPI returned an invalid JSON response."
                )

                st.code(
                    response.text,
                    language="text"
                )

                st.stop()

            answer = data.get(
                "response"
            )

            if answer is None:

                st.error(
                    "FastAPI response does not contain "
                    "'response'."
                )

                st.json(data)

            else:

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                with st.chat_message("assistant"):

                    st.markdown(answer)

        # ====================================================
        # AUTHENTICATION ERROR
        # ====================================================

        elif response.status_code == 401:

            st.session_state.token = None

            st.session_state.username = None

            st.session_state.messages = []

            st.warning(
                "Your session has expired. "
                "Please login again."
            )

            st.rerun()

        # ====================================================
        # VALIDATION ERROR
        # ====================================================

        elif response.status_code == 422:

            st.error(
                "FastAPI validation error (422)."
            )

            st.write(
                "Request sent:"
            )

            st.json(
                {
                    "message": prompt
                }
            )

            st.write(
                "FastAPI response:"
            )

            st.code(
                response.text,
                language="json"
            )

        # ====================================================
        # OTHER FASTAPI ERROR
        # ====================================================

        else:

            st.error(
                f"FastAPI returned HTTP "
                f"{response.status_code}"
            )

            st.code(
                response.text,
                language="text"
            )

    # ========================================================
    # CONNECTION ERROR
    # ========================================================

    except requests.exceptions.ConnectionError:

        st.error(
            " Cannot connect to FastAPI.\n\n"
            "Make sure FastAPI is running:\n"
            "uvicorn backend.main:app --reload"
        )

    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout:

        st.error(
            "⏱️ Ollama response timed out. "
            "Make sure Ollama is running and the model "
            "is available."
        )

    # ========================================================
    # OTHER REQUEST ERROR
    # ========================================================

    except requests.exceptions.RequestException as e:

        st.error(
            f" Request error: {str(e)}"
        )

    # ========================================================
    # UNEXPECTED ERROR
    # ========================================================

    except Exception as e:

        st.error(
            f" Unexpected error: {str(e)}"
        )

