FROM node:20-bookworm-slim AS build
WORKDIR /app
# Sin package-lock: el lock de Windows omite @rollup/rollup-linux-x64-gnu (bug npm #4828)
COPY package.json ./
RUN npm install
COPY . .
ARG VITE_API_BASE=
ENV VITE_API_BASE=$VITE_API_BASE
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
