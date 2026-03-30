import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests

app = Flask(__name__)

# REPLACE THIS with your key from Step 1
TRACKING_API_KEY = "YOUR_TRACKING_API_KEY"

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    # 1. Get the message from WhatsApp
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    try:
        # 2. Split message (Expected: "DTDC 123456")
        parts = incoming_msg.split()
        if len(parts) < 2:
            msg.body("Welcome! 📦\nSend your tracking like this:\n[Carrier] [Number]\n\nExample: DTDC 123456")
            return str(resp)

        carrier_input = parts[0].lower()
        track_num = parts[1]

        # 3. Ask TrackingMore for the status
        # We use the 'trackings/get' endpoint for v4
        url = f"https://api.trackingmore.com{track_num}"
        headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": TRACKING_API_KEY
        }
        
        response = requests.get(url, headers=headers).json()

        # 4. Parse the result
        if response.get('meta', {}).get('code') == 200 and response.get('data'):
            # Get the first result from the data list
            tracking_info = response['data'][0]
            status = tracking_info.get('delivery_status', 'Unknown')
            last_event = tracking_info.get('last_event', 'No details available')
            
            output = (
                f"📦 *Status:* {status.upper()}\n"
                f"📍 *Latest:* {last_event}\n"
                f"🔢 *Number:* {track_num}"
            )
            msg.body(output)
        else:
            msg.body(f"❌ Details for {track_num} not found. Check if the number is correct!")

    except Exception as e:
        msg.body("⚠️ Service busy. Please try again in a minute.")

    return str(resp)

if __name__ == "__main__":
    # Render provides a PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
