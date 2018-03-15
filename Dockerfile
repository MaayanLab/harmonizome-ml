FROM nikolaik/python-nodejs:latest

WORKDIR /app

ADD entrypoint.sh /entrypoint.sh
RUN set -x \
    && chmod +x /entrypoint.sh

VOLUME [ "/app" ]
EXPOSE 5000

ENV PREFIX ""
ENV MYSQL_HOST ""
ENV MYSQL_DATABASE ""
ENV MYSQL_USER ""
ENV MYSQL_PASSWORD ""

ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "npm", "run", "start" ]
