import socket
import threading
import json
from datetime import datetime


class ChatNode:
    def __init__(self, nome, ip, porta, vizinhos):
        self.nome = nome
        self.ip = ip
        self.porta = porta
        self.vizinhos = vizinhos
        self.historico = {} 

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, porta))

        print(f"{self.nome} rodando em {ip}:{porta}")

    # -----------------------------
    # Criar mensagem
    # -----------------------------
    def criar_mensagem(self, destino, texto, encaminhado=False):
        return json.dumps({
            "timestamp": str(datetime.now()),
            "remetente": {
                "nome": self.nome,
                "ip": self.ip,
                "porta": self.porta
            },
            "destino": destino,
            "conteudo": texto,
            "encaminhado": encaminhado
        })

    # -----------------------------
    # Enviar
    # -----------------------------
    def enviar(self, destino, texto, encaminhado=False):
        ip, porta = self.vizinhos[destino]
        msg = self.criar_mensagem(destino, texto, encaminhado)
        self.socket.sendto(msg.encode(), (ip, porta))

    # -----------------------------
    # Receber
    # -----------------------------
    def ouvir(self):
        while True:
            dados, _ = self.socket.recvfrom(1024)
            msg = json.loads(dados.decode())
            destino = msg["destino"]

            # valida destinatário final
            if destino != self.nome:
                continue

            remetente = msg["remetente"]["nome"]
            conteudo = msg["conteudo"]

            # salvar no histórico
            if remetente not in self.historico:
                self.historico[remetente] = []

            self.historico[remetente].append(msg)

            print(f"\n[{remetente}] -> {conteudo}")

    # -----------------------------
    # Mostrar conversas
    # -----------------------------
    def ver_conversas(self):
        for contato in self.historico:
            print(f"\n--- Conversa com {contato} ---")
            for i, msg in enumerate(self.historico[contato]):
                print(f"{i} - {msg['conteudo']}")

    # -----------------------------
    # Encaminhar mensagem específica
    # -----------------------------
    def encaminhar(self):
        self.ver_conversas()

        contato = input("\nDe qual contato? ")
        if contato not in self.historico:
            print("Contato inválido")
            return

        indice = int(input("Número da mensagem: "))
        try:
            msg = self.historico[contato][indice]
        except:
            print("Mensagem inválida")
            return

        destino = input("Encaminhar para: ")
        if destino not in self.vizinhos:
            print("Destino inválido")
            return

        remetente_original = msg["remetente"]["nome"]
        conteudo_original = msg["conteudo"]

        novo_texto = f"Encaminhado por {self.nome}: [{remetente_original}] {conteudo_original}"
        self.enviar(destino, novo_texto, True)

    # -----------------------------
    # Menu
    # -----------------------------
    def menu(self):
        while True:
            print("\n--- MENU ---")
            print("1 - Enviar mensagem")
            print("2 - Ver conversas")
            print("3 - Encaminhar mensagem")
            print("4 - Sair")

            op = input("Escolha: ")

            if op == "1":
                print("\nPara quem você quer enviar?")
                for v in self.vizinhos:
                    print("-", v)

                destino = input("Destino: ")
                if destino not in self.vizinhos:
                    print("Destino inválido")
                    continue

                texto = input("Mensagem: ")
                self.enviar(destino, texto)

            elif op == "2":
                self.ver_conversas()

            elif op == "3":
                self.encaminhar()

            elif op == "4":
                break


# -----------------------------
# Configuração
# -----------------------------
nome = input("Quem é você? ")
porta = int(input("Em que porta você quer rodar? "))
ip = "127.0.0.1"

vizinhos = {
    "Michelle Obama": ("127.0.0.1", 3333),
    "Marie Curie": ("127.0.0.1", 4444),
    "Frida Kahlo": ("127.0.0.1", 5555),
}

vizinhos.pop(nome)

node = ChatNode(nome, ip, porta, vizinhos)

# thread para ouvir
thread = threading.Thread(target=node.ouvir)
thread.daemon = True
thread.start()

# iniciar menu
node.menu()