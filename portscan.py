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
    try:
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
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário. Saindo...")

if __name__ == "__main__":
    main()
