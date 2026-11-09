# Projeto 01 — DevOps com Vagrant e Ansible

## 1. Identificação

- **Instituição:** Instituto Federal da Paraíba (IFPB) — Campus João Pessoa
- **Disciplina:** Administração de Sistemas Abertos (ASA)
- **Professor:** Leonidas Lima
- **Período:** 2026.2

**Integrantes da equipe:**

| Integrante | Matrícula |
|---|---|
| Murilo | 20242380005 |
| Rian | 20242380002 |

## 2. Descrição do projeto

O Projeto 01 tem como objetivo implementar uma infraestrutura virtual utilizando **Vagrant, VirtualBox e Ansible**, aplicando os conceitos de infraestrutura como código (IaC) e automação da administração de sistemas Linux.

A infraestrutura é composta por quatro máquinas virtuais com Debian 12 (Bookworm), cada uma responsável por diferentes serviços de rede e aplicações.

O Vagrant é utilizado para criar e gerenciar as máquinas virtuais, enquanto o Ansible automatiza a instalação dos pacotes, a configuração dos serviços e a aplicação das políticas de segurança.

Os serviços implementados incluem DHCP, DNS, SSH, NTP, LVM, NFS, MariaDB, Apache2 e montagem automática de compartilhamentos com autofs.

## 3. Tecnologias utilizadas

- **Vagrant:** criação e gerenciamento das máquinas virtuais.
- **VirtualBox:** plataforma de virtualização.
- **Debian 12 (Bookworm):** sistema operacional das máquinas.
- **Ansible:** automação das configurações por meio de playbooks YAML.
- **OpenSSH:** acesso remoto seguro e encaminhamento X11.
- **Chrony:** sincronização de data e hora.
- **ISC DHCP Server:** distribuição de endereços IPv4.
- **BIND9:** resolução de nomes DNS.
- **LVM2:** gerenciamento de volumes lógicos.
- **NFS:** compartilhamento de arquivos pela rede.
- **Autofs:** montagem automática de compartilhamentos.
- **MariaDB:** servidor de banco de dados.
- **Apache2:** servidor web.
- **Firefox ESR e Xauth:** execução de aplicações gráficas remotamente.

## 4. Infraestrutura e topologia da rede

O ambiente utiliza o domínio interno `murilo.rian.devops` e a rede privada `192.168.56.0/24`.

| Máquina | Hostname | Endereço IPv4 | Função |
|---|---|---|---|
| arq | arq.murilo.rian.devops | 192.168.56.105 | Arquivos, DHCP e DNS |
| db | db.murilo.rian.devops | 192.168.56.102 | Banco de dados |
| app | app.murilo.rian.devops | 192.168.56.152 | Servidor web |
| cli | cli.murilo.rian.devops | DHCP (ex.: 192.168.56.50) | Cliente |

O endereço do `arq` é fixo. Os endereços de `db` e `app` são atribuídos pelo DHCP por meio de reservas baseadas nos respectivos endereços MAC. O `cli` recebe um endereço da faixa dinâmica.

As máquinas possuem interfaces de rede para comunicação NAT e para acesso à rede privada do laboratório.

O DHCP do VirtualBox é desabilitado para evitar conflitos com o servidor DHCP configurado na máquina `arq`.

## 5. Configurações comuns às máquinas

O Ansible aplica configurações comuns às quatro máquinas virtuais.

### 5.1. Atualização do sistema

O sistema operacional é atualizado utilizando os recursos de gerenciamento de pacotes do Debian, por meio do módulo `apt` do Ansible.

### 5.2. Sincronização de horário

O Chrony é instalado e configurado para utilizar o servidor `pool.ntp.br`.

O fuso horário de todas as máquinas é configurado como `America/Recife`.

### 5.3. Usuários e grupos

É criado o grupo `ifpb`, ao qual pertencem os usuários `murilo` e `rian`.

O grupo recebe permissão para executar comandos administrativos utilizando `sudo`.

### 5.4. Segurança SSH

As configurações de segurança incluem:

- Autenticação exclusivamente por chaves públicas.
- Bloqueio de autenticação SSH do usuário `root`.
- Restrição de acesso aos usuários pertencentes aos grupos `vagrant` e `ifpb`.
- Configuração das chaves públicas dos integrantes.
- Exibição de uma mensagem de aviso antes da autenticação.

