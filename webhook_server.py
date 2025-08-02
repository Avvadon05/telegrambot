import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import sqlite3

load_dotenv()
CRYPTOBOT_SECRET = os.getenv("CRYPTOBOT_SECRET")
DATABASE = "bot.db"

app = FastAPI()

class CryptoBotWebhook(BaseModel):
    invoice_id: str
    user_id: int
    amount: float
    asset: str
    status: str

def get_user_by_invoice(invoice_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, amount FROM invoices WHERE invoice_id = ?", (invoice_id,))
    result = cur.fetchone()
    conn.close()
    return result

def mark_invoice_paid(invoice_id):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("UPDATE invoices SET status = 'paid' WHERE invoice_id = ?", (invoice_id,))
    conn.commit()
    conn.close()

def add_coins(user_id: int, coins: int):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (coins, user_id))
    conn.commit()
    conn.close()

def get_coin_amount(usd_amount):
    rates = {5: 500, 9: 1000, 14: 1500, 19: 2000, 33: 5000}
    return rates.get(usd_amount, 0)

@app.post("/cryptobot/webhook")
async def handle_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("Crypto-Pay-Signature", "")
    calculated_signature = hmac.new(CRYPTOBOT_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(signature, calculated_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    payload = CryptoBotWebhook(**data)

    if payload.status != "paid":
        return {"status": "ignored"}

    user_info = get_user_by_invoice(payload.invoice_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="Invoice not found")

    user_id, amount = user_info
    coins = get_coin_amount(int(amount))
    if coins == 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    add_coins(user_id, coins)
    mark_invoice_paid(payload.invoice_id)
    return {"status": "ok"}