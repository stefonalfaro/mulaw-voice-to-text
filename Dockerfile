FROM stefonalfaro/ai-base

WORKDIR /app

COPY . .

RUN pip install Flask

RUN pip install gunicorn

RUN pip install gevent

EXPOSE 5000

ENTRYPOINT gunicorn -w ${WORKERS:-4} -k gevent -b 0.0.0.0:5000 voiceToTextServer:app