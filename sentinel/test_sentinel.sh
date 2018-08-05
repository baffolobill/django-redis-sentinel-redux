#!/usr/bin/env bash
MASTER_IP=$(docker-compose -f ../docker-compose.yaml exec redis-master ifconfig eth0 | grep "inet addr" | cut -d':' -f2 | cut -d' ' -f1)
SLAVE_IP1=$(docker-compose -f ../docker-compose.yaml exec redis-slave1 ifconfig eth0 | grep "inet addr" | cut -d':' -f2 | cut -d' ' -f1)
SLAVE_IP2=$(docker-compose -f ../docker-compose.yaml exec redis-slave2 ifconfig eth0 | grep "inet addr" | cut -d':' -f2 | cut -d' ' -f1)
SENTINEL_IP=$(docker-compose -f ../docker-compose.yaml exec sentinel1 ifconfig eth0 | grep "inet addr" | cut -d':' -f2 | cut -d' ' -f1)

echo Redis master: $MASTER_IP
echo Redis Slave: $SLAVE_IP1, $SLAVE_IP2
echo Redis Sentinel: $SENTINEL_IP

echo ------------------------------------------------
echo Initial status of sentinel
echo ------------------------------------------------
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 info Sentinel
echo Current master is
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL get-master-addr-by-name rmaster
echo Current slaves are
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL slaves rmaster
echo ------------------------------------------------

echo Stop redis master
docker-compose -f ../docker-compose.yaml pause redis-master
echo Wait for 25 seconds
sleep 25
echo Current infomation of sentinel
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 info Sentinel
echo Current master is
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL get-master-addr-by-name rmaster
echo Current slaves are
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL slaves rmaster

echo ------------------------------------------------
echo Restart Redis master
docker-compose -f ../docker-compose.yaml unpause redis-master
sleep 5
echo Current infomation of sentinel
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 info Sentinel
echo Current master is
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL get-master-addr-by-name rmaster
echo Current slaves are
docker-compose -f ../docker-compose.yaml exec sentinel1 redis-cli -p 26379 SENTINEL slaves rmaster