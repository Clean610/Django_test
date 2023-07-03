FROM python:3.9
ENV TZ=Asia/Bangkok
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
WORKDIR /code
COPY /requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
