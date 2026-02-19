import os
import shutil
import subprocess
from flask import current_app


# ======================================================
# 1️⃣ Load existing keys (already generated in C)
# ======================================================

def load_kyber_public_key() -> bytes:
    path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "kyber_pk.bin"
    )
    with open(path, "rb") as f:
        return f.read()


def load_kyber_private_key() -> bytes:
    path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "kyber_sk.bin"
    )
    with open(path, "rb") as f:
        return f.read()


def load_dilithium_public_key() -> bytes:
    path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "dilithium_pk.bin"
    )
    with open(path, "rb") as f:
        return f.read()


def load_dilithium_private_key() -> bytes:
    path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "dilithium_sk.bin"
    )
    with open(path, "rb") as f:
        return f.read()


# ======================================================
# 2️⃣ Store received public keys (handshake phase)
# ======================================================

def store_sender_dilithium_public_key(pk_bytes: bytes):
    """
    Receiver stores sender's Dilithium public key as raw bytes
    """
    dest = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "sender_dilithium_pk.bin"
    )
    with open(dest, "wb") as f:
        f.write(pk_bytes)


def store_receiver_kyber_public_key(pk_bytes: bytes):
    """
    Sender stores receiver's Kyber public key as raw bytes
    """
    dest = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "receiver_kyber_pk.bin"
    )
    with open(dest, "wb") as f:
        f.write(pk_bytes)
# ======================================================
# 3️⃣ Sender side: Kyber encapsulation
# ======================================================

def sender_generate_shared_secret_and_ciphertext():
    """
    Uses receiver's Kyber public key to generate:
    - shared secret
    - Kyber ciphertext
    """
    
    kyber_encaps_bin = os.path.join(
        current_app.root_path,
        "services", "PQC", "kyber", "bin", "kyber_encaps"
    )
    
    if not os.path.exists(kyber_encaps_bin):
        raise FileNotFoundError("kyber_encaps binary not found")
    print("Running kyber_encaps binary")
    subprocess.run([kyber_encaps_bin], check=True)
    
    shared_secret_path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "shared_secret_sender.bin"
    )
    print("Shared secret and Kyber ciphertext generated")

    ciphertext_path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "kyber_ct.bin"
    )

    with open(shared_secret_path, "rb") as f:
        shared_secret = f.read()

    with open(ciphertext_path, "rb") as f:
        ciphertext = f.read()

    return shared_secret, ciphertext


# ======================================================
# 4️⃣ Receiver side: Kyber decapsulation
# ======================================================

def receiver_derive_shared_secret_from_ciphertext():
    """
    Uses:
    - receiver Kyber private key
    - received Kyber ciphertext
    """

    kyber_decaps_bin = os.path.join(
        current_app.root_path,
        "services", "PQC", "kyber", "bin", "kyber_decaps"
    )

    if not os.path.exists(kyber_decaps_bin):
        raise FileNotFoundError("kyber_decaps binary not found")

    subprocess.run([kyber_decaps_bin], check=True)

    shared_secret_path = os.path.join(
        current_app.config["PQC_KEY_FOLDER"],
        "shared_secret_receiver.bin"
    )

    with open(shared_secret_path, "rb") as f:
        return f.read()