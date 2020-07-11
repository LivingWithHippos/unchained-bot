FROM python:3.7
COPY . /app
WORKDIR /app
RUN pip  install .
CMD [ "python", "./unchained-bot.py" ]