FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y pip
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install tzdata

WORKDIR /app

RUN useradd -r -d /app -s /bin/bash -c "User serving timetable manager" manager

ADD . .

RUN chown -R manager: /app
RUN chmod 777 /app

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

USER manager

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
