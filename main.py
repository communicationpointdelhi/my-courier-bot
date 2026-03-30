import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Get API key from environment
TRACKING_API_KEY = os.environ.get("TRACKING_API_KEY")

# ✅ ROOT ROUTE (IMPORTANT for Render)
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
            msg.body("Format: [Carrier] [Number]\nExample: DTDC 123456")
            return str(resp)

        # Carrier mapping
        CARRIER_MAP = {
            "dtdc": "dtdc-express",
            "delhivery": "delhivery",
            "bluedart": "blue-dart",
            "trackon": "trackon-couriers"
        }

        carrier_input = parts[0].lower()
        track_num = parts[1]
        carrier = CARRIER_MAP.get(carrier_input, carrier_input)

        # TrackingMore API
        url = "https://api.trackingmore.com/v4/trackings/get"
        headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": TRACKING_API_KEY
        }

        params = {
            "tracking_numbers": track_num,
            "courier_code": carrier
        }

        response = requests.get(url, params=params, headers=headers, timeout=10).json()

        if response.get('meta', {}).get('code') == 200 and response.get('data'):
            data = response['data'][0]
            status = data.get('delivery_status', 'Unknown')
            last_event = data.get('last_event', 'No recent updates')

            reply = (
                f"✅ Status: {status.upper()}\n"
                f"📍 Last Update: {last_event}\n"
                f"🔢 Number: {track_num}"
            )
            msg.body(reply)
        else:
            msg.body(f"❌ No info for {track_num}. Check number or carrier.")

    except Exception as e:
        print("ERROR:", e)  # 👈 logs will help debugging
        msg.body("⚠️ Service error. Try again later.")

    return str(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
