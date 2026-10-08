import socket
import subprocess
import sys
from threading import Thread

if sys.platform == "win32" and "--externo" not in sys.argv:
    subprocess.Popen(
        [sys.executable, __file__, "--externo"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    sys.exit()

# Solicita o nome do usuário ao iniciar
meu_nome = input("Digite seu nome de usuário: ").strip()
while not meu_nome:
    meu_nome = input("O nome não pode ser vazio. Digite seu nome: ").strip()

# conexoes = { "ip:porta": {"socket": sock, "nome": nome_remoto} }
conexoes = {}
destino = None  # chave "ip:porta" de com quem estou falando agora


def receber(sock, endereco_remoto):
    global destino
    try:
        with sock.makefile("r", encoding="utf-8") as arq:
            # A primeira linha recebida da conexão é o nome do usuário remoto
            nome_remoto = arq.readline().strip()
            if not nome_remoto:
                nome_remoto = endereco_remoto

            if endereco_remoto in conexoes:
                conexoes[endereco_remoto]["nome"] = nome_remoto

            print(f"\nConectado com: {nome_remoto} ({endereco_remoto})")

            for linha in arq:
                print(f"\n[{nome_remoto}] {linha.rstrip()}")
    except OSError:
        pass

    info = conexoes.pop(endereco_remoto, None)
    nome_desconectado = info["nome"] if info and info.get("nome") else endereco_remoto
    if destino == endereco_remoto:
        destino = None
    print(f"\n{nome_desconectado} ({endereco_remoto}) desconectou.")


def adicionar(sock, endereco_remoto, falar):
    global destino
    conexoes[endereco_remoto] = {"socket": sock, "nome": "Aguardando nome..."}
    if falar:
        destino = endereco_remoto

    # Envia nosso nome de usuário assim que a conexão é estabelecida
    try:
        sock.sendall((meu_nome + "\n").encode("utf-8"))
    except OSError:
        pass

    Thread(target=receber, args=(sock, endereco_remoto), daemon=True).start()


def aceitar(srv):
    while True:
        try:
            conn, addr = srv.accept()
        except OSError:
            return
        adicionar(conn, f"{addr[0]}:{addr[1]}", falar=destino is None)


with socket.socket() as srv:
    srv.bind(("0.0.0.0", 0))
    srv.listen()
    porta = srv.getsockname()[1]
    Thread(target=aceitar, args=(srv,), daemon=True).start()

    print(f"\nUsuário: {meu_nome}")
    print(f"Sua porta: {porta}")
    print("----------------------------------------")
    print("Comandos disponíveis:")
    print("  conectar IP:PORTA  -> Conecta a um novo peer")
    print("  conexoes          -> Lista todas as conexões ativas com seus números")
    print("  falar <numero>    -> Troca a conversa para o peer correspondente ao número")
    print('  sair              -> Encerra a conversa / programa')
    print("----------------------------------------\n")

    while True:
        try:
            texto = input(">: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if texto == "sair":
            break

        # Comando: conexoes
        if texto == "conexoes":
            if not conexoes:
                print("Nenhuma conexão ativa no momento.")
            else:
                print("\n--- Conexões Ativas ---")
                lista_chaves = list(conexoes.keys())
                for idx, chave in enumerate(lista_chaves, start=1):
                    info = conexoes[chave]
                    marcador = " (conversando agora)" if chave == destino else ""
                    print(f" [{idx}] {info['nome']} ({chave}){marcador}")
                print("-----------------------\n")

        # Comando: falar <numero>
        elif texto.startswith("falar"):
            partes = texto.split()
            if len(partes) < 2 or not partes[1].isdigit():
                print("Use: falar <numero_da_conexao> (ex: falar 1)")
                continue

            num = int(partes[1])
            lista_chaves = list(conexoes.keys())

            if 1 <= num <= len(lista_chaves):
                destino = lista_chaves[num - 1]
                nome_destino = conexoes[destino]["nome"]
                print(f"Agora você está falando com: {nome_destino} ({destino})")
            else:
                print(f"Número inválido. Use 'conexoes' para ver os números disponíveis (1 a {len(lista_chaves)}).")

        # Comando: conectar IP:PORTA
        elif texto.startswith("conectar"):
            ip, _, p = texto[8:].strip().partition(":")
            endereco_remoto = f"{ip}:{p}"
            if not p:
                print("Use: conectar IP:PORTA")
                continue
            if endereco_remoto in conexoes:
                destino = endereco_remoto
                nome_destino = conexoes[destino]["nome"]
                print(f"Já conectado! Agora falando com {nome_destino} ({endereco_remoto})")
            else:
                try:
                    sock = socket.create_connection((ip, int(p)), timeout=5)
                except (OSError, ValueError) as e:
                    print(f"Erro ao conectar: {e}")
                    continue
                sock.settimeout(None)
                adicionar(sock, endereco_remoto, falar=True)
                print(f"Conectando a {endereco_remoto}...")

        # Envio de Mensagem
        elif texto:
            if destino is None or destino not in conexoes:
                print("Ninguém selecionado para conversar. Use 'conexoes' para listar ou 'falar <numero>' para escolher.")
                continue
            
            sock = conexoes[destino]["socket"]
            try:
                sock.sendall((texto + "\n").encode("utf-8"))
                print(f"[{meu_nome}]: {texto}")
            except OSError:
                print("Falha ao enviar mensagem.")