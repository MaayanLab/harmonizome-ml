FROM nikolaik/python-nodejs:latest

WORKDIR /app

ADD package.json /app/package.json
RUN set -x \
    && npm install

ADD app/requirements.txt /app/requirements.txt
RUN set -x \
    && pip install -r requirements.txt

EXPOSE 5000

ADD ./app/ /app/app
ADD ./data/attribute_list.json /app/data/attribute_list.json
ADD ./data/harmonizome.py /app/data/harmonizome.py
ADD ./gruntfile.js /app/gruntfile.js

ARG HARMONIZOME_API_PREFIX=Harmonizome-ML
ENV HARMONIZOME_API_PREFIX=${HARMONIZOME_API_PREFIX}

CMD [ "npx", "grunt", "shell:flaskApp" ]
