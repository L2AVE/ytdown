
FROM python:3.7.9

# app dir 생성
WORKDIR /src/app

# package-lock까지 가져가자
COPY package*.json ./

RUN yarn

COPY . .

EXPOSE 5000
CMD yarn run dev