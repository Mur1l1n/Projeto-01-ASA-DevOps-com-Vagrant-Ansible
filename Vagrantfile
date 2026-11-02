# -*- mode: ruby -*-
# vi: set ft=ruby :

NOME1 = "murilo"
NOME2 = "rian"
XX = "05"
DOMINIO = "#{NOME1}.#{NOME2}.devops"

MAC_DB  = "0800273A0001"
MAC_APP = "0800273A0002"

#Configuração do Vagrant
Vagrant.configure("2") do |config|
  config.vm.box = "debian/bookworm64"
  config.ssh.insert_key = false
  config.vm.synced_folder ".", "/vagrant", disabled: true

  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  config.vm.provider :virtualbox do |v|
    v.memory = 512
    v.linked_clone = true
    v.check_guest_additions = false
  end

  
config.trigger.before :"Vagrant::Action::Builtin::WaitForCommunicator", type: :action do |t|
  t.warn = "Desabilitando o servidor DHCP do VirtualBox"
  t.run = {
    inline: "VBoxManage dhcpserver modify --network=HostInterfaceNetworking-vboxnet0 --disable"
  }
  t.on_error = :halt
end


  #Configuração do servidor de arquivos
  config.vm.define "arq" do |arq|
    arq.vm.hostname = "arq.#{DOMINIO}"
    arq.vm.network :private_network, ip: "192.168.56.1#{XX}"

    (0..2).each do |x|
      arq.vm.disk :disk, size: "10GB", name: "disk-#{x}"
    end
  end

  #Configuração do servidor de banco de dados
  config.vm.define "db" do |db|
    db.vm.hostname = "db.#{DOMINIO}"
    db.vm.network :private_network, type: "dhcp", mac: MAC_DB
  end

  #Configuração do servidor de aplicação
  config.vm.define "app" do |app|
    app.vm.hostname = "app.#{DOMINIO}"
    app.vm.network :private_network, type: "dhcp", mac: MAC_APP
  end

  #Configuração do host cliente
  config.vm.define "cli" do |cli|
    cli.vm.hostname = "cli.#{DOMINIO}"
    cli.vm.network :private_network, type: "dhcp"

    cli.vm.provider :virtualbox do |v|
      v.memory = 1024
    end
  end

end