FROM node:14

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY ./frontend/dashboard/. .

ENV REACT_APP_API_URL=http://localhost:5002
ENV REACT_APP_EVIDENTLY_UI_URL=http://localhost:8000

EXPOSE 3000

CMD ["npm", "start"]