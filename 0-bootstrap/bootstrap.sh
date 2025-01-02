#!/bin/bash
echo "> Bootstrapping kind cluster. Entire process should take around 12min."
sleep 2

# create cluster
echo "> Creating cluster..."
sleep 2
kind create cluster --name testcluster --wait 2m

# deploy kubevirt
echo "> Deploying kubevirt..."
sleep 2
kubectl create -f kubevirt-operator.yaml
sleep 240
kubectl create -f kubevirt-cr.yaml
sleep 120

# check kubevirt deployment
echo "> Checking kubevirt deployment (should say Deployed)..."
sleep 2
kubectl get kubevirt -n kubevirt

# deploy cdi
echo "> Deploying cdi..."
sleep 2
kubectl create -f cdi-operator.yaml
sleep 240
kubectl create -f cdi-cr.yaml
sleep 120

# check cdi deployment
echo "> Checking cdi deployment (should say Deployed)..."
sleep 2
kubectl get cdi cdi -n cdi 

read -p "Press any key to open k9s... " -n1 -s

k9s