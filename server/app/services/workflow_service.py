import time

from app.services.encryption_service import aes_encrypt_file,aes_decrypt_file
from app.services.kem_service import rsa_encrypt_key, rsa_decrypt_key
from app.services.signature_service import sign_hash,verify_signature
from app.utils.helpers import sha256_hash_file
import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

def encrypt_file_workflow(
    input_path,
    output_dir,
    rsa_public_key,
    signing_private_key
):
    # 1. AES encrypt file
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    aes_start = time.perf_counter_ns()
    encrypted_path, aes_key = aes_encrypt_file(input_path, output_dir)
    aes_end = time.perf_counter_ns()

    # 2. RSA encrypt AES key (KEM)
    rsa_start = time.perf_counter_ns()
    encrypted_aes_key = rsa_encrypt_key(aes_key, rsa_public_key)
    rsa_end = time.perf_counter_ns()

    # 3. Hash encrypted file
    hash_start = time.perf_counter_ns()
    file_hash = sha256_hash_file(encrypted_path)
    hash_end = time.perf_counter_ns()

    # 4. Sign hash
    sign_start = time.perf_counter_ns()
    signature = sign_hash(file_hash, signing_private_key)
    sign_end = time.perf_counter_ns()
    
    data = {
                "file_name": os.path.basename(input_path),
                'AES_time': (aes_end - aes_start) / 1e6,
                'RSA_time': (rsa_end - rsa_start) / 1e6,
                'Hash_time': (hash_end - hash_start) / 1e6,
                'Sign_time': (sign_end - sign_start) / 1e6
    }
    # response = supabase.table("classical encryption").insert(data).execute()
    # print("Supabase insert response:", response)

    return {
        "encrypted_file_path": encrypted_path,
        'aes_key': aes_key,
        "encrypted_aes_key": encrypted_aes_key,
        "file_hash": file_hash,
        "signature": signature
    }

def decrypt_file_workflow(
    encrypted_file_path,
    encrypted_aes_key,
    signature,
    rsa_private_key,
    signer_public_key,
    decrypted_output_dir,
    original_filename
):
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    # 1. Hash encrypted file

    hash_start = time.perf_counter_ns()
    file_hash = sha256_hash_file(encrypted_file_path)
    hash_end = time.perf_counter_ns()

    # 2. Verify signature
    verify_start = time.perf_counter_ns()
    if not verify_signature(file_hash, signature, signer_public_key):
        raise Exception("Signature verification failed")
    verify_end = time.perf_counter_ns()

    # 3. Decrypt AES key
    rsa_start = time.perf_counter_ns()
    aes_key = rsa_decrypt_key(encrypted_aes_key, rsa_private_key)
    rsa_end = time.perf_counter_ns()

    # 4. AES decrypt file
    aes_start = time.perf_counter_ns()
    decrypted_path = aes_decrypt_file(
        encrypted_file_path,
        decrypted_output_dir,
        aes_key,
        original_filename
    )
    aes_end = time.perf_counter_ns()

    data = {
        "file_name":original_filename,
        'Hash_time': (hash_end - hash_start) / 1e6,
        'Verify_time': (verify_end - verify_start) / 1e6,
        'RSA_time': (rsa_end - rsa_start) / 1e6,
        'AES_time': (aes_end - aes_start) / 1e6
    }

    # response = supabase.table("classical decryption").insert(data).execute()
    # print("Supabase insert response:", response)

    return decrypted_path
