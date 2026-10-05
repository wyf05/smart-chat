# 第一阶段：Node 打包 Vue 源码为静态文件
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --registry=https://mirrors.cloud.tencent.com/npm/
COPY . .
RUN npm run build     # 产出 dist/ 目录

# 第二阶段：Nginx 托管静态文件
# 最终镜像不含 Node（1G+），只有 Nginx（~50MB），这就是多阶段构建的价值
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
