# Script is from https://docs.docker.com/engine/installation/linux/ubuntu/#install-using-the-repository
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update
sudo apt-get install docker-ce

# No sudo
sudo groupadd docker
sudo gpasswd -a ${USER} docker
sudo service docker restart

