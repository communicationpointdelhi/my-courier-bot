# --- TrackingMore API Setup ---
url = "https://api.trackingmore.com/v4/trackings/get"

headers = {
    "Content-Type": "application/json",
    "Tracking-Api-Key": TRACKING_API_KEY
}

# --- First try WITH carrier ---
payload = {
    "tracking_numbers": [track_num],
    "courier_code": carrier
}

response = requests.post(url, json=payload, headers=headers, timeout=10).json()
items = response.get('data', {}).get('items', [])

# --- Fallback: auto-detect ---
if not items:
    payload = {
        "tracking_numbers": [track_num]
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10).json()
    items = response.get('data', {}).get('items', [])

# --- Final result ---
if items:
    data = items[0]
    status = data.get('delivery_status', 'Unknown')
    last_event = data.get('last_event', 'No recent updates')

    reply = (
        f"✅ *Status:* {status.upper()}\n"
        f"📍 *Last Update:* {last_event}\n"
        f"🔢 *Number:* {track_num}"
    )
    msg.body(reply)
else:
    msg.body(f"❌ Could not find tracking info for {track_num}.")
