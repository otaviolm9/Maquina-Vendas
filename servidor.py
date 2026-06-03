from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Configuração do Valor Fixo da Máquina
VALOR_FIXO = "5.00"  # Altere aqui para o valor que desejar (ex: "2.50", "10.00")

# Gerenciador da conexão WebSocket com a máquina
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

# Modelo de dados para simular o Webhook do Banco
class WebhookData(BaseModel):
    pix_id: str
    status: str  # Deve ser "CONCLUIDO" para liberar

# --- ROTAS HTTP ---

@app.get("/pedir-pix")
async def pedir_pix():
    """
    Rota chamada pela máquina para gerar o Pix de valor fixo.
    """
    # Linha do Pix Copia e Cola simulada com o valor fixo embutido
    pix_copia_e_cola = f"00020126360014BR.GOV.BCB.PIX0114+55119999999995204000053039865404{VALOR_FIXO}5802BR5925VendingMachine6009SaoPaulo62070503***6304ABCD"
    
    # ID padrão que usaremos para validar o pagamento no teste
    pix_id = "pix_fixo_demonstracao"
    
    print(f"\n[SERVIDOR] Novo Pix solicitado! Valor: R$ {VALOR_FIXO}")
    return {
        "status": "pendente",
        "pix_code": pix_copia_e_cola,
        "pix_id": pix_id
    }

@app.post("/webhook-pix")
async def webhook_pix(data: WebhookData):
    """
    Rota que simula o Banco avisando que o Pix foi pago.
    """
    print(f"\n[WEBHOOK] Notificação recebida -> ID: {data.pix_id} | Status: {data.status}")
    
    if data.status == "CONCLUIDO" and data.pix_id == "pix_fixo_demonstracao":
        if manager.active_connection:
            # Envia o comando em tempo real para a máquina liberar o produto
            await manager.send_message("LIBERAR_PRODUTO")
            print("[SERVIDOR] Comando 'LIBERAR_PRODUTO' enviado para a máquina.")
            return {"status": "sucesso", "mensagem": "Máquina notificada"}
        else:
            print("[SERVIDOR] Erro: A máquina está desconectada do WebSocket.")
            return {"status": "erro", "mensagem": "Máquina offline"}
            
    return {"status": "ignorado", "mensagem": "Status inválido ou ID incorreto"}

# --- CANAL WEBSOCKET ---

@app.websocket("/ws/maquina")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("\n[SERVIDOR] 🤖 Máquina Virtual conectada ao canal WebSocket!")
    try:
        while True:
            # Mantém a conexão aberta escutando a máquina (se necessário)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect()
        print("\n[SERVIDOR] ❌ Máquina Virtual se desconectou.")

if __name__ == "__main__":
    # Inicializa o servidor na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
