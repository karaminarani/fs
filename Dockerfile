FROM python:3.9-alpine

RUN apk add git -q

WORKDIR /FSub
COPY . ./

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN pip install -q \
pyrogram==2.0.106 \
pyromod==3.1.6 \
tgcrypto==1.2.5 \
uvloop==0.19.0 \
pymongo==4.6.3

CMD ["python", "-m", "Bot"]