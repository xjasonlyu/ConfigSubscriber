#!/bin/sh

build_push_latest() {
  docker rmi xjasonlyu/subscriber:latest \
    && docker build -t xjasonlyu/subscriber:latest . \
    && docker push xjasonlyu/subscriber:latest
}

pull_deploy_latest() {
  docker-compose down \
    && docker rmi xjasonlyu/subscriber:latest \
    && docker-compose pull \
    && docker-compose up -d
}

case $1 in
  0)
    echo "build & push"
    build_push_latest
    ;;
  1)
    echo "pull & deploy"
    pull_deploy_latest
    ;;
  *)
    echo "arguments error"
    ;;
esac
