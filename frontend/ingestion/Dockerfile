# Build stage
FROM node:14
WORKDIR /app
COPY ./frontend/ingestion/package*.json ./frontend/ingestion/

ARG REACT_APP_INGESTION_API_URL
ENV REACT_APP_INGESTION_API_URL=$REACT_APP_INGESTION_API_URL

WORKDIR /app/frontend/ingestion
RUN npm install
COPY ./frontend/ingestion ./
RUN npm run build

# Production stage
RUN npm install -g serve
EXPOSE 3001

CMD ["serve", "-s", "build", "-l", "3001"]