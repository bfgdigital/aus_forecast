mkdir -p ~/.streamlit/
echo "\
[server]\n\ 
headless = true\n\
port = $PORT\n\
[client]\n\
caching = false\n\
[logger]\n\
level = "debug"\n\
" > ~/.streamlit/config.toml