FROM python:3

WORKDIR /app
COPY requirements.txt ./
RUN apt-get -y update
RUN apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

ENTRYPOINT ["bash", "run_server.sh"]
