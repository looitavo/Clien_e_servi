import socket
# Sockets permitem a comunicação entre processos - na mesma máquina ou não -
# através da criação de conexões entre os processos.

# Define o endereço como a própria máquina e a portas como: 3210
IP = '127.0.0.1'
Server_Port = 3216

# Cria o socket padrão: IPv4 - UDP
# socket.AF_INET -> ipv4 - Internet Protocol version 4
# SOCK_DGRAM -> UDP
# Gerente de Contextos
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    print('Cliente Inicializado ...\n\n')

    # Conecta ao servidor
    sock.connect((IP, Server_Port))

    print('Cliente Conectado ao servidor ...\n\n')

    while True:
        mensagem = input('Digite um valor [digite "sair" para encerrar]:')

        # Codifica a string para enviar ao cliente
        mensagem = mensagem.encode()

        # Envia a mensagem para o Servidor
        sock.sendall(mensagem)

        print(f'Mensagem: {mensagem.decode()} \n  - enviada para IP {IP} : Porta {Server_Port}\n')

        if mensagem.decode() == 'sair':
            break

        # Aguarda/Recebe a mensagem de resposta do servidor
        data = sock.recv(1024)

        # decodifica a mensagem retornando apenas a string referente à mensagem
        mensagem = data.decode()

        print(f'Mensagem: {mensagem} \n  - recebida do IP {IP} : Porta {Server_Port}\n')


print('\nCliente Finalizado.\n')
