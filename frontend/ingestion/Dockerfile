# Build stage
FROM node:14 as build
WORKDIR /app
COPY ./frontend/ingestion/package*.json ./frontend/ingestion/

WORKDIR /app/frontend/ingestion
RUN npm install
COPY ./frontend/ingestion ./
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/frontend/ingestion/build /usr/share/nginx/html
COPY ./frontend/ingestion/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]