Mensagem configurada:

*Acesso apenas para pessoas com autorização expressa!!!*

### 5.5. Cliente NFS

O pacote `nfs-common` é instalado nas quatro máquinas, permitindo utilizar os recursos de cliente NFS.

## 6. Configuração do servidor de arquivos (arq)

O servidor `arq` concentra os serviços DHCP, DNS, armazenamento LVM e compartilhamento NFS.

### 6.1. Servidor DHCP

O ISC DHCP Server é configurado como servidor DHCP autoritativo para a rede interna.

| Parâmetro | Valor |
|---|---|
| Domínio | murilo.rian.devops |
| Servidor DNS | 192.168.56.105 |
| Rede | 192.168.56.0/24 |
| Faixa dinâmica | 192.168.56.50–192.168.56.100 |
| Gateway | 192.168.56.1 |
| Lease padrão | 180 segundos |
| Lease máximo | 3600 segundos |

São configuradas reservas de endereços:

- `db`: MAC `08:00:27:3a:00:01` → `192.168.56.102`.
- `app`: MAC `08:00:27:3a:00:02` → `192.168.56.152`.

O serviço utiliza a interface privada `eth1` do servidor `arq`.

### 6.2. Servidor DNS

O BIND9 é responsável pela resolução de nomes do domínio interno `murilo.rian.devops`.

São configuradas duas zonas:

- **Zona direta:** `murilo.rian.devops`, utilizada para resolver nomes de máquinas em endereços IPv4.
- **Zona reversa:** `56.168.192.in-addr.arpa`, utilizada para resolver endereços IPv4 em nomes de máquinas.

As zonas possuem registros para os servidores `arq`, `db` e `app`.

O BIND9 permite consultas da rede `192.168.56.0/24` e está configurado com os encaminhadores DNS externos `1.1.1.1` e `8.8.8.8`.

### 6.3. Armazenamento com LVM

O servidor `arq` possui três discos adicionais de 10 GB:

- `/dev/sdb`
- `/dev/sdc`
- `/dev/sdd`

Os discos são preparados como volumes físicos (PVs) e agrupados em um Volume Group (VG) chamado `dados`.

Dentro desse grupo, é criado um Logical Volume (LV) chamado `ifpb`, com 15 GB.

O volume lógico é formatado com o sistema de arquivos `ext4` e montado no diretório `/dados`.

A montagem automática é configurada no arquivo `/etc/fstab`, permitindo que o volume seja montado durante a inicialização do sistema.

### 6.4. Servidor NFS

O serviço NFS compartilha o diretório `/dados/nfs` com os equipamentos da rede `192.168.56.0/24`.

É criado o usuário `nfs-ifpb`, sem acesso a um shell interativo, para ser utilizado como identidade efetiva das operações remotas.

As configurações de exportação incluem:

- `rw`: permite operações de leitura e escrita.
- `sync`: utiliza gravação síncrona.
- `all_squash`: mapeia os usuários remotos para uma identidade anônima.
- `anonuid` e `anongid`: definem essa identidade como o usuário e grupo `nfs-ifpb`.
- `no_subtree_check`: desabilita a verificação de subárvores.

O diretório `/dados/nfs` pertence ao usuário `nfs-ifpb` e possui permissões `0700`, restringindo o acesso local aos demais usuários.

Os testes de escrita realizados a partir de `db`, `app` e `cli` confirmaram a criação de arquivos com proprietário `nfs-ifpb`.

## 7. Configuração do servidor de banco de dados (db)

O servidor `db` utiliza o MariaDB como sistema gerenciador de banco de dados.

O pacote `mariadb-server` é instalado pelo Ansible, e o serviço é configurado para iniciar automaticamente.

Foi validada a instalação do MariaDB 10.11.19, incluindo a execução de uma consulta SQL local.

O servidor também utiliza o `autofs` para montar automaticamente o compartilhamento NFS do `arq` no diretório `/var/nfs`.

## 8. Configuração do servidor de aplicação (app)

O servidor `app` utiliza o Apache2 para disponibilizar uma página web na rede privada.

O Ansible instala e habilita o serviço Apache2 e substitui sua página inicial pelo arquivo personalizado `index.html`.

