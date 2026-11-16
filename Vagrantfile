# -*- mode: ruby -*-
# vi: set ft=ruby :
require "open3"

# Identificação da equipe e domínio das VMs.
NOME1 = "murilo"
NOME2 = "rian"
XX = "05"
DOMINIO = "#{NOME1}.#{NOME2}.devops"

# Interface host-only existente no hospedeiro e IP fixo da VM arq.
REDE_HOST_ONLY = "vboxnet0"
MASCARA_REDE   = "255.255.255.0"
IP_ARQ         = "192.168.56.1#{XX}"

# DHCP do VirtualBox. A faixa dinâmica não inclui o IP da arq nem as reservas.
DHCP_IP     = "192.168.56.100"
DHCP_INICIO = "192.168.56.200"
DHCP_FIM    = "192.168.56.254"

# IPs propostos para as reservas. Ajuste se o enunciado indicar outros.
MAC_DB  = "0800273A0001"
MAC_APP = "0800273A0002"
IP_DB   = "192.168.56.106"
IP_APP  = "192.168.56.107"

REDE_DHCP = {
  type: "dhcp",
  name: REDE_HOST_ONLY,
  netmask: MASCARA_REDE,
  dhcp_ip: DHCP_IP,
  dhcp_lower: DHCP_INICIO,
  dhcp_upper: DHCP_FIM
}

GRUPOS_ANSIBLE = {
  "servidores" => ["arq", "db", "app", "cli"]
}

# Configuração do Vagrant
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

  # Prepara o DHCP uma vez por comando, antes de iniciar qualquer VM.
  # Esta versão usa o DHCP do VirtualBox, sem um segundo servidor DHCP na arq.
  config.trigger.before [:up, :reload], type: :command do |trigger|
    trigger.info = "Configurando o DHCP do VirtualBox em #{REDE_HOST_ONLY}"
    trigger.on_error = :halt

    trigger.ruby do |_env, _machine|
      vbox = lambda do |*args|
        saida, status = Open3.capture2e("VBoxManage", *args)
        raise "VBoxManage #{args.join(' ')} falhou: #{saida.strip}" unless status.success?

        saida
      end

      servidores = vbox.call("list", "dhcpservers")
      rede = "HostInterfaceNetworking-#{REDE_HOST_ONLY}"
      existe = servidores.each_line.any? do |linha|
        linha.match?(/\ANetworkName:\s+#{Regexp.escape(rede)}\s*\z/)
      end

      vbox.call(
        "dhcpserver", existe ? "modify" : "add",
        "--interface=#{REDE_HOST_ONLY}",
        "--server-ip=#{DHCP_IP}", "--netmask=#{MASCARA_REDE}",
        "--lower-ip=#{DHCP_INICIO}", "--upper-ip=#{DHCP_FIM}", "--enable",
        "--mac-address=#{MAC_DB.scan(/../).join(':')}", "--fixed-address=#{IP_DB}",
        "--mac-address=#{MAC_APP.scan(/../).join(':')}", "--fixed-address=#{IP_APP}"
      )
    end
  end

  # Configuração do servidor de arquivos
  config.vm.define "arq" do |arq|
    arq.vm.hostname = "arq.#{DOMINIO}"
    arq.vm.network :private_network, ip: IP_ARQ,
      name: REDE_HOST_ONLY, netmask: MASCARA_REDE

    # Três discos de 10 GB destinados ao armazenamento LVM configurado pelo Ansible.
    (0..2).each do |x|
      arq.vm.disk :disk, size: "10GB", name: "disk-#{x}"
    end

    arq.vm.provision "configura-servidores", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-servidores.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    arq.vm.provision "configura-ssh", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-ssh.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    arq.vm.provision "configura-arq", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-arq.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # db e app recebem IP por DHCP, com reservas identificadas pelos MACs abaixo.
  # Configuração do servidor de banco de dados
  config.vm.define "db" do |db|
    db.vm.hostname = "db.#{DOMINIO}"
    db.vm.network :private_network, **REDE_DHCP.merge(mac: MAC_DB)

    db.vm.provision "configura-servidores", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-servidores.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    db.vm.provision "configura-ssh", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-ssh.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    db.vm.provision "configura-autofs", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-autofs.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    db.vm.provision "configura-db", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-db.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # Configuração do servidor de aplicação
  config.vm.define "app" do |app|
    app.vm.hostname = "app.#{DOMINIO}"
    app.vm.network :private_network, **REDE_DHCP.merge(mac: MAC_APP)

    app.vm.provision "configura-servidores", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-servidores.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    app.vm.provision "configura-ssh", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-ssh.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    app.vm.provision "configura-autofs", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-autofs.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    app.vm.provision "configura-app", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-app.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # Configuração do host cliente
  config.vm.define "cli" do |cli|
    cli.vm.hostname = "cli.#{DOMINIO}"
    cli.vm.network :private_network, **REDE_DHCP

    # O cliente recebe mais memória para executar o Firefox com encaminhamento X11.
    cli.vm.provider :virtualbox do |v|
      v.memory = 1024
    end

    cli.vm.provision "configura-servidores", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-servidores.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    cli.vm.provision "configura-ssh", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-ssh.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    cli.vm.provision "configura-autofs", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-autofs.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end

    cli.vm.provision "configura-cli", type: "ansible" do |ansible|
      ansible.playbook = "playbooks/configura-cli.yml"
      ansible.groups = GRUPOS_ANSIBLE
    end
  end

  # Gera o SSH config somente para as VMs que estão em execução.
  config.trigger.after :up, type: :command do |trigger|
    trigger.info = "Gerando vagrant-ssh-config para o Ansible"
    trigger.on_error = :continue

    trigger.ruby do |env, _machine|
      arquivos_ssh = env.active_machines.filter_map do |nome, provider|
        next unless GRUPOS_ANSIBLE.fetch("servidores").include?(nome.to_s)
        next unless env.machine(nome, provider).state.id == :running

        saida, status = Open3.capture2("vagrant", "ssh-config", nome.to_s, chdir: env.root_path.to_s)
        raise "Não foi possível gerar a configuração SSH da VM #{nome}." unless status.success? && !saida.strip.empty?

        saida
      end

      unless arquivos_ssh.empty?
        File.write(env.root_path.join("vagrant-ssh-config"), arquivos_ssh.join("\n"))
      end
    end
  end
end
