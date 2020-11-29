mkdir -p ~/.streamlit/
echo "[server]
headless = true
port = $PORT
enableCORS = false
enableWebsocketCompression = false
" > ~/.streamlit/config.toml