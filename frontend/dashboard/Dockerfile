FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY ./frontend/dashboard/. .

EXPOSE 3000

CMD ["npm", "start"]