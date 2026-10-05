#!/bin/bash
# 多镜像轮询拉取基础镜像（每个镜像源限时，成功即换下一个镜像）
set -u
MIRRORS=("docker.1ms.run" "docker.m.daocloud.io" "hub.rat.dev" "dockerpull.cn")
IMAGES=("python:3.11-slim" "node:20-alpine" "nginx:alpine")

for IMG in "${IMAGES[@]}"; do
  if docker image inspect "$IMG" > /dev/null 2>&1; then
    echo "[skip] $IMG already exists"
    continue
  fi
  ok=0
  for M in "${MIRRORS[@]}"; do
    echo "[pull] $M/$IMG (timeout 420s)"
    if timeout 420 docker pull "$M/$IMG" > /tmp/pull_${M//./_}_${IMG//[:.]/_}.log 2>&1; then
      docker tag "$M/$IMG" "$IMG"
      echo "[ok] $IMG via $M"
      ok=1
      break
    else
      echo "[fail] $M/$IMG"
      tail -1 "/tmp/pull_${M//./_}_${IMG//[:.]/_}.log"
    fi
  done
  [ $ok -eq 0 ] && echo "[ERROR] could not pull $IMG from any mirror"
done
docker images | grep -E "python|node|nginx"
echo "ALL DONE"
