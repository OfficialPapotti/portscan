MassScan - Script de Escaneamento de IPs e Captura de Banners
Este é um script em Python que automatiza o processo de escaneamento de uma faixa de IPs e captura de banners de serviços expostos, utilizando ferramentas como masscan para escaneamento de portas e netcat ou telnet para captura de banners. O script foi criado para fins educativos e de segurança ofensiva em ambientes controlados.

Funcionalidades
Escaneamento de IPs e portas em massa utilizando o masscan.
Captura de banners de serviços em portas abertas, como HTTP, MySQL, RDP, SSH, entre outros.
Geração de relatórios com os IPs e banners encontrados.
Requisitos
Python 3.x instalado no sistema.
masscan instalado e configurado no PATH do sistema.
netcat ou telnet para captura de banners.
Permissões de rede para realizar o escaneamento em massa.
Instalação
Clone este repositório: 
git clone https://github.com/OfficialPapotti/portscan + cd portscan

Execute o script de instalação automatizada para instalar todas as dependências necessárias (incluindo o masscan, netcat e o ambiente Python): 
chmod +x install.sh
./install.sh

O script install.sh irá:
Instalar o masscan, netcat e telnet no sistema.
Configurar o ambiente Python e instalar as dependências.
Garantir que as ferramentas necessárias estejam no PATH para o correto funcionamento do script.

Uso
Após a execução do script de instalação, você pode iniciar o escaneamento com o seguinte comando: python3 scan.py
O script solicitará que você insira a faixa de IPs e as portas a serem escaneadas. O processo de escaneamento pode demorar dependendo do tamanho da faixa de IPs e das portas selecionadas.
Após o escaneamento, os resultados serão exibidos no terminal e também salvos em um arquivo de relatório com as informações dos IPs e banners encontrados.

Exemplo de Uso
O script pedirá para inserir a faixa de IPs: Digite a faixa de IPs para escanear (exemplo: 192.168.1.0/24): 177.126.128.0/24
Em seguida, será solicitado para inserir as portas a serem verificadas: Digite as portas a serem escaneadas (exemplo: 80,443,22): 3306,80,443
O script realizará o escaneamento e gerará um relatório com os banners encontrados.

Exemplo de Saída
O relatório gerado pode ser parecido com este:
IP: 177.126.128.235
Porta: 3306 (MySQL)
Banner: MySQL 8.0.18

IP: 177.126.128.240
Porta: 80 (HTTP)
Banner: Apache/2.4.41 (Ubuntu)


Considerações de Segurança
Uso responsável: Este script deve ser usado apenas em ambientes controlados e autorizados, como redes de teste ou laboratórios. Realizar escaneamento em massa sem permissão em redes externas pode ser considerado ilegal em várias jurisdições.
Permissões: Certifique-se de ter permissão explícita para realizar o escaneamento e a coleta de banners em qualquer rede ou sistema.
Ética: Sempre siga práticas éticas ao realizar testes de segurança. Não use este script para fins maliciosos.

Licença
Este projeto é licenciado sob a MIT License - veja o arquivo LICENSE para mais detalhes.

