print("📡 Please scan your RFID card (press Ctrl+C to stop)...")

try:
    while True:
        # Wait for the reader to type the UID
        uid = input("UID: ").strip()
        if uid:
            print(f"✅ Card detected — UID: {uid}")
except KeyboardInterrupt:
    print("\n🛑 Stopped scanning.")
