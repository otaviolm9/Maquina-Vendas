import asyncio
import websockets
import requests
import sys

SERVIDOR_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/maquina"

async def escutar_servidor(websocket):
    """
    Fica escutando o servidor em segundo plano via WebSocket.
    Se o servidor mandar 'LIBERAR_PRODUTO', a máquina simula a entrega física.
    """
    try:
        async for mensagem in websocket:
            if mensagem == "LIBERAR_PRODUTO":
                print("\n" + "="*50)
                print("🟢 [MÁQUINA] SINAL RECEBIDO: PAGAMENTO APROVADO!")
                print("⚙️ [MOTOR] Acionando motor de liberação do produto... 🕒")
                await asyncio.sleep(2.5)  # Simula o tempo do motor girando fisicamente
                print("📦 [SUCESSO] Produto liberado na gaveta! Obrigado.")
                print("="*50 + "\n")
                
                # Reseta o menu visual na tela do usuário
                print("=== VENDING MACHINE (VALOR FIXO: R$ 5,00) ===")
                print("1 - Comprar Produto")
                print("Digite 1 para iniciar ou 'sair': ", end="", flush=True)
    except websockets.exceptions.ConnectionClosed:
        print("\n[MÁQUINA] Erro: Conexão WebSocket com o servidor fechada.")

async def fluxo_maquina():
    print("[MÁQUINA] Tentando conectar ao servidor...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("[MÁQUINA] Conectado ao servidor via WebSocket com sucesso!")
            
            # Cria a tarefa em segundo plano para ficar ouvindo o servidor
            asyncio.create_task(escutar_servidor(websocket))
            
            while True:
                print("\n=== VENDING MACHINE (VALOR FIXO: R$ 5,00) ===")
                print("1 - Comprar Produto")
                opcao = input("Digite 1 para iniciar ou 'sair': ")
                
                if opcao.lower() == 'sair':
                    print("[MÁQUINA] Desligando simulador...")
                    break
                if opcao != '1':
                    print("[MÁQUINA] Opção inválida.")
                    continue
                    
                print("\n[MÁQUINA] Solicitando código Pix ao servidor backend...")
                try:
                    # Faz a requisição HTTP para criar o Pix
                    resposta = requests.get(f"{SERVIDOR_URL}/pedir-pix").json()
                    pix_code = resposta["pix_code"]
                    pix_id = resposta["pix_id"]
                    
                    print("\n" + "-"*40)
                    print("📱 [TELA DA MÁQUINA] PIX COPIA E COLA GENERADO:")
                    print(f"\n{pix_code}\n")
                    print(f"ID desta transação para o teste: {pix_id}")
                    print("-"*40)
                    print("[MÁQUINA] Aguardando confirmação do banco... Pode simular o pagamento agora.\n")
                    
                    # Pequena pausa para sincronizar o terminal
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"[MÁQUINA] Erro ao comunicar com a API do servidor: {e}")
                    
    except Exception as e:
        print(f"[MÁQUINA] Não foi possível conectar ao servidor: {e}")
        print("[MÁQUINA] Certifique-se de que o 'servidor.py' está rodando primeiro.")

if __name__ == "__main__":
    # Inicia o loop de eventos assíncronos do simulador da máquina
    try:
        asyncio.run(fluxo_maquina())
    except KeyboardInterrupt:
        print("\n[MÁQUINA] Encerrada pelo usuário.")
