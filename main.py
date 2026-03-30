import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

TRACKING_API_KEY = os.environ.get("TRACKING_API_KEY")

CARRIER_MAP = {
    "dtdc": "dtdc-express",
    "delhivery": "delhivery",
    "bluedart": "blue-dart",
    "trackon": "trackon-couriers"
}

@app.route("/")
def home():
    return "Bot is running"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    try:
        parts = incoming_msg.split()

        if len(parts) < 2:
            msg.body("📦 Send like:\nDTDC 123456")
            return str(resp)

        carrier_input = parts[0].lower()
        track_num = parts[1]
        carrier = CARRIER_MAP.get(carrier_input, carrier_input)

        url = "https://api.trackingmore.com/v4/trackings/get"

        headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": TRACKING_API_KEY
        }

        # Try with carrier
        payload = {
            "tracking_numbers": [track_num],
            "courier_code": carrier
        }

        response = requests.post(url, json=payload, headers=headers, timeout=10).json()
        items = response.get('data', {}).get('items', [])

        # Fallback auto-detect
        if not items:
            payload = {
                "tracking_numbers": [track_num]
            }
            response = requests.post(url, json=payload, headers=headers, timeout=10).json()
            items = response.get('data', {}).get('items', [])

        if items:
            data = items[0]
            status = data.get('delivery_status', 'Unknown')
            last_event = data.get('last_event', 'No updates')

            reply = f"✅ Status: {status}\n📍 {last_event}"
            msg.body(reply)
        else:
            msg.body("❌ Tracking not found.")

    except Exception as e:
        print("ERROR:", e)
        msg.body("⚠️ Error. Try again later.")

    return str(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
       
      
