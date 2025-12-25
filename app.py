import streamlit as st
import requests
from urllib.parse import urlencode, quote_plus
import uuid

# Configuration (replace with real values in production)
AUTH_ENDPOINT = "https://auth.example.com/authorize"
TOKEN_ENDPOINT = "https://auth.example.com/token"
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
REDIRECT_URI = "https://your-app.com/"
SCOPE = ["openid", "profile", "email"]


def build_auth_url(client_id: str, redirect_uri: str, scope: list, state: str) -> str:
    """Construct the OAuth2 authorization URL.

    This function ensures values are URL-encoded and uses a correct f-string.
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scope),
        "state": state,
    }
    # Use urlencode to properly encode parameters
    return f"{AUTH_ENDPOINT}?{urlencode(params, quote_via=quote_plus)}"


def exchange_code_for_token(code: str) -> dict:
    """Exchange authorization code for an access token."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    resp = requests.post(TOKEN_ENDPOINT, data=data)
    resp.raise_for_status()
    return resp.json()


def main():
    st.title("PICU Helper App")

    # State management using streamlit's query_params API
    params = st.query_params

    if "state" not in params:
        # Initialize a random state and set it in the URL query params
        state = str(uuid.uuid4())
        st.set_query_params(state=state)
        params = st.query_params
    else:
        state = params.get("state")
        # streamlit returns lists for query param values
        if isinstance(state, list):
            state = state[0]

    # Check for authorization code in the URL
    code = params.get("code")
    if isinstance(code, list):
        code = code[0]

    if code:
        st.write("Authorization code detected — exchanging for token...")
        try:
            token_response = exchange_code_for_token(code)
            st.success("Successfully retrieved token")
            st.write(token_response)
        except Exception as e:
            st.error(f"Token exchange failed: {e}")
    else:
        st.write("Not authorized yet. Click the button below to start the OAuth flow.")
        if st.button("Sign in"):
            auth_url = build_auth_url(CLIENT_ID, REDIRECT_URI, SCOPE, state)
            st.markdown(f"[Continue to auth provider]({auth_url})")


if __name__ == "__main__":
    main()
