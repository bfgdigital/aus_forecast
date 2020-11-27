mkdir -p ~/.streamlit/
echo "[global]
logLevel = debug
"
echo "[server]
headless = true
port = $PORT
enableCORS = false
enableWebsocketCompression = false
" > ~/.streamlit/config.toml