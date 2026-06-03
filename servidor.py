from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
import asyncio

app = FastAPI()

# Armazena a conexão ativa da máquina virtual
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

# Modelo para simular os dados que o banco envia no Webhook
class WebhookData(BaseModel):
    pix_id: str
    status: str  # ex: "CONCLUIDO"

# -----------------------------------------------------------------
# ROTAS DA API
# -----------------------------------------------------------------

@app.get("/pedir-pix/{produto_id}")
async def pedir_pix(produto_id: int):
    """
    A máquina (ou o cliente) chama essa rota para solicitar o Pix de um produto.
    """
    # Aqui na vida real você chamaria a API do Mercado Pago/Efí.
    # Vamos simular um código Pix Copia e Cola estático.
    valores = {1: "5.00", 2: "7.00"}
    
    if produto_id not in valores:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    
    valor = valores[produto_id]
    pix_copia_e_cola = f"00020126360014BR.GOV.BCB.PIX0114+55119999999995204000053039865404{valor}5802BR5925VendingMachine6009SaoPaulo62070503***6304ABCD"
    
    print(f"[SERVIDOR] Pix de R$ {valor} gerado para o Produto {produto_id}")
    return {"status": "pendente", "pix_code": pix_copia_e_cola, "pix_id": f"id_simulado_{produto_id}"}


@app.post("/webhook-pix")
async def webhook_pix(data: WebhookData):
    """
    O Banco chama essa rota quando o Pix é pago.
    """
    print(f"[WEBHOOK] Banco avisou: Pix {data.pix_id} mudou para status: {data.status}")
    
    if data.status == "CONCLUIDO":
        # Avisa a máquina virtual via WebSocket para liberar o produto
        if manager.active_connection:
            await manager.send_message("LIBERAR_PRODUTO")
            return {"status": "sucesso", "mensagem": "Máquina notificada"}
        else:
            return {"status": "erro", "mensagem": "Máquina offline no momento"}
            
    return {"status": "ignorado"}

# -----------------------------------------------------------------
# CANAL WEBSOCKET (IoT)
# -----------------------------------------------------------------

@app.websocket("/ws/maquina")
async def websocket_endpoint(websocket: WebSocket):
    """
    Mantém o canal de comunicação aberto e em tempo real com a máquina.
    """
    await manager.connect(websocket)
    print("[SERVIDOR] Máquina Virtual se conectou via WebSocket!")
    try:
        while True:
            # Fica ouvindo se a máquina mandar alguma mensagem voluntária
            data = await websocket.receive_text()
            print(f"[SERVIDOR] Mensagem recebida da máquina: {data}")
    except WebSocketDisconnect:
        manager.disconnect()
        print("[SERVIDOR] Máquina Virtual se desconectou.")

if __name__ == "__main__":
    import uvicorn
    # Roda o servidor localmente na porta 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
