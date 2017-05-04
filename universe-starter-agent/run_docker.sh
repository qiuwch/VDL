docker run -p 10000:5900 -p 15900:15900 --cap-add SYS_ADMIN --ipc host --privileged quay.io/openai/universe.flashgames:0.20.28 &
docker run -p 10001:5900 -p 15901:15900 --cap-add SYS_ADMIN --ipc host --privileged quay.io/openai/universe.flashgames:0.20.28 &

