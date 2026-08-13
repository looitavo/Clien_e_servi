import socket

# Define o endereço como a própria máquina ()
# e a portas como: 3210 - Servidor / 3211 - Cliente
TCP_IP = '127.0.0.1'
TCP_PORT = 3216

# Cria o socket padrão: IPv4 - UDP
# socket.AF_INET -> ipv4 - Internet Protocol version 4
# SOCK_STREAM -> TCP
# Gerente de contextos do socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    # Solicita/Reserva a porta no SO
    sock.bind((TCP_IP, TCP_PORT))

    # Responde aos pacotes que chegarem à porta
    sock.listen()

    print('Servidor Inicializado ...\n\n')

    #Aceita uma conexão
    # conn - objeto de conexão
    # addr - e o endereço do cliente
    conn, addr = sock.accept()

    # Gerente de contextos da conexão
    with conn:

        print(f'Servidor conectado por>: {addr}')

        while True:
            # recebe até 1024 bytes
            data = conn.recv(1024)

            # decodifica a mensagem retornando apenas a string referente à mensagem
            mensagem = data.decode()

            if mensagem == 'sair':
                break

            print(f'Mensagem: {mensagem} \n  - recebida do IP {addr[0]} : Porta {addr[1]}\n')

            # Inverte a string da mensagem
            mensagem = mensagem[::-1]

            # Codifica a string para enviar ao cliente
            mensagem = mensagem.encode()

            # Retorna a mensagem ao cliente
            conn.sendall(mensagem)

            print(f'Mensagem: {mensagem.decode()} \n  - enviada para IP {addr[0]} : Porta {addr[1]}\n')


print('\nServidor Finalizado.\n')
