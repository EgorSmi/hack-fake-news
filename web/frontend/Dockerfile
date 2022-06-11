FROM node:16-alpine

WORKDIR /app

COPY package.json /app

RUN npm i

COPY . /app
RUN ["chmod", "+x", "./runfrontend"]

CMD ./runfrontend