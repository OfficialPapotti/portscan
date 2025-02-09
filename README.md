# PortScan - Script de Escaneamento de IPs e Captura de Banners

Este é um script em Python que automatiza o processo de escaneamento de uma faixa de IPs e captura de banners de serviços expostos, utilizando ferramentas como `masscan` para escaneamento de portas e `netcat` ou `telnet` para captura de banners. O script foi criado para fins educativos e de segurança ofensiva em ambientes controlados.

## Funcionalidades
- Escaneamento de IPs e portas em massa utilizando o `masscan`.
- Captura de banners de serviços em portas abertas, como HTTP, MySQL, RDP, SSH, entre outros.
- Geração de relatórios com os IPs e banners encontrados.

## Requisitos
- Python 3.x instalado no sistema.
- `masscan` instalado e configurado no PATH do sistema.
- `netcat` ou `telnet` para captura de banners.
- Permissões de rede para realizar o escaneamento em massa.

## Instalação

1. Clone este repositório:
    
    git clone https://github.com/OfficialPapotti/portscan
    cd portscan
    

2. Execute o script de instalação automatizada para instalar todas as dependências necessárias (incluindo o `masscan`, `netcat` e o ambiente Python):
   
    chmod +x install.sh
    ./install.sh
    

   O script `install.sh` irá:
   - Instalar o `masscan`, `netcat` e `telnet` no sistema.
   - Configurar o ambiente Python e instalar as dependências.
   - Garantir que as ferramentas necessárias estejam no PATH para o correto funcionamento do script.

## Uso

Após a execução do script de instalação, você pode iniciar o escaneamento com o seguinte comando:

python3 scan.py
