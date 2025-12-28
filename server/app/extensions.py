class AppState:
    role = "IDLE"   # IDLE | SENDER | RECEIVER
    receiver_ip = None
    receiver_port = 5000

    peer_rsa_public_key = None
    peer_signature_public_key = None

    discovery_thread = None
    accepting_files = False


app_state = AppState()
