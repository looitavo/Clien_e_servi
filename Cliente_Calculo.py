import socket

# Endereço e porta do servidor
IP = '127.0.0.1'
Server_Port = 3216

# Cria o socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    print('Cliente Inicializado ...\n')

    # Conecta ao servidor
    sock.connect((IP, Server_Port))

    print('Cliente conectado ao servidor!\n')

    while True:

        # Pede uma entrada ao usuário
        mensagem = input('Digite um número ou operador (+, -, *, /) [= para calcular]: ')

        # Envia a mensagem para o servidor
        sock.sendall(mensagem.encode())

        # Se o usuário digitar sair
        if mensagem == 'sair':
            break

        # Recebe a resposta do servidor
        data = sock.recv(1024)

        resposta = data.decode()

        print(f'Calculadora: {resposta}\n')

        # Se digitou =, o servidor terminou a operação
        if mensagem == '=':
            print('Operação finalizada.\n')


print('Cliente Finalizado.')
