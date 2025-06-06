docker run \
    -d \
    --restart always \
    --name local_server_pilot \
    -p 18501:18501 \
    -v ${PWD}:/app \
    -w /app \
    iss/baseenv:v1.10.1 \
    streamlit run webui.py --server.port 18501 --server.address 0.0.0.0