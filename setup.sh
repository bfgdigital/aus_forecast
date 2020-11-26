mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
level = "debug"\n\
port = $PORT\n\
caching = false\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml