FROM python:3.10.0-alpine
RUN apk update \
  && apk add \
    mariadb-dev \
    gcc \
    python3-dev \ 
    mysql-client \
    alpine-sdk
RUN find /usr/include
RUN mkdir /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD [ "gunicorn", "--thread=1", "--timeout=240", "--bind=0.0.0.0:8700", "showlist:app"]