#!/bin/bash
sudo apt update
git clone https://github.com/BrunoSDomingues/tasks.git && mv tasks /home/ubuntu
sudo sed -i 's/node1/ADD_IP_HERE/' /home/ubuntu/tasks/portfolio/settings.py 
/home/ubuntu/tasks/./install.sh
echo $? >> /home/ubuntu/default.txt
reboot