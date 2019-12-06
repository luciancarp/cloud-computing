#!/bin/bash

echo What value do you want for D?

read d

echo How many Pods do you want to run?

read pods_num

cd ~/.ssh

ssh -tt -i "cloud-computing.pem" ubuntu@ec2-34-255-207-253.eu-west-1.compute.amazonaws.com << EOF

    sudo su -

    cd cloud-computing/

    cd cnd-master/

    python cnd_master.py --d $d --pod-count $pods_num

    exit

EOF
