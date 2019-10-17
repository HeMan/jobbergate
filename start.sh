#!/bin/bash
app="jobbergate"
docker build -t ${app} .
docker run -d -p 56733:80 \
  --name=${app} \
  -v $PWD/apps:/app/apps ${app}
