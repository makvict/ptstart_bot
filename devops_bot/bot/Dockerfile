FROM python:3.9-slim
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install --verbose -r requirements.txt
COPY . .

CMD ["python", "bot.py"]
