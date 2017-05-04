sh stop_docker.sh
docker run --rm -p 13000:5900 -p 15900:15900 --cap-add SYS_ADMIN --ipc host --privileged quay.io/openai/universe.flashgames:0.20.28 > docker1.log 2>&1  &
docker run --rm -p 13001:5900 -p 15901:15900 --cap-add SYS_ADMIN --ipc host --privileged quay.io/openai/universe.flashgames:0.20.28 > docker2.log 2>&1  &


