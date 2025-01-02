# Source: https://kubernetes.io/blog/2019/07/23/get-started-with-kubernetes-using-python/

# Using minikube
1. Enter minikube docker env
    eval $(minikube docker-env)

2. Create docker container using python base and Dockerfile
    docker build -f Dockerfile -t k8stest:latest .

3. Apply deployment.yaml
    kubectl apply -f deployment_apigateway.yaml

4. Get ip and port of srvice
    minikube service api-gateway-service --url

# Using kind
https://iximiuz.com/en/posts/kubernetes-kind-load-docker-image/

docker build -f Dockerfile -t k8stest:latest .
kind load docker-image k8stest:latest -n testcluster 
kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh
curl api-gateway-service:1337/helloworld
FQDN: api-gateway-service.default.svc.cluster.local

should work

# misc
Idea: connect to host from devcontainer using ssh, execute scripts there
