#!/bin/bash

echo What value do you want for D?

read d

echo How many Pods do you want to run?

read pods_num

cd ~/.ssh

ssh -tt -i "cloud-computing.pem" ubuntu@ec2-34-242-38-144.eu-west-1.compute.amazonaws.com << EOF

    sudo su -

    ssh -i id_rsa admin@34.242.85.154

    cd cloud-computing/

    cd cnd-master/

    python cnd_master.py --d $d --pod-count $pods_num

    exit

EOF
