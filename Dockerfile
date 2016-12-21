FROM ubuntu:latest

RUN apt-get update

RUN apt-get install iproute2 iputils-ping -y && rm -rf /var/lib/apt/lists/*

