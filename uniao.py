import subprocess
import sys
import os
from threading import Thread

pasta = os.path.dirname(os.path.abspath(__file__))
peer = os.path.join(pasta, "peer.py")
QUANTIDADE = 1


def abrir(numero):
    if sys.platform == "win32":
        # Comando para Windows
        processo = subprocess.Popen(
            [sys.executable, peer, "--externo"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        
    else:
        # Comando para Linux (Ubuntu)
        env = dict(os.environ)
        env.pop("LD_LIBRARY_PATH", None)
        env.pop("LD_PRELOAD", None)
        
        processo = subprocess.Popen(
            ["xterm", "-e", sys.executable, peer],
            env=env,
        )

    processo.wait()
    print(f"Peer {numero} finalizado.")


threads = [Thread(target=abrir, args=(n,)) for n in range(1, QUANTIDADE + 1)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print("Todos os peers finalizados.")