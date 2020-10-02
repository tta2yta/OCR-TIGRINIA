FROM ubuntu:latest

ENV DEBIAN_FRONTEND=noninteractive 

RUN apt-get update -y && apt-get -y install cron
RUN apt-get install -y python3-pip python3-minimal libsm6 libxext6
RUN apt update && apt install  libsm6 libxext6
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y

RUN apt install -y libtesseract-dev libleptonica-dev liblept5
RUN apt-get update && apt-get install -y tesseract-ocr
RUN apt-get install -y tesseract-ocr-amh

COPY . /app

# COPY crontab file in the cron directory
#COPY ted /etc/cron.d/crontab
COPY ted /var/spool/cron/crontabs/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
python3-pip


RUN pip3 install pillow
RUN pip3 install pytesseract
RUN pip3 install opencv-python
RUN pip3 install -r requirements.txt


# Copy hello-cron file to the cron.d directory
COPY ted /etc/cron.d/ted

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/ted

# Apply cron job
RUN crontab /etc/cron.d/ted

RUN mkdir /data

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

CMD service rsyslog start && service cron start && tail -f /var/log/syslog

ENTRYPOINT ["python3"]
CMD ["app.py"]
#CMD cron && tail -f /var/log/cron.log

