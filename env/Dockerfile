FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3.10 python3-pip
# pip
RUN pip3 install fastapi  \
    uvicorn[standard]  \
    jinja2  \
    aiofiles  \
    numpy  \
    pandas  \
    requests  \
    python-multipart  \
    openpyxl  \
    python-docx  \
    pymysql  \
    tortoise-orm[aiomysql]  \
    aiomysql  \
    apscheduler  \
    cryptography  \
    redis  \
    py2neo \
    streamlit \
    qdrant-client \
    openai \
    pyyaml \
    aiohttp \
    aioredis \
    -U --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip3 install paramiko \
    -U --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple