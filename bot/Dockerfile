FROM python:3.9-slim
WORKDIR /app
COPY . .

RUN apt update
RUN apt install -y openssh-server

RUN echo "PermitRootLogin yes" > /etc/ssh/sshd_config
RUN echo "root:123" | chpasswd

RUN pip install -r requirements.txt

CMD service ssh start && python3 bot.py