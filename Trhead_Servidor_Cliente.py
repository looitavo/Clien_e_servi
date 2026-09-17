import socket
import threading
import time

# Definimos exatamente a mesma porta para ambas as máquinas
PORTA_PADRAO = 65432  

def rodar_servidor():
    """Thread do Servidor: Escuta conexões vindas do outro IP na porta 65432."""
    print(f"[SERVIDOR] Ativo e escutando na porta {PORTA_PADRAO}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind(('0.0.0.0', PORTA_PADRAO))
        servidor.listen(1) # Aceita apenas 1 cliente (sem sub-threads)
        
        conexao, endereco = servidor.accept()
        with conexao:
            print(f"\n[SERVIDOR] O outro computador se conectou! Origem: {endereco}\n> ", end="")
            while True:
                dados = conexao.recv(1024)
                if not dados:
                    print("\n[SERVIDOR] Conexão encerrada pelo outro computador.")
                    break
                print(f"\n[MENSAGEM RECEBIDA]: {dados.decode()}\n> ", end="")

def rodar_cliente(ip_destino):
    """Thread do Cliente: Tenta conectar no outro IP na porta 65432."""
    time.sleep(2) # Pequena pausa para o servidor local ligar primeiro
    print(f"[CLIENTE] Tentando conectar em {ip_destino}:{PORTA_PADRAO}...")
    
    # Loop de tentativas caso o outro computador ainda não tenha aberto o programa
    while True:
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((ip_destino, PORTA_PADRAO))
            print("[CLIENTE] Conectado com sucesso ao outro computador!")
            break
        except Exception:
            time.sleep(2) # Tenta novamente a cada 2 segundos

    with cliente:
        print("--- Chat Ativo! Digite e pressione Enter (ou 'sair') ---")
        while True:
            mensagem = input("> ")
            if mensagem.strip().lower() == 'sair':
                break
            if mensagem.strip():
                try:
                    cliente.sendall(mensagem.encode())
                except:
                    print("[CLIENTE] Conexão perdida ao enviar.")
                    break

if __name__ == "__main__":
    # Cada máquina apenas digita o IP da OUTRA máquina
    ip_remoto = input("Digite o IP do OUTRO computador: ").strip()
    
    # Criamos as duas threads paralelas usando a mesma porta lógica
    thread_servidor = threading.Thread(target=rodar_servidor, daemon=True)
    thread_cliente = threading.Thread(target=rodar_cliente, args=(ip_remoto,))
    
    thread_servidor.start()
    thread_cliente.start()
    
    thread_cliente.join()
    print("[PROGRAMA] Chat encerrado.")

    print("[MÁQUINA A] Encerrada.")
