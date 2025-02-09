Este é um script em Python que automatiza o processo de escaneamento de uma faixa de IPs e captura de banners de serviços expostos, utilizando ferramentas como masscan para escaneamento de portas e netcat ou telnet para captura de banners. O script foi criado para fins educativos e de segurança ofensiva em ambientes controlados.

Funcionalidades
Escaneamento de IPs e portas em massa utilizando o masscan.
Captura de banners de serviços em portas abertas, como HTTP, MySQL, RDP, SSH, etc.
Geração de relatório com os IPs e banners encontrados.
Requisitos
Python 3.x instalado no sistema.
Masscan instalado e configurado no PATH do sistema.
Netcat ou Telnet para captura de banners.
Permissões de rede para realizar o escaneamento em massa.
Instalação

1 Clone este repositório:
git clone https://github.com/seu-usuario/escaneamento-em-massa.git
cd escaneamento-em-massa

2 Instale os requisitos necessários (se houver):
pip install -r requirements.txt

3 Certifique-se de que o Masscan e o Netcat ou Telnet estão instalados no seu sistema. Para instalar o Masscan, você pode usar o seguinte comando:
No Linux (Ubuntu/Debian): sudo apt-get install masscan
No Windows: Baixe a versão compilada do Masscan

Uso

1 Inicie o script passando a faixa de IPs e as portas que deseja escanear. O script permite personalizar a faixa de IPs e portas a serem verificadas:
python escaneamento.py

2 O script solicitará que você insira a faixa de IPs e as portas. A execução do escaneamento pode demorar dependendo do tamanho da faixa de IPs e das portas selecionadas.

3 Após o escaneamento, os resultados serão exibidos no terminal e também salvos em um arquivo relatorio.txt, que contém as informações sobre os IPs e os banners capturados.

Exemplo de uso
1 Quando executado, o script pedirá para inserir o intervalo de IPs: Digite a faixa de IPs para escanear (exemplo: 192.168.1.0/24): 177.126.128.0/24
2 Depois, será solicitado para inserir as portas a serem verificadas: Digite as portas a serem escaneadas (exemplo: 80,443,22): 3306,80,443
3 O script irá realizar o escaneamento e gerar um relatório com os banners encontrados. 

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
