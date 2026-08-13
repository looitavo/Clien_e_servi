import socket # Permite a comunicação entre processos - na mesma máquina ou não -, atravéz da conexão entre eles

IP = '192.168.7.27' # Define o endereço como a própria máquina
Server_Port = 7654 # Define a porta como 7654

# Cria o socket padrão: IPv4 - UDP
# socket.AF_INET -> ipv4 - Internet Protocol version 4
# SOCK_DGRAM -> UDP
# Gerente de Contextos

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

    print('Cliente Inicializado ...\n\n') # Mensagem que mostra a inicialização do programa
    sock.connect((IP, Server_Port)) # Conecta a máquina ao servidor
    print('Cliente Conectado ao servidor ...\n\n') # Mensagem que mostra que a máquina já está conectada ao servidor
    
    cnt = 0

    while True: 
        mensagem = input('Digite um valor [digite "sair" para encerrar]: ') 
        
        if mensagem == 'sair': 
            break

        sock.sendall(mensagem.encode()) 
        cnt += 1 # Conta que enviamos um número
        
        print(f'Mensagem: {mensagem} \n  - enviada para IP {IP} : Porta {Server_Port}\n') 

        # CORREÇÃO 2: Só espera a resposta do servidor se já tiver enviado os 2 números!
        if cnt == 2:
            print("Aguardando o resultado da soma do servidor...")
            data = sock.recv(1024) 
            resultado = data.decode() 

            print(f'Resultado da Soma: {resultado} \n  - recebido do IP {IP} : Porta {Server_Port}\n') 
            break # Encerra o cliente após receber o resultado final
