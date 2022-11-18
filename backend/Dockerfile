FROM python:3.7-slim

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip

RUN pip install -r ./requirements.txt --no-cache-dir
COPY . /app

WORKDIR /app
CMD ["python3", "manage.py", "runserver", "0:8000"]