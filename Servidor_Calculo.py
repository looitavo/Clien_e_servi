import socket
# Endereço e porta do servidor
TCP_IP = '127.0.0.1'
TCP_PORT = 3216
# Cria o socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Reserva a porta
    sock.bind((TCP_IP, TCP_PORT))
    # Coloca o servidor para esperar conexões
    sock.listen()
    print('Servidor Inicializado ...\n')
    # Aceita uma conexão
    conn, addr = sock.accept()

    with conn:
        print(f'Servidor conectado por: {addr}\n')
        # Variável que vai guardar a operação
        operacao = ''

        while True:
            # Recebe a mensagem do cliente
            data = conn.recv(1024)
            # Se não receber nada, encerra
            if not data:
                break

            mensagem = data.decode()
            print(f'Mensagem recebida: {mensagem}')

            # Se o cliente quiser sair
            if mensagem == 'sair':
                break

            # Se receber "=" significa que a operação terminou
            if mensagem == '=':
                try:
                    # Calcula a expressão
                    resultado = eval(operacao)

                    # Envia o resultado para o cliente
                    resposta = str(resultado)

                    conn.sendall(resposta.encode())
                    print(f'Resultado: {resultado}')

                    # Limpa a operação para poder fazer outra
                    operacao = ''

                except:
                    # Caso a expressão esteja inválida
                    resposta = 'Operação inválida'

                    conn.sendall(resposta.encode())

                    operacao = ''
            else:
                # Adiciona o número ou operador à operação
                operacao += mensagem

                # Mostra a operação atual
                print(f'Operação atual: {operacao}')

                # Devolve a operação para o cliente
                conn.sendall(operacao.encode())

print('\nServidor Finalizado.')

