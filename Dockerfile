FROM remnux/thug
MAINTAINER Edux87 "edaniel15@gmail.com"
ENV TERM xterm
USER root
ADD ./conf/logging.conf /home/thug/src/Logging/logging.conf

RUN pip install pymongo cython falcon gunicorn requests

EXPOSE 5000 8000 80
COPY ./app /app
WORKDIR /app

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "run:api"]