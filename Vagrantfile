# -*- mode: ruby -*-
# vi: set ft=ruby :

# Identificação da equipe: forma o domínio e o final do IP fixo do arq.
NOME1 = "murilo"
NOME2 = "rian"
XX = "05"
DOMINIO = "#{NOME1}.#{NOME2}.devops"

# MACs fixos para o DHCP reconhecer db e app e reservar seus endereços.
MAC_DB  = "0800273A0001"
MAC_APP = "0800273A0002"

#Configuração do Vagrant
Vagrant.configure("2") do |config|
  # Base Debian, chave padrão do Vagrant e compartilhamento /vagrant desativado.
  config.vm.box = "debian/bookworm64"
  config.ssh.insert_key = false
  config.vm.synced_folder ".", "/vagrant", disabled: true

  # Evita atualizações automáticas do Guest Additions quando o plugin está instalado.
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  # Recursos padrão das VMs e clones vinculados para economizar espaço.
  config.vm.provider :virtualbox do |v|
    v.memory = 512
    v.linked_clone = true
    v.check_guest_additions = false
  end

  
# Antes de aguardar o SSH, desativa o DHCP da rede vboxnet0 no hospedeiro.
# Uma falha interrompe a operação para evitar dois servidores DHCP na rede.
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

    # Três discos de 10 GB destinados ao armazenamento LVM configurado pelo Ansible.
    (0..2).each do |x|
      arq.vm.disk :disk, size: "10GB", name: "disk-#{x}"
    end
  end

  # db e app recebem IP por DHCP, com reservas identificadas pelos MACs abaixo.
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

    # O cliente recebe mais memória para executar o Firefox com encaminhamento X11.
    cli.vm.provider :virtualbox do |v|
      v.memory = 1024
    end
  end

end