FROM python:3.10-slim-bullseye

RUN apt update 
RUN apt install -y gcc 
RUN apt install -y python3-dev wget
RUN wget https://dlm.mariadb.com/2678574/Connectors/c/connector-c-3.3.3/mariadb-connector-c-3.3.3-debian-bullseye-amd64.tar.gz -O - | tar -zxf - --strip-components=1 -C /usr
RUN apt install -y libmariadb-dev
RUN apt install -y libmariadb-dev-compat default-libmysqlclient-dev build-essential pkg-config
RUN apt list
RUN find /usr/include
RUN mkdir /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV PYTHONUNBUFFERED 1
CMD [ "gunicorn", "--thread=1", "--timeout=240", "--bind=0.0.0.0:8700", "showlist:app"]