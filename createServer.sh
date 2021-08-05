#!/bin/sh

docker build -t some-content-nginx .
docker run --name nginx-test -d -p 80:80 some-content-nginx
