# -*- mode: ruby -*-
# vi: set ft=ruby :
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--name", "app-backend", "--memory", "1536"]
  end

  # Ansible needs Python 2.7
  config.vm.provision "shell" do |s|
    s.inline = "apt-get install -y python"
  end

  # Run the ansible script
  config.vm.provision "ansible" do |ansible|
    ansible.verbose = "vvv"
    ansible.playbook = "vagrant.yml"
  end

end
