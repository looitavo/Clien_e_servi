import os
import secrets
import socket
import subprocess
import sys
from threading import Lock, Thread

if sys.platform == "win32" and "--externo" not in sys.argv:
    subprocess.Popen(
        [sys.executable, __file__, "--externo"],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    sys.exit()

PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_CHAVES = os.path.join(PASTA, "chaves.txt")        # IP + chave dos outros usuários
ARQUIVO_MINHA_CHAVE = os.path.join(PASTA, "minha_chave.txt")  # a chave deste usuário
ALFABETO = "abcdefghijklmnopqrstuvwxyz"
lock_arquivo = Lock()


# ---------- Chave: cada letra do alfabeto é trocada por outra, sem repetir ----------

def gerar_chave():
    """Embaralha as 26 letras uma única vez. Nenhuma letra fica no mesmo lugar."""
    sorteio = secrets.SystemRandom()
    while True:
        letras = list(ALFABETO)
        sorteio.shuffle(letras)
        if all(a != b for a, b in zip(ALFABETO, letras)):
            return "".join(letras)


def chave_para_texto(chave):
    """'qwerty...' -> 'a,q ; b,w ; c,e ; ...'"""
    return " ; ".join(f"{a},{b}" for a, b in zip(ALFABETO, chave))


def texto_para_chave(texto):
    """'a,q ; b,w ; ...' -> 'qwerty...'. Dá ValueError se não for uma chave válida."""
    pares = [p for p in texto.split(";") if p.strip()]
    if len(pares) != 26:
        raise ValueError("a chave precisa ter 26 pares")
    mapa = {}
    for par in pares:
        a, _, b = par.partition(",")
        a, b = a.strip().lower(), b.strip().lower()
        if a not in ALFABETO or b not in ALFABETO or len(a) != 1 or len(b) != 1:
            raise ValueError("par inválido")
        mapa[a] = b
    if sorted(mapa) != list(ALFABETO) or sorted(mapa.values()) != list(ALFABETO):
        raise ValueError("letras repetidas ou faltando")
    return "".join(mapa[a] for a in ALFABETO)


def tabela(origem, destino):
    """Tabela de troca de letras (maiúsculas e minúsculas). Outros caracteres não mudam."""
    return str.maketrans(origem + origem.upper(), destino + destino.upper())


def carregar_ou_criar_chave():
    """O computador possui uma chave permanente única salva em minha_chave.txt."""
    with lock_arquivo:
        if os.path.exists(ARQUIVO_MINHA_CHAVE):
            with open(ARQUIVO_MINHA_CHAVE, encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha:
                        continue
                    partes = linha.split(" | ")
                    try:
                        return texto_para_chave(partes[-1]), False
                    except ValueError:
                        pass
        chave = gerar_chave()
        with open(ARQUIVO_MINHA_CHAVE, "w", encoding="utf-8") as f:
            f.write(f"{chave_para_texto(chave)}\n")
        return chave, True


def carregar_chave_ip(ip):
    """Busca a chave salva para um determinado IP em chaves.txt."""
    with lock_arquivo:
        if os.path.exists(ARQUIVO_CHAVES):
            with open(ARQUIVO_CHAVES, encoding="utf-8") as f:
                for linha in f:
                    partes = linha.rstrip("\n").split(" | ")
                    if len(partes) >= 2 and partes[0] == ip:
                        try:
                            return texto_para_chave(partes[-1])
                        except ValueError:
                            pass
    return None


def salvar_chave(ip, chave):
    """Guarda ou atualiza apenas 'IP | chave' em chaves.txt, mantendo apenas 1 registro por IP."""
    linha_formatada = f"{ip} | {chave_para_texto(chave)}\n"
    with lock_arquivo:
        linhas = []
        encontrado = False
        if os.path.exists(ARQUIVO_CHAVES):
            with open(ARQUIVO_CHAVES, "r", encoding="utf-8") as f:
                for linha in f:
                    partes = linha.rstrip("\n").split(" | ")
                    if len(partes) >= 1 and partes[0] == ip:
                        linhas.append(linha_formatada)
                        encontrado = True
                    else:
                        linhas.append(linha)
        if not encontrado:
            linhas.append(linha_formatada)

        with open(ARQUIVO_CHAVES, "w", encoding="utf-8") as f:
            f.writelines(linhas)


# ---------- Programa ----------

meu_nome = input("Digite seu nome de usuário: ").strip()
while not meu_nome:
    meu_nome = input("O nome não pode ser vazio. Digite seu nome: ").strip()

minha_chave, chave_nova = carregar_ou_criar_chave()
minha_chave_texto = chave_para_texto(minha_chave)
tabela_descriptografar = tabela(minha_chave, ALFABETO)  # desfaz a troca feita com a MINHA chave

conexoes = {}
destino = None  # chave "ip:porta" de quem estou falando agora


def receber(sock, endereco_remoto):
    global destino
    try:
        with sock.makefile("r", encoding="utf-8") as arq:
            # Handshake: 1ª linha = nome do usuário remoto, 2ª linha = chave dele
            nome_remoto = arq.readline().strip()
            if not nome_remoto:
                nome_remoto = endereco_remoto
            texto_chave = arq.readline().strip()

            if endereco_remoto in conexoes:
                conexoes[endereco_remoto]["nome"] = nome_remoto

            chave_remota = None
            try:
                chave_remota = texto_para_chave(texto_chave)
            except ValueError:
                print(f"\n{nome_remoto} ({endereco_remoto}) enviou uma chave inválida. Conexão encerrada.")

            if chave_remota is not None:
                ip_remoto = endereco_remoto.rpartition(":")[0]
                salvar_chave(ip_remoto, chave_remota)

                if endereco_remoto in conexoes:
                    # Atualiza a tabela de envio com a chave remota recebida
                    conexoes[endereco_remoto]["tabela_enviar"] = tabela(ALFABETO, chave_remota)

                print(f"\nConectado com: {nome_remoto} ({endereco_remoto})")
                print("Chave salva em chaves.txt")

                for linha in arq:
                    # Mensagem chega criptografada com a MINHA chave; descriptografo com ela
                    print(f"\n[{nome_remoto}] {linha.rstrip().translate(tabela_descriptografar)}")
    except OSError:
        pass

    info = conexoes.pop(endereco_remoto, None)
    nome_desconectado = info["nome"] if info and info.get("nome") else endereco_remoto
    if destino == endereco_remoto:
        destino = None
    sock.close()
    print(f"\n{nome_desconectado} ({endereco_remoto}) desconectou.")


def adicionar(sock, endereco_remoto, falar):
    global destino
    ip_remoto = endereco_remoto.rpartition(":")[0]
    
    # Se já existir uma chave salva para esse IP em chaves.txt, já carrega a tabela de envio imediatamente
    chave_salva = carregar_chave_ip(ip_remoto)
    tabela_envio = tabela(ALFABETO, chave_salva) if chave_salva else None

    conexoes[endereco_remoto] = {
        "socket": sock,
        "nome": "Aguardando nome...",
        "tabela_enviar": tabela_envio
    }
    if falar:
        destino = endereco_remoto

    # Envia nosso nome de usuário e nossa chave assim que a conexão é estabelecida
    try:
        sock.sendall((meu_nome + "\n" + minha_chave_texto + "\n").encode("utf-8"))
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
    print("Sua chave: " + ("criada agora e salva em minha_chave.txt" if chave_nova else "carregada de minha_chave.txt"))
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

            tab_enviar = conexoes[destino].get("tabela_enviar")
            if tab_enviar is None:
                print("Ainda recebendo a chave desse peer. Tente de novo em instantes.")
                continue

            sock = conexoes[destino]["socket"]
            try:
                # Criptografo com a chave de QUEM VAI RECEBER
                sock.sendall((texto.translate(tab_enviar) + "\n").encode("utf-8"))
                print(f"[{meu_nome}]: {texto}")
            except OSError:
                print("Falha ao enviar mensagem.")