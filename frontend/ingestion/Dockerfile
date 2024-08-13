FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY ./frontend/ingestion/. .

EXPOSE 3001

ENV PORT=3001

CMD ["npm", "start"]