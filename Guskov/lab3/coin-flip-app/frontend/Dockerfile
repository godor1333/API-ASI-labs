FROM node:18-alpine as build

WORKDIR /app

# Копируем только package.json
COPY package.json ./
RUN npm install

# Копируем исходный код
COPY public ./public
COPY src ./src

RUN npm run build

FROM nginx:alpine

# Копируем собранное приложение
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]