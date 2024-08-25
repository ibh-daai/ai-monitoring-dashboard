# Build stage
FROM node:14
WORKDIR /app
COPY ./frontend/dashboard/package*.json ./frontend/dashboard/

ARG REACT_APP_DASHBOARD_API_URL
ENV REACT_APP_DASHBOARD_API_URL=$REACT_APP_DASHBOARD_API_URL

WORKDIR /app/frontend/dashboard
RUN npm install
COPY ./frontend/dashboard ./
RUN npm run build

# Production stage
RUN npm install -g serve
EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]