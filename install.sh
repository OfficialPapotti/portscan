#!/bin/bash

# Função para verificar se um comando está instalado
check_installed() {
    command -v $1 &>/dev/null
    if [ $? -ne 0 ]; then
        echo "$1 não está instalado. Instalando..."
        install_package $1
    else
        echo "$1 já está instalado."
    fi
}

# Função para instalar pacotes necessários
install_package() {
    if [ -f /etc/debian_version ]; then
        # Para distribuições baseadas no Debian (Ubuntu, Debian, etc)
        sudo apt update
        sudo apt install -y $1
    elif [ -f /etc/redhat-release ]; then
        # Para distribuições baseadas no RedHat (CentOS, Fedora, etc)
        sudo yum install -y $1
    else
        echo "Sistema não suportado para instalação automática de pacotes."
    fi
}

# Instalando os pacotes necessários
echo "Verificando dependências..."

check_installed "masscan"
check_installed "nc"  # netcat
check_installed "telnet"

# Verificando se o Python 3 está instalado
if ! command -v python3 &>/dev/null; then
    echo "Python3 não encontrado. Instalando..."
    install_package "python3"
    install_package "python3-pip"
fi

# Baixando ou copiando o script Python
echo "Baixando o script Python de escaneamento..."

SCRIPT_PATH="/usr/local/bin/scan.py"
cat <<EOL > $SCRIPT_PATH
import socket
import ipaddress

def banner_grabber(ip, port):
    try:
        # Verifica se a porta é válida (um número entre 1 e 65535)
        if not (1 <= port <= 65535):
            raise ValueError(f"Porta inválida: {port}")
        
        s = socket.socket()
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        banner = s.recv(1024)
        return banner
    except Exception as e:
        return None

def main():
    # Entrada de IP e portas pelo usuário
    ip_range = input("Digite a faixa de IPs para escanear (exemplo: 192.168.0.0/16): ")
    ports = input("Digite as portas para escanear (exemplo: 80,443,3306): ").split(',')

    # Validando os IPs
    try:
        ip_network = ipaddress.IPv4Network(ip_range)
    except ValueError as e:
        print(f"Erro ao processar faixa de IPs: {e}")
        return

    # Escaneando IPs
    print(f"Escaneando {ip_range} nas portas {', '.join(ports)}...")

    # Para cada IP na faixa
    for ip in ip_network.hosts():
        for port in ports:
            try:
                port = int(port)  # Tenta converter a porta para inteiro
                print(f"Conectando-se a {port}/tcp em {ip} para capturar banner...")
                banner = banner_grabber(str(ip), port)
                if banner:
                    print(f"Banner de {ip}:{port} - {banner.decode()}")
                else:
                    print(f"Sem resposta de banner para {ip}:{port}")
            except ValueError as e:
                print(f"Erro com a porta {port}: {e}")

if __name__ == "__main__":
    main()
EOL

# Tornando o script executável
sudo chmod +x $SCRIPT_PATH

# Informações finais
echo "Instalação concluída com sucesso."
echo "Você pode executar o script com o comando: python3 /usr/local/bin/scan.py"
