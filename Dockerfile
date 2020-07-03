FROM python:3.8-buster AS build
WORKDIR /usr/src/app

# Container inrichten
## packages nodig voor compilen
RUN apt-get update && apt-get upgrade -y &&  apt-get -y install nodejs git nginx gcc yarn make tzdata python-rtree curl
RUN curl https://www.npmjs.com/install.sh | sh

## tijd goedzetten
RUN cp /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime  &&\
    echo "Europe/Amsterdam" > /etc/timezone

# frontend
ADD frontend /tmp/frontend/
RUN cd /tmp/frontend                        &&\
    npm install                             &&\
    npm run build                           &&\
    mkdir /usr/src/app/frontend             &&\
    cp -pr dist/* /usr/src/app/frontend/

# backend
ADD backend/ backend/
RUN cd backend && pip install -r requirements.txt

COPY build_docker/nginx.conf /etc/nginx/
RUN rm -rf /etc/nginx/conf.d

# container poetsen
RUN apt-get -y remove gcc make yarn npm nodejs git tzdata curl
RUN rm -rf /tmp/*
RUN apt-get -y autoremove

# starten
ADD build_docker/start.sh /
ENV PYTHONPATH=/usr/src/app/backend
RUN chmod a+x /start.sh
CMD ["/start.sh"]

