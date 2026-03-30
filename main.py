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

        # --- Carrier mapping ---
        CARRIER_MAP = {
            "dtdc": "dtdc-express",
            "delhivery": "delhivery",
            "bluedart": "blue-dart",
            "trackon": "trackon-couriers"
        }

        carrier_input = parts[0].lower()
        track_num = parts[1]
        carrier = CARRIER_MAP.get(carrier_input, carrier_input)

        # --- TrackingMore API Setup ---
        # Note: v4 /get is a GET request with query params
        url = "https://api.trackingmore.com"
        headers = {
            "Content-Type": "application/json",
            "Tracking-Api-Key": TRACKING_API_KEY
        }
        
        # We try to get results for this specific number
        params = {"tracking_numbers": track_num}
        response = requests.get(url, params=params, headers=headers, timeout=10).json()

        # --- Final result check ---
        # TrackingMore v4 returns results in the 'data' list
        if response.get('meta', {}).get('code') == 200 and response.get('data'):
            # Filter for the correct carrier if multiple exist, or just take the first
            data = response['data'][0] 
            status = data.get('delivery_status', 'Unknown')
            last_event = data.get('last_event', 'No recent updates')

            reply = (
                f"✅ *Status:* {status.upper()}\n"
                f"📍 *Last Update:* {last_event}\n"
                f"🔢 *Number:* {track_num}"
            )
            msg.body(reply)
        else:
            msg.body(f"❌ No info for {track_num}. Ensure the number is registered in your TrackingMore portal.")

    except Exception as e:
        msg.body("⚠️ Service busy. Please try again.")

    return str(resp)
