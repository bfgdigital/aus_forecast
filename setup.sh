mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableWebsocketCompression = false
" > ~/.streamlit/config.toml