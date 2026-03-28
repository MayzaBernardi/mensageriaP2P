import socket 
import threading 
import json
import os 
from datetime import datetime  

    
# -----------------------------
# Imports da biblioteca Rich
# -----------------------------
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

class ChatNode:
    
    def __init__(self, nome, ip, porta, vizinhos):

        self.nome = nome
        self.ip = ip
        self.porta = porta
        self.vizinhos = vizinhos
        self.historico = {} 
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, porta))

        print(f"{self.nome} rodando em {ip}:{porta}");

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
        });

    # -----------------------------
    # Enviar
    # -----------------------------

    def enviar(self, destino, texto, encaminhado=False):
        ip, porta = self.vizinhos[destino]
        msg = self.criar_mensagem(destino, texto, encaminhado)
        self.socket.sendto(msg.encode(), (ip, porta));

    # -----------------------------
    # Receber
    # -----------------------------
    def ouvir(self):
        while True:
            try:
                dados, _ = self.socket.recvfrom(1024)
                msg = json.loads(dados.decode())
                destino = msg["destino"]

                if destino != self.nome:
                    continue

                remetente = msg["remetente"]["nome"]
                conteudo = msg["conteudo"]

                if remetente not in self.historico:
                    self.historico[remetente] = []

                self.historico[remetente].append(msg)

                console.print(f"\n[bold magenta]🔔 Nova mensagem de {remetente}![/bold magenta] [italic](Vá em Ver Conversas para ler)[/italic]")
                
            except ConnectionResetError:
                pass
            except Exception as e:
                console.print(f"\n[bold red][Erro na escuta][/bold red] {e}");

    # -----------------------------
    # Mostrar conversas
    # -----------------------------

    def ver_conversas(self, encaminhando=False):
        limpar_tela()
        
        if not self.historico:
            console.print(Panel("[yellow]Nenhuma mensagem recebida ou enviada ainda.[/yellow]", title="Suas Conversas", border_style="yellow"))
            Prompt.ask("\n[bold yellow]Pressione ENTER para voltar...[/bold yellow]")
            return

        for contato in self.historico:
            tabela = Table(title=f"Conversa com {contato}", show_header=True, header_style="bold magenta", border_style="blue")
            tabela.add_column("ID", justify="center", style="cyan", no_wrap=True)
            tabela.add_column("Status", justify="center")
            tabela.add_column("Mensagem", style="green")
            tabela.add_column("Hora", style="dim")

            for i, msg in enumerate(self.historico[contato]):
                status = "➡️ Recebido"
                hora = msg["timestamp"][11:16] 
                
                tabela.add_row(str(i), status, msg['conteudo'], hora)

            console.print(tabela)
            print("")

        if not encaminhando:
            Prompt.ask("\n[bold yellow]Pressione ENTER para voltar ao menu...[/bold yellow]")
        else:
            Prompt.ask("\n[bold yellow]Pressione ENTER para escolher o contato...[/bold yellow]");

    # -----------------------------
    # Encaminhar mensagem 
    # -----------------------------
    def encaminhar(self):
        
        self.ver_conversas(encaminhando=True)

        if not self.historico:
            return

        contato = Prompt.ask("\n[bold yellow]De qual contato?[/bold yellow]")
        if contato not in self.historico:
            console.print("[bold red]Contato inválido[/bold red]")
            Prompt.ask("Pressione ENTER para voltar...")
            return

        indice_str = Prompt.ask("[bold yellow]Número (ID) da mensagem[/bold yellow]")
        try:
            indice = int(indice_str)
            msg = self.historico[contato][indice]
        except:
            console.print("[bold red]Mensagem inválida[/bold red]")
            Prompt.ask("Pressione ENTER para voltar...")
            return

        console.print("\n[bold green]Para quem deseja encaminhar?[/bold green]")
        for v in self.vizinhos:
            console.print(f" - [bold cyan]{v}[/bold cyan]")
            
        destino = Prompt.ask("\n[bold yellow]Destino[/bold yellow]")
        if destino not in self.vizinhos:
            console.print("[bold red]Destino inválido[/bold red]")
            Prompt.ask("Pressione ENTER para voltar...")
            return

        remetente_original = msg["remetente"]["nome"]
        conteudo_original = msg["conteudo"]

        novo_texto = f"Encaminhado por {self.nome}: [{remetente_original}] {conteudo_original}"
        self.enviar(destino, novo_texto, True)
        Prompt.ask(f"[bold green]Mensagem encaminhada com sucesso para {destino}![/bold green] Pressione ENTER...");

    # -----------------------------
    # Menu
    # -----------------------------
    def menu(self):
        while True:
            limpar_tela()
            
            menu_texto = (
                " ✉️ 1 - Enviar mensagem\n"
                " 💬 2 - Ver conversas\n"
                " ↪️ 3 - Encaminhar mensagem\n"
                " ❌ 4 - Sair"
            )
            
            console.print(Panel(menu_texto, title=f"[bold cyan]Bem-vindo(a), {self.nome}![/bold cyan]", border_style="cyan", expand=False))

            op = Prompt.ask("\n[bold yellow]Escolha uma opção[/bold yellow]", choices=["1", "2", "3", "4"], show_choices=False)

            if op == "1":
                limpar_tela()
                console.print(Panel("Escolha um destinatário abaixo:", title="[bold green]Enviar Mensagem[/bold green]", border_style="green"))
                
                for v in self.vizinhos:
                    console.print(f" - [bold cyan]{v}[/bold cyan]")

                destino = Prompt.ask("\n[bold yellow]Destino[/bold yellow]")
                if destino not in self.vizinhos:
                    Prompt.ask(f"[bold red]Destino inválido![/bold red] Pressione ENTER...")
                    continue

                texto = Prompt.ask("[bold yellow]Mensagem[/bold yellow]")
                self.enviar(destino, texto)
                Prompt.ask(f"[bold green]Mensagem enviada com sucesso![/bold green] Pressione ENTER para voltar...")

            elif op == "2":
                self.ver_conversas()

            elif op == "3":
                self.encaminhar()

            elif op == "4":
                console.print("[bold red]Encerrando o sistema P2P... Até logo![/bold red]")
                break


# -----------------------------
# Configuração inicial
# -----------------------------
limpar_tela()
console.print(Panel("[bold magenta]INICIALIZANDO NÓ P2P[/bold magenta]", expand=False))

nome = Prompt.ask("[bold cyan]Quem é você?[/bold cyan]")
porta_str = Prompt.ask("[bold cyan]Em que porta você quer rodar?[/bold cyan]")
porta = int(porta_str)
ip = "127.0.0.1"

vizinhos = {
    "Michelle Obama": ("127.0.0.1", 3333),
    "Marie Curie": ("127.0.0.1", 4444),
    "Frida Kahlo": ("127.0.0.1", 5555),
}

# caso a pessoa digite um nome que não está na lista
if nome in vizinhos:
    vizinhos.pop(nome)

node = ChatNode(nome, ip, porta, vizinhos)

# thread para ouvir
thread = threading.Thread(target=node.ouvir)
thread.daemon = True
thread.start()

# iniciar menu
node.menu()