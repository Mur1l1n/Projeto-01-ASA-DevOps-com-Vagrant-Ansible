# -*- mode: ruby -*-
# vi: set ft=ruby :

# Grupo entregue ao inventário gerado pelo provisionador Ansible do Vagrant.
# Permite reutilizar o playbook comum nas quatro máquinas.
GRUPOS_ANSIBLE = {
  "servidores" => ["arq", "db", "app", "cli"]
}

# Configuração do Vagrant
Vagrant.configure("2") do |config|
  # Define a imagem Debian 12 e mantém a chave SSH padrão do Vagrant.
  # O compartilhamento /vagrant não é configurado explicitamente neste arquivo.
  config.vm.box = "debian/bookworm64"
  config.ssh.insert_key = false

  # Evita atualizações automáticas do Guest Additions quando o plugin está instalado.
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end

  # Clones vinculados reutilizam o disco da imagem base para economizar espaço.
  # A verificação de Guest Additions é desativada para este laboratório.
  config.vm.provider :virtualbox do |v|
    v.linked_clone = true
    v.check_guest_additions = false
  end

  # Antes da ação de aguardar comunicação SSH, desativa o DHCP do VirtualBox
  # na interface vboxnet0. O DHCP do laboratório será fornecido pela VM arq.
  # O gatilho pode executar a cada ocorrência dessa ação durante a inicialização.
  config.trigger.before :"Vagrant::Action::Builtin::WaitForCommunicator", type: :action do |t|
    t.warn = "Interrompe o servidor dhcp do virtualbox"
    t.run = {inline: "vboxmanage dhcpserver modify --disable --interface vboxnet0"} 
  end

  # arq concentra DHCP, DNS, LVM e NFS; seu IP fixo permite iniciar a rede.
  # Reserva 512 MB de RAM e usa o playbook específico após criar a VM.
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
  # db recebe 512 MB de RAM e instala MariaDB e o cliente autofs via Ansible.
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

  # app recebe 512 MB de RAM e publica a página HTML com Apache2.
  # Seu MAC corresponde à reserva 192.168.56.152 em arquivos/dhcpd.conf.
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

  # cli recebe IP dinâmico e 1024 MB de RAM para executar o Firefox via X11.
  # O provisionamento instala as ferramentas de acesso e o autofs.
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
