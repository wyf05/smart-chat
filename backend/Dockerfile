# 基础镜像：官方 Python 3.11 精简版（约 120MB）
FROM python:3.11-slim

WORKDIR /app

# 先只复制依赖清单并安装（利用 Docker 层缓存：改代码不用重装依赖，构建快很多）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 再复制源码（.env 不进镜像，由 compose 注入，避免密钥泄露）
COPY app ./app

# data 目录由 compose 挂载数据卷，这里只创建占位
RUN mkdir -p data

EXPOSE 8000

# 容器内必须绑 0.0.0.0：绑 127.0.0.1 只有容器自己访问得到，外面进不来
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
