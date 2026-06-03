import asyncio
import websockets
import requests
from aioconsole import ainput  # Importa o input que não trava o WebSocket

SERVIDOR_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/maquina"

async def escutar_servidor(websocket):
    """
    Fica escutando o servidor em segundo plano via WebSocket.
    """
    try:
        async for mensagem in websocket:
            if mensagem == "LIBERAR_PRODUTO":
                print("\n" + "="*50)
                print("🟢 [MÁQUINA] SINAL RECEBIDO: PAGAMENTO APROVADO!")
                print("⚙️ [MOTOR] Acionando motor de liberação do produto... 🕒")
                await asyncio.sleep(2.5)
                print("📦 [SUCESSO] Produto liberado na gaveta! Obrigado.")
                print("="*50 + "\n")
                
                print("=== VENDING MACHINE (VALOR FIXO: R$ 5,00) ===")
                print("1 - Comprar Produto")
                print("Digite 1 para iniciar ou 'sair': ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\n[MÁQUINA] Erro: Conexão WebSocket com o servidor fechada.")

async def fluxo_maquina():
    print("[MÁQUINA] Tentando conectar ao servidor...")
    # Adicionamos ping_interval=None e ping_timeout=None aqui também para garantir
    try:
        async with websockets.connect(WS_URL, ping_interval=None, ping_timeout=None) as websocket:
            print("[MÁQUINA] Conectado ao servidor via WebSocket com sucesso!")
            
            # Inicia a tarefa de escuta em segundo plano
            asyncio.create_task(escutar_servidor(websocket))
            
            while True:
                print("\n=== VENDING MACHINE (VALOR FIXO: R$ 5,00) ===")
                print("1 - Comprar Produto")
                
                # Usamos o ainput() no lugar do input() normal
                opcao = await ainput("Digite 1 para iniciar ou 'sair': ")
                
                if opcao.lower() == 'sair':
                    print("[MÁQUINA] Desligando simulador...")
                    break
                if opcao != '1':
                    print("[MÁQUINA] Opção inválida.")
                    continue
                    
                print("\n[MÁQUINA] Solicitando código Pix ao servidor backend...")
                try:
                    resposta = requests.get(f"{SERVIDOR_URL}/pedir-pix").json()
                    pix_code = resposta["pix_code"]
                    pix_id = resposta["pix_id"]
                    
                    print("\n" + "-"*40)
                    print("📱 [TELA DA MÁQUINA] PIX COPIA E COLA GERADO:")
                    print(f"\n{pix_code}\n")
                    print(f"ID desta transação para o teste: {pix_id}")
                    print("-"*40)
                    print("[MÁQUINA] Aguardando confirmação do banco...\n")
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"[MÁQUINA] Erro ao comunicar com a API do servidor: {e}")
                    
    except Exception as e:
        print(f"[MÁQUINA] Não foi possível conectar ao servidor: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(fluxo_maquina())
    except KeyboardInterrupt:
        print("\n[MÁQUINA] Encerrada pelo usuário.")
