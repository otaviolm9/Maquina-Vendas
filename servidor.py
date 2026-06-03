from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
import requests
import uuid

app = FastAPI()

# -----------------------------------------------------------------
# GERENCIADOR DE CONEXÕES IOT (WEBSOCKET)
# -----------------------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connection: WebSocket = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection = websocket

    def disconnect(self):
        self.active_connection = None

    async def send_message(self, message: str):
        if self.active_connection:
            await self.active_connection.send_text(message)

manager = ConnectionManager()

# CONFIGURAÇÃO DE VALOR FIXO
VALOR_FIXO = 5.00
# Substitua pelo seu Token de Teste do Mercado Pago se for usar o Ngrok real
ACCESS_TOKEN = "TEST-MERCADO-PAGO-TOKEN-TEMPLATE" 

# -----------------------------------------------------------------
# ROTAS HTTP (API)
# -----------------------------------------------------------------

@app.get("/pedir-pix")
async def pedir_pix():
    """
    Simula a criação de um Pix de valor fixo no Mercado Pago.
    """
    print(f"\n[API] Recebida solicitação de Pix de valor fixo: R$ {VALOR_FIXO}")
    
    # Geramos um ID único para esta transação fictícia
    pix_id = f"pay_{uuid.uuid4().hex[:8]}"
    
    # String padrão de Pix Copia e Cola estruturada com o valor fixo
    pix_copia_e_cola = f"00020126360014BR.GOV.BCB.PIX0114+55119999999995204000053039865404{VALOR_FIXO:.2f}5802BR5925VendingMachine6009SaoPaulo62070503***6304ABCD"
    
    print(f"[API] Pix Gerado com Sucesso. ID do Pagamento: {pix_id}")
    
    return {
        "status": "pending",
        "pix_code": pix_copia_e_cola,
        "pix_id": pix_id
    }


@app.post("/webhook-pix")
async def webhook_pix(request: Request):
    """
    Rota que recebe o aviso de pagamento (Webhook) do Mercado Pago ou do Simulador.
    """
    try:
        dados = await request.json()
        print(f"\n[WEBHOOK] Notificação recebida: {dados}")
        
        # Padrão de leitura para o webhook do Mercado Pago ou do nosso /docs
        # Verifica se o status enviado é aprovado/concluído
        status = dados.get("status") or dados.get("action")
        
        if status in ["approved", "CONCLUIDO", "payment.updated"]:
            print("[WEBHOOK] Pagamento Confirmado! Enviando comando de liberação para a máquina...")
            
            # Dispara o aviso em tempo real via WebSocket para a máquina virtual
            await manager.send_message("LIBERAR_PRODUTO")
            return {"status": "sucesso", "mensagem": "Máquina notificada"}
            
        print("[WEBHOOK] Notificação recebida, mas o status não era de aprovação.")
        return {"status": "ignorado"}
        
    except Exception as e:
        print(f"[WEBHOOK] Erro ao processar dados: {e}")
        return {"status": "erro", "detalhes": str(e)}

# -----------------------------------------------------------------
# CANAL WEBSOCKET (CORRIGIDO)
# -----------------------------------------------------------------
@app.websocket("/ws/maquina")
async def websocket_endpoint(websocket: WebSocket):
    # Desativa o timeout de ping para evitar que a conexão caia por inatividade
    await manager.connect(websocket)
    print("\n[WS] 🔵 Máquina Virtual se conectou ao canal WebSocket!")
    try:
        while True:
            # Fica aguardando mensagens, mas sem desconectar por timeout
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect()
        print("\n[WS] 🔴 Máquina Virtual se desconectou do canal WebSocket.")


if __name__ == "__main__":
    import uvicorn
    # Inicializa o servidor local na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
