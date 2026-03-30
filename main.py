import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# API key from Render environment
TRACKING_API_KEY = os.environ.get("TRACKING_API_KEY")


# ✅ Home route
@app.route("/")
def home():
    return "Bot is running"


# ✅ WhatsApp webhook
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

        # 🔥 Carrier mapping (UPDATED)
        CARRIER_MAP = {
            "dtdc": "dtdc-express",
            "delhivery": "delhivery",
            "bluedart": "blue-dart",
            "blue": "blue-dart",
            "trackon": "trackon-couriers",
            "shree": "shree-anjani-courier",
            "anjani": "shree-anjani-courier",
            "skyking": "skyking-courier"
        }

        carrier_input = parts[0].lower()
        track_num = parts[1]
        carrier = CARRIER_MAP.get(carrier_input, carrier_input)

        # API request
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

        # ✅ SUCCESS
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

        # ❌ FALLBACK (SUPER IMPORTANT 🔥)
        else:
            # Smart fallback links
            if "blue" in carrier:
                link = f"https://www.bluedart.com/?track={track_num}"
            elif "dtdc" in carrier:
                link = f"https://www.dtdc.in/tracking.asp?awb={track_num}"
            elif "delhivery" in carrier:
                link = f"https://www.delhivery.com/track/package/{track_num}"
            elif "trackon" in carrier:
                link = f"https://trackon.in/tracking/?tracking_number={track_num}"
            elif "anjani" in carrier or "shree" in carrier:
                link = f"https://shreeanjanicourier.com/track?awb={track_num}"
            elif "skyking" in carrier:
                link = f"https://skyking.co/track?awb={track_num}"
            else:
                link = ""

            reply = (
                f"❌ Not found in API\n\n"
                f"🔍 Track here:\n{link}"
            )
            msg.body(reply)

    except Exception as e:
        print("ERROR:", e)
        msg.body("⚠️ Service error. Try again later.")

    return str(resp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