A página contém:

- Título do projeto.
- Descrição da infraestrutura.
- Nomes dos integrantes.
- Matrículas dos integrantes.

O acesso HTTP pode ser realizado pelo endereço:

`http://192.168.56.152`

O funcionamento do Apache2 e o carregamento da página personalizada foram verificados a partir da máquina hospedeira.

O servidor `app` também utiliza `autofs` para acessar o compartilhamento NFS em `/var/nfs`.

## 9. Configuração do cliente (cli)

A máquina `cli` recebe um endereço IP dinamicamente do servidor DHCP.

O Ansible instala os pacotes `firefox-esr` e `xauth` e configura o OpenSSH para permitir o encaminhamento de aplicações gráficas pelo protocolo X11.

As opções configuradas são:

- `X11Forwarding yes`
- `X11UseLocalhost no`

O funcionamento foi verificado por meio de uma sessão SSH com encaminhamento X11 confiável, utilizando `vagrant ssh cli -- -Y`.

Durante o teste, o Firefox ESR foi executado dentro da VM e sua janela gráfica foi exibida na máquina hospedeira.

O cliente também utiliza `autofs` para montar o compartilhamento NFS remoto no diretório `/var/nfs`.

## 10. Organização dos arquivos

Os principais arquivos do projeto são:

| Arquivo ou diretório | Finalidade |
|---|---|
| `Vagrantfile` | Definição e configuração das máquinas virtuais |
| `ansible.cfg` | Configuração do Ansible |
| `hosts.ini` | Inventário das máquinas |
| `playbooks/configura-servidores.yml` | Configurações comuns |
| `playbooks/configura-ssh.yml` | Segurança e autenticação SSH |
| `playbooks/configura-arq.yml` | DHCP, BIND9, LVM e NFS |
| `playbooks/configura-autofs.yml` | Montagem NFS automática |
| `playbooks/configura-db.yml` | Instalação e configuração do MariaDB |
| `playbooks/configura-app.yml` | Instalação e configuração do Apache2 |
| `playbooks/configura-cli.yml` | Firefox ESR, Xauth e SSH/X11 |
| `playbooks/arquivos/` | Arquivos utilizados nas configurações dos serviços |
| `playbooks/chaves/` | Chaves públicas utilizadas na autenticação SSH |

O arquivo `.gitignore` impede o versionamento dos dados locais das VMs, das chaves privadas dos integrantes e do arquivo SSH gerado pelo Vagrant.

## 11. Requisitos para executar o projeto

A máquina hospedeira deve possuir:

- Sistema operacional Linux.
- VirtualBox instalado.
- Vagrant instalado.
- Ansible instalado.
- Cliente OpenSSH.
- Acesso aos pacotes necessários para o Debian 12.
- Recursos suficientes para executar as quatro máquinas virtuais.

O projeto utiliza a imagem `debian/bookworm64`.

É necessário que a rede privada do VirtualBox esteja configurada corretamente e que não exista outro servidor DHCP ativo na mesma rede.

## 12. Execução do projeto

Todos os comandos desta seção devem ser executados a partir da pasta raiz do repositório, na máquina hospedeira.

### 12.1. Acessar o diretório do projeto

`cd Projeto-01-ASA-DevOps-com-Vagrant-Ansible`

### 12.2. Inicializar e configurar o servidor arq

Na implantação inicial, configure primeiro o servidor `arq`, pois ele fornece o DHCP necessário às interfaces privadas de `db`, `app` e `cli`.

Inicie somente o `arq` e gere a configuração SSH para o Ansible:

```bash
vagrant up arq
vagrant ssh-config > vagrant-ssh-config
```

O arquivo `vagrant-ssh-config` registra os parâmetros de conexão SSH das VMs, é utilizado pela configuração local do Ansible e não é versionado no Git.

Verifique a comunicação com o `arq`:

```bash
ansible arq -m ping
```

Execute as configurações comuns e de SSH somente no `arq` e, em seguida, configure seus serviços:

```bash
ansible-playbook playbooks/configura-servidores.yml --limit arq
ansible-playbook playbooks/configura-ssh.yml --limit arq
ansible-playbook playbooks/configura-arq.yml
```

### 12.3. Inicializar as demais máquinas virtuais

