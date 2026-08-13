import socket # Permite a comunicação entre processos - na mesma máquina ou não -, atravéz da conexão entre eles

TCP_IP = '0.0.0.0' # Define o endereço como a própria máquina ()
TCP_PORT = 7654 # e a portas como: 3210 - Servidor / 3211 - Cliente

# Cria o socket padrão: IPv4 - UDP
# socket.AF_INET -> ipv4 - Internet Protocol version 4
# SOCK_STREAM -> TCP
# Gerente de contextos do socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    sock.bind((TCP_IP, TCP_PORT)) # Solicita/Reserva a porta no SO
    sock.listen() # Responde aos pacotes que chegarem à porta

    print('Servidor Inicializado ...\n\n') #Inicialização do servidor

    #Aceita uma conexão
    # conn - objeto de conexão
    # addr - é o endereço do cliente
    
    conn, addr = sock.accept()

    # Gerente de contextos da conexão
    with conn:

        print(f'Servidor conectado por>: {addr}') # Printa a conexão com o cliente
        lista_numeros = []

        while True:
            # recebe até 1024 bytes
            data = conn.recv(1024)
            
            if not data: 
                print("Cliente desconectou de forma limpa.")
                break # Sai do loop do cliente atual e finaliza o servidor


            # decodifica a mensagem retornando apenas a string referente à mensagem
            numero = data.decode()

            if numero == 'sair':
                break
            
            lista_numeros.append(numero)

            print(f'Mensagem: {numero} \n  - recebida do IP {addr[0]} : Porta {addr[1]}\n')
            
            if len(lista_numeros) == 2:
                soma = int(lista_numeros[0]) + int(lista_numeros[1])
                soma = str(soma)
                conn.sendall(soma.encode())
                print(f'Mensagem: {soma} \n  - enviada para IP {addr[0]} : Porta {addr[1]}\n')

print('\nServidor Finalizado.\n')