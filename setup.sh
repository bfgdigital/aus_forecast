mkdir -p ~/.streamlit/
echo "
[client]
caching = false
[logger]
level = "debug"
[server]
headless = true
port = $PORT
" > ~/.streamlit/config.toml