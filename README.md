## Run CND

Make Bash script executable

```
chmod +x cnd.sh
```

Run CND

```
./cnd.sh
```

Enter the D value and number of pods desired

```
What value do you want for D?
24
How many Pods do you want to run?
8
```

## Deploy Kubernetes Cluster on AWS

Adapted from https://github.com/ValaxyTech/DevOpsDemos/blob/master/Kubernetes/k8s-setup.md

1. Create Ubuntu EC2 instance
1. install AWSCLI
   ```sh
    curl https://s3.amazonaws.com/aws-cli/awscli-bundle.zip -o awscli-bundle.zip
    apt install unzip python
    unzip awscli-bundle.zip
    #sudo apt-get install unzip - if you dont have unzip in your system
    ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
   ```
1. Install kubectl
   ```sh
   curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
    chmod +x ./kubectl
    sudo mv ./kubectl /usr/local/bin/kubectl
   ```
1. Create an IAM user/role with Route53, EC2, IAM and S3 full access
1. Attach IAM role to ubuntu server

   #### Note: If you create IAM user with programmatic access then provide Access keys.

   ```sh
     aws configure
   ```

1. Install kops on ubuntu instance:
   ```sh
    curl -LO https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
    chmod +x kops-linux-amd64
    sudo mv kops-linux-amd64 /usr/local/bin/kops
   ```
1. Create a Route53 private hosted zone (you can create Public hosted zone if you have a domain)
1. create an S3 bucket
   ```sh
    aws s3 mb s3://dev.k8s.luciancarp.in
   ```
1. Expose environment variable:
   ```sh
    export KOPS_STATE_STORE=s3://dev.k8s.luciancarp.in
   ```
1. Create sshkeys before creating cluster
   ```sh
    ssh-keygen
   ```
1. Create kubernetes cluster definitions on S3 bucket
   ```sh
    kops create cluster --cloud=aws --zones=eu-west-1b --name=dev.k8s.luciancarp.com --dns-zone=luciancarp.com --dns private
   ```
1. Create kubernetes cluser
   ```sh
     kops update cluster dev.k8s.luciancarp.in --yes
   ```
1. Validate your cluster

   ```sh
    kops validate cluster
   ```

1. To list nodes
   ```sh
     kubectl get nodes
   ```

## Pause Cluster

https://perrohunter.com/how-to-shutdown-a-kops-kubernetes-cluster-on-aws/

Set maxSize and minSize to 0

```
kops edit ig nodes
```

Get master node name

```
kops get ig
```

Change min and max size to 0

```
kops edit ig <master-name>
```

Update Cluster

```
kops update cluster --yes
kops rolling-update cluster
```
