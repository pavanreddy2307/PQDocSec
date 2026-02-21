from flask import current_app

# Key / KEM
from app.services.pqc_key_service import (
    sender_generate_shared_secret_and_ciphertext,
    receiver_derive_shared_secret_from_ciphertext
)

# Crypto
from app.services.crypto_service import (
    derive_aes_key_from_shared_secret,
    compute_hash_from_encrypted_file_and_kyber_ct
)

# AES encryption
from app.services.pqc_encryption_service import (
    encrypt_file_with_aes_key,
    decrypt_file_with_aes_key
)

# Signatures
from app.services.pqc_signature_service import (
    sign_hash_with_dilithium,
    verify_dilithium_signature
)
# Timer
import time

# ======================================================
# SENDER WORKFLOW (Encrypt + Sign)
# ======================================================

def pqc_encrypt_file_workflow(input_path: str):
    """
    PQC-based encryption workflow (Sender side)

    Returns:
        {
            encrypted_file_path,
            kyber_ciphertext,
            file_hash,
            signature
        }
    """
    start = time.perf_counter_ns()
    # 1️⃣ Kyber encapsulation (shared secret + ciphertext)
    shared_secret, kyber_ct = sender_generate_shared_secret_and_ciphertext()
    end = time.perf_counter_ns()
    print(f"Kyber encapsulation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken
    # 2️⃣ Derive AES key from shared secret
    print(f"Derived shared secret: {shared_secret.hex()}")  # Debug print of shared secret

    start = time.perf_counter_ns()
    aes_key = derive_aes_key_from_shared_secret(shared_secret)
    end = time.perf_counter_ns()
    print(f"AES key derivation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken
    print(f"Derived AES key: {aes_key.hex()}")  # Debug print of AES key
    # 3️⃣ AES encrypt file
    
    start = time.perf_counter_ns()
    encrypted_path = encrypt_file_with_aes_key(
        input_path,
        current_app.config["ENCRYPTED_FOLDER"],
        aes_key
    )
    end = time.perf_counter_ns()
    print(f"AES encryption time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    # 4️⃣ Hash encrypted file + Kyber ciphertext
    start = time.perf_counter_ns()
    file_hash = compute_hash_from_encrypted_file_and_kyber_ct(
        encrypted_path,
        f"{current_app.config['PQC_KEY_FOLDER']}/kyber_ct.bin"
    )
    end = time.perf_counter_ns()
    print(f"Hash computation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    # 5️⃣ Sign hash using Dilithium
    start = time.perf_counter_ns()
    signature = sign_hash_with_dilithium(file_hash)
    end = time.perf_counter_ns()
    print(f"Dilithium signature time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    return {
        "encrypted_file_path": encrypted_path,
        "kyber_ciphertext": kyber_ct,
        "shared_secret": shared_secret,
        "file_hash": file_hash,
        "signature": signature
    }


# ======================================================
# RECEIVER WORKFLOW (Verify + Decrypt)
# ======================================================

def pqc_decrypt_file_workflow(
    encrypted_file_path: str,
    signature: bytes,
    original_filename: str
):
    """
    PQC-based decryption workflow (Receiver side)

    Returns:
        decrypted_file_path
    """

    # 1️⃣ Hash encrypted file + Kyber ciphertext
    start = time.perf_counter_ns()
    file_hash = compute_hash_from_encrypted_file_and_kyber_ct(
        encrypted_file_path,
        f"{current_app.config['PQC_KEY_FOLDER']}/kyber_ct.bin"
    )
    end = time.perf_counter_ns()
    print(f"Hash computation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    # 2️⃣ Verify Dilithium signature
    start = time.perf_counter_ns()
    if not verify_dilithium_signature(file_hash, signature):
        raise Exception("Signature verification failed")
    end = time.perf_counter_ns()
    print(f"Dilithium signature verification time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    # 3️⃣ Kyber decapsulation (derive shared secret)
    start = time.perf_counter_ns()
    shared_secret = receiver_derive_shared_secret_from_ciphertext()
    end = time.perf_counter_ns()
    print(f"Kyber decapsulation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken
    print(f"Derived shared secret: {shared_secret.hex()}")  # Debug print of shared secret

    # 4️⃣ Derive AES key from shared secret
    start = time.perf_counter_ns()
    aes_key = derive_aes_key_from_shared_secret(shared_secret)
    end = time.perf_counter_ns()
    print(f"AES key derivation time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken
    print(f"Derived AES key: {aes_key.hex()}")  # Debug print of AES key

    # 5️⃣ AES decrypt file
    start = time.perf_counter_ns()
    decrypted_path = decrypt_file_with_aes_key(
        encrypted_file_path,
        current_app.config["DECRYPTED_FOLDER"],
        aes_key,
        original_filename
    )
    end = time.perf_counter_ns()
    print(f"AES decryption time: {(end - start) / 1e6:.2f} ms")  # Debug print of time taken

    return {
        "decrypted_file_path": decrypted_path,
        "file_hash": file_hash,
        "shared_secret": shared_secret,
        "signature_verified": True,
        "original_filename": original_filename,
        # This can be added if needed for debugging       
    }