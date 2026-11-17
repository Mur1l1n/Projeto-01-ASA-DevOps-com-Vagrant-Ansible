# -*- mode: ruby -*-
# vi: set ft=ruby :

GRUPOS_ANSIBLE = {
  "servidores" => ["arq", "db", "app", "cli"]
}

# Configuração do Vagrant
Vagrant.configure("2") do |config|
  # Base Debian, chave padrão do Vagrant e compartilhamento /vagrant desativado.
  config.vm.box = "debian/bookworm64"
  config.ssh.insert_key = false

  # Evita atualizações automáticas do Guest Additions quando o plugin está instalado.
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  # Recursos padrão das VMs e clones vinculados para economizar espaço.
  config.vm.provider :virtualbox do |v|
    v.linked_clone = true
    v.check_guest_additions = false
  end

  # Prepara o DHCP uma vez por comando, antes de iniciar qualquer VM.
  # Esta versão usa o DHCP do VirtualBox, sem um segundo servidor DHCP na arq.
  config.trigger.before [:up, :reload], type: :command do |trigger|
    trigger.info = "Configurando o DHCP do VirtualBox na vboxnet0"
    trigger.run = {
      inline: "vboxmanage dhcpserver modify --interface=vboxnet0 --disable"
    }
    trigger.on_error = :continue
  end

  # Configuração do servidor de arquivos
  config.vm.define "arq" do |arq|
    arq.vm.hostname = "arq.murilo.rian.devops"
    arq.vm.network :private_network, ip: "192.168.56.105"
    arq.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end

    # Três discos de 10 GB destinados ao armazenamento LVM configurado pelo Ansible.
    (0..2).each do |x|
      arq.vm.disk :disk, size: "10GB", name: "disk-#{x}"
    end
    
    # provisiona o playbook do servidor arq
    arq.vm.provision "configura-arq", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-arq.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # db e app recebem IP por DHCP, com reservas identificadas pelos MACs abaixo.
  # Configuração do servidor de banco de dados
  config.vm.define "db" do |db|
    db.vm.hostname = "db.murilo.rian.devops"
    db.vm.network "private_network", type: "dhcp", mac: "0800273A0001"
    db.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end

    db.vm.provision "configura-db", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-db.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # Configuração do servidor de aplicação
  config.vm.define "app" do |app|
    app.vm.hostname = "app.murilo.rian.devops"
    app.vm.network "private_network", type: "dhcp", mac: "0800273A0002" 
    app.vm.provider "virtualbox" do |vb|
      vb.memory = "512"
    end

    app.vm.provision "configura-app", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-app.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # Configuração do host cliente
  config.vm.define "cli" do |cli|
    cli.vm.hostname = "cli.murilo.rian.devops"
    cli.vm.network "private_network", type: "dhcp"
    cli.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
    end

    cli.vm.provision "configura-cli", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-cli.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

end
