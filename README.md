# KUBEVIRT-KIND

Numerous experiments with kubevirt using kind. Focus is on Windows VMs, because linux-based VMs were working properly out of the box most of the time.

## The following experiments are included in this repo:
* Experiment 0: bootstrapped cluster setup
* Experiment 1: Example deployment of an application using k8s api
* Experiment 2: UI-based VM management using kubevirt-manager
* Experiment 3: Using datavolume abstraction for dynamic pvc creation
* Experiment 4: Deployment using helm chart

----

# Prerequisites
- Make sure versions of kubevirt and cdi manifests match version specified below (kubevirt v1.3.0, cdi v1.59.0). To ensure all compatible versions are available in an air gapped environment, these files are provided in the bootstrap folder.
- INFO: bootstrap/bootstrap.sh installs basic kind cluster using offline resources. Using the bootstrap script, the first five steps can be skipped. 

# 0. Install kind and kubectl
kind:       https://kind.sigs.k8s.io/docs/user/quick-start/#installation
kubectl:    https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/

# 1. Create cluster (latest)
kind create cluster [--name <name> --wait 5m]

# 2. Deploy kubevirt (latest)
export VERSION=$(curl -s https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirt/stable.txt)
echo $VERSION
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/kubevirt-operator.yaml
kubectl create -f https://github.com/kubevirt/kubevirt/releases/download/${VERSION}/kubevirt-cr.yaml

# 3. Check kubevirt
By default KubeVirt will deploy 6 pods in namespace kubevirt. Following check should show 6 deployed pods
kubectl get pods -n kubevirt

# 4. Deploy cdi (latest)
export VERSION=$(basename $(curl -s -w %{redirect_url} https://github.com/kubevirt/containerized-data-importer/releases/latest))
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-operator.yaml
kubectl create -f https://github.com/kubevirt/containerized-data-importer/releases/download/$VERSION/cdi-cr.yaml

# 5. Check cdi
By default KubeVirt will deploy 4 pods in namespace cdi. Wait until finished. Following check should show Deployed
kubectl get cdi cdi -n cdi 

> this is where bootstrap ends

# 6. Create custom namespace testnamespace
kubectl create namespace testnamespace  

# 7. Expose cdi
option 1:
    kubectl create -f svc_cdi_upload_proxy.yaml
    kubectl get nodes -o wide           // send request to ip:port 
option 2:
    kubectl port-forward service/cdi-uploadproxy 1338:443 -n cdi  //preferrable

# 8. Upload win.iso to custom namespace (using 6.2). This creates a new pvc to store the iso. Make sure that the service is exposed (see 7).
virtctl image-upload pvc iso-win10 \
--image-path=windows10.iso \
--access-mode=ReadWriteOnce \
--size=7G \
--uploadproxy-url=https://localhost:1338 \
--force-bind \
--insecure \
--wait-secs=60 \
--namespace testnamespace

# 9. Create pvc for win10 disk (ignore stuck at pending, pvc WaitForFirstConsumer to change status)
kubectl create -f pvc_win10.yaml

# 10.1 Option 1: Using VMI (no virtio, no state management -> ONLY FOR TEST PURPOSES)

    # 10.1.1 Create VMI
    kubectl create -f vmi-win10.yaml

    # 10.1.2 Connect using VNC
    virtctl vnc vmi-win10 -n testnamespace

# 10.2 Option 2: Using VM (PREFERRED OPTION)

    # 10.2.1 Download openssh server from https://github.com/PowerShell/Win32-OpenSSH/releases

    # 10.2.2 Download virtio iso from https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/stable-virtio/virtio-win.iso 

    # 10.2.3 Add openssh-win64.msi to virtio iso
        - mount virtio iso
        - copy folder to local folder
        - copy openssh-win64.msi to local folder
        - add all files from local folder to new iso using
            genisoimage -o virtio_with_ssh.iso ./*

    # 10.2.4 Upload virtio.iso to namespace. Make sure that the service is exposed (see 7).
        virtctl image-upload pvc iso-virtio \
        --image-path=virtio_with_ssh.iso \
        --access-mode=ReadWriteOnce \
        --size=1.5G \
        --uploadproxy-url=https://localhost:1338 \
        --force-bind \
        --insecure \
        --wait-secs=60 \
        --namespace testnamespace

    # 10.2.2 Create vm  
        kubectl create -f vm-win10.yaml 

    # 10.2.3 Start vm
        virtctl start vm-win10 -n testnamespace
        (During install: Load Drivers > Browse > virtio disk iso > w10. Only select the folder, no subfolder. Should install two drivers, Redhat VirtIO SCSI controller and path-through controller.)

    # 10.2.4 Connect to vm
        virtctl vnc vm-win10 -n testnamespace  

# 11 Install Win10
    Install Windows 10 Pro, minimal config, disable firewall for now.
    Install ssh-server from virtio iso, create service (or port forwarding) for ssh connection to vm.

# 12 Create ssh service to expose win10 ssh server
    kubectl create -f svc_win10_ssh.yaml
    ssh is available via ssh -P <nodeport> <nodeip> and virtctl ssh vm-win10 -n testnamespace


#######################################

# misc
kubectl config current-context 
kind delete cluster -n testcluster
kind load //remember to set imagePullPolicy to Never

# test connection pod
./bootstrap.sh
kubectl create -f connectiontest/dpl_nginx.yaml
kubectl run mycurlpod --image=curlimages/curl -i --tty -- sh
curl svc-nginx
svc-nginx.default.svc.cluster.local

# load custom pod into cluster
see pod/WriteUppythonpod



# upload qcow2 to pvc
virtctl image-upload pvc win10base \
--image-path=win10.qcow2 \
--access-mode=ReadWriteOnce \
--size=25G \
--uploadproxy-url=https://localhost:1338 \
--force-bind \
--insecure \
--wait-secs=60 \
--namespace testnamespace

# builing vm in libvirt
bios, not uefi
remove nic
virtio disk 18GB

ToDO: 

1. X Include ssh in base image
2. X DataVolume-Weg zur OPtimierung (https://kubevirt.io/2019/How-To-Import-VM-into-Kubevirt.html#creation-with-a-datavolume)
3. Bundled deployment (datavolume, vm, service for ssh)
4. Enable horizontal scaling
5. Custom post install proceure using cloudInitNoCloud
