import asyncio
import websockets
import requests

SERVIDOR_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/maquina"

async def escutar_servidor(websocket):
    """Fica escutando o servidor em segundo plano para ver se o pagamento foi aprovado."""
    try:
        async for mensagem in websocket:
            if mensagem == "LIBERAR_PRODUTO":
                print("\n" + "="*40)
                print("[MÁQUINA - HARDWARE] 🟢 SINAL RECEBIDO: PAGAMENTO CONFIRMADO!")
                print("[MÁQUINA - MOTOR] Girando a mola/motor... 🕒")
                await asyncio.sleep(2) # Simula o tempo do motor girando
                print("[MÁQUINA - SUCESSO] Produto entregue! Obrigado pela compra.")
                print("="*40 + "\n")
                print("Escolha o produto:\n1 - Refrigerante (R$ 5,00)\n2 - Salgadinho (R$ 7,00)\nDigite o número: ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("[MÁQUINA] Conexão com o servidor perdida.")

async def fluxo_maquina():
    # Abre a conexão em tempo real (WebSocket) com o servidor
    async with websockets.connect(WS_URL) as websocket:
        print("[MÁQUINA] Conectado ao servidor com sucesso!")
        
        # Inicia a tarefa que fica ouvindo o servidor em segundo plano
        asyncio.create_task(escutar_servidor(websocket))
        
        while True:
            print("\n=== VENDING MACHINE SIMULATOR ===")
            print("1 - Refrigerante (R$ 5,00)")
            print("2 - Salgadinho (R$ 7,00)")
            opcao = input("Digite o número do produto desejado (ou 'sair'): ")
            
            if opcao.lower() == 'sair':
                break
            if opcao not in ['1', '2']:
                print("Opção inválida.")
                continue
                
            # 1. Solicita o Pix para o backend via HTTP comum
            print(f"[MÁQUINA] Solicitando Pix para o produto {opcao} ao servidor...")
            try:
                resposta = requests.get(f"{SERVIDOR_URL}/pedir-pix/{opcao}").json()
                pix_copia_e_cola = resposta["pix_code"]
                pix_id = resposta["pix_id"]
                
                print("\n" + "-"*30)
                print(f"👉 [TELA DA MÁQUINA] Copie o código abaixo para pagar:")
                print(f"\n{pix_copia_e_cola}\n")
                print(f"ID do seu Pix para simulação: {pix_id}")
                print("-"*30)
                print("[MÁQUINA] Aguardando confirmação de pagamento do banco...\n")
                
                # Deixa um pequeno delay para não atropelar o input do terminal
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"[MÁQUINA] Erro ao conectar ao servidor: {e}")

if __name__ == "__main__":
    # Inicia o loop assíncrono da máquina
    asyncio.run(fluxo_maquina())