Após concluir a configuração do `arq`, inicie `db`, `app` e `cli` e atualize a configuração SSH para incluir todas as máquinas:

```bash
vagrant up db app cli
vagrant ssh-config > vagrant-ssh-config
```

Verifique o estado das máquinas com:

```bash
vagrant status
```

### 12.4. Verificar a comunicação com o Ansible

```bash
ansible servidores -m ping -f 1
```

O comando deve retornar `pong` para todas as máquinas.

### 12.5. Executar os demais playbooks

Com todas as VMs ligadas e acessíveis, execute os playbooks na seguinte ordem:

```bash
ansible-playbook playbooks/configura-servidores.yml
ansible-playbook playbooks/configura-ssh.yml
ansible-playbook playbooks/configura-autofs.yml
ansible-playbook playbooks/configura-db.yml
ansible-playbook playbooks/configura-app.yml
ansible-playbook playbooks/configura-cli.yml
```

O comando `ansible-playbook --syntax-check`, seguido pelo caminho de cada playbook, pode ser utilizado para verificar a sintaxe antes da execução.

## 13. Verificação do funcionamento

Os seguintes comandos podem ser utilizados para conferir os serviços.

### DHCP

`ansible arq -b -a "systemctl is-active isc-dhcp-server"`

`ansible db -a "ip -br -4 addr show eth1"`

`ansible app -a "ip -br -4 addr show eth1"`

### DNS

`ansible arq -b -a "named-checkconf -z"`

`ansible arq -a "dig @192.168.56.105 db.murilo.rian.devops +short"`

`ansible arq -a "dig @192.168.56.105 -x 192.168.56.152 +short"`

### LVM

`ansible arq -b -a "pvs"`

`ansible arq -b -a "vgs"`

`ansible arq -b -a "lvs"`

`ansible arq -b -a "df -h /dados"`

### NFS e autofs

`ansible arq -b -a "exportfs -v"`

`ansible 'db:app:cli' -a "findmnt -T /var/nfs"`

### MariaDB

`ansible db -b -a "systemctl is-active mariadb"`

`ansible db -b -a 'mariadb -e "SELECT VERSION();"'`

### Apache2

`ansible app -b -a "systemctl is-active apache2"`

Na máquina hospedeira:

`curl http://192.168.56.152`

### SSH e X11

Na máquina hospedeira, com ambiente gráfico:

`vagrant ssh cli -- -Y`

Dentro da VM:

`echo $DISPLAY`

`firefox-esr --no-remote --new-instance`

O Firefox deverá abrir sua interface gráfica na máquina hospedeira.

## 14. Gerenciamento das máquinas virtuais

Consultar o estado das VMs:

`vagrant status`

Acessar uma máquina:

`vagrant ssh arq`

`vagrant ssh db`

`vagrant ssh app`

`vagrant ssh cli`

Reiniciar uma VM:

`vagrant reload NOME_DA_VM`

Desligar as máquinas:

`vagrant halt`

Ao reiniciar ou recriar as VMs, pode ser necessário atualizar o arquivo `vagrant-ssh-config`.

## 15. Segurança e versionamento

O projeto utiliza autenticação SSH por chave pública.

As chaves privadas dos integrantes não devem ser publicadas no GitHub. Apenas as respectivas chaves públicas podem ser versionadas.

Os arquivos gerados pelo Vagrant, como `.vagrant/` e `vagrant-ssh-config`, também são excluídos do versionamento.

As configurações de serviços são mantidas nos playbooks e nos arquivos de configuração, permitindo acompanhar as alterações realizadas durante o desenvolvimento.

## 16. Considerações finais

O projeto integra virtualização, automação, segurança, serviços de rede, armazenamento e aplicações em uma infraestrutura Linux composta por quatro máquinas virtuais.

O Vagrant fornece a estrutura virtual, enquanto o Ansible centraliza as configurações dos servidores e permite repetir as tarefas de administração.

Durante o desenvolvimento, foram realizados testes individuais de DHCP, DNS, LVM, NFS, autofs, MariaDB, Apache2 e encaminhamento X11. Essas verificações demonstraram o funcionamento dos serviços configurados.

A validação final do provisionamento completo a partir de um ambiente novo e dos acessos por hostname em todas as máquinas permanece como etapa de revisão antes da entrega.
