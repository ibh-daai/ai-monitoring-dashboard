# Build stage
FROM node:14 as build
WORKDIR /app
COPY ./frontend/dashboard/package*.json ./frontend/dashboard/

WORKDIR /app/frontend/dashboard
RUN npm install
COPY ./frontend/dashboard ./
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/frontend/dashboard/build /usr/share/nginx/html
COPY ./frontend/dashboard/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]