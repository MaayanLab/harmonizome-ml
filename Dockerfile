FROM nikolaik/python-nodejs:latest

WORKDIR /app

ADD package.json /app/package.json
RUN set -x \
    && npm install

ADD app/requirements.txt /app/requirements.txt
RUN set -x \
    && pip install -r requirements.txt

VOLUME [ "/app" ]
EXPOSE 5000

ENV PREFIX ""
ENV MYSQL_HOST ""
ENV MYSQL_DATABASE ""
ENV MYSQL_USER ""
ENV MYSQL_PASSWORD ""

CMD [ "npm", "run", "start" ]
