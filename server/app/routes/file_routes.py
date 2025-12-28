from flask import Blueprint, request, jsonify, current_app
from app.services.file_service import save_uploaded_file
from app.services.encryption_service import aes_encrypt_file
from app.extensions import app_state
import os
from app.services.workflow_service import decrypt_file_workflow
from app.services.key_service import load_rsa_private_key
from app.services.workflow_service import encrypt_file_workflow
from app.services.key_service import load_signature_private_key

file_bp = Blueprint("files", __name__)



@file_bp.route("/secureUpload", methods=["POST"])
def secureUpload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Save original file
    input_path = save_uploaded_file(
        file,
        current_app.config["UPLOAD_FOLDER"]
    )

    # Encrypt using AES
    encrypted_path, aes_key = aes_encrypt_file(
        input_path,
        current_app.config["ENCRYPTED_FOLDER"]
    )

    return jsonify({
        "message": "File encrypted using AES-256",
        "original_file": input_path,
        "encrypted_file": encrypted_path,
        "aes_key_hex": aes_key.hex()  # TEMP: for Phase-1 testing only
    })

@file_bp.route("/encrypt", methods=["POST"])
def encrypt_file():
    # Sender-only operation
    if app_state.role != "SENDER":
        return jsonify({"error": "Not in sender mode"}), 403

    if "file" not in request.files:
        return jsonify({"error": "File missing"}), 400

    if app_state.peer_rsa_public_key is None:
        return jsonify({"error": "Receiver public key not available"}), 400

    uploaded_file = request.files["file"]

    # Save original file
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    input_path = os.path.join(upload_dir, uploaded_file.filename)
    uploaded_file.save(input_path)

    # Load sender signature private key
    signature_private_key = load_signature_private_key()

    # Encrypt workflow
    result = encrypt_file_workflow(
        input_path=input_path,
        output_dir=current_app.config["ENCRYPTED_FOLDER"],
        receiver_rsa_public_key=app_state.peer_rsa_public_key,
        sender_signature_private_key=signature_private_key
    )

    return jsonify({
        "message": "File encrypted successfully",
        "encrypted_file": os.path.basename(result["encrypted_file_path"]),
        "encrypted_aes_key": result["encrypted_aes_key"].hex(),
        "signature": result["signature"].hex()
    })

@file_bp.route("/decrypt", methods=["POST"])
def decrypt_file():
    # Receiver-only operation
    if app_state.role != "RECEIVER":
        return jsonify({"error": "Not in receiver mode"}), 403

    if "file" not in request.files:
        return jsonify({"error": "Encrypted file missing"}), 400

    encrypted_file = request.files["file"]
    encrypted_aes_key = request.form.get("encrypted_aes_key")
    signature = request.form.get("signature")

    if not encrypted_aes_key or not signature:
        return jsonify({"error": "Missing key or signature"}), 400

    # Save encrypted file
    encrypted_dir = current_app.config["ENCRYPTED_FOLDER"]
    os.makedirs(encrypted_dir, exist_ok=True)

    encrypted_path = os.path.join(encrypted_dir, encrypted_file.filename)
    encrypted_file.save(encrypted_path)

    # Load receiver RSA private key
    rsa_private_key = load_rsa_private_key()

    # Sender public key must already be stored from handshake
    sender_signature_public_key = app_state.peer_signature_public_key
    if sender_signature_public_key is None:
        return jsonify({"error": "Sender public key not available"}), 400

    try:
        decrypted_path = decrypt_file_workflow(
            encrypted_file_path=encrypted_path,
            encrypted_aes_key=bytes.fromhex(encrypted_aes_key),
            signature=bytes.fromhex(signature),
            rsa_private_key=rsa_private_key,
            sender_signature_public_key=sender_signature_public_key,
            decrypted_output_dir=current_app.config["DECRYPTED_FOLDER"]
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "message": "File decrypted successfully",
        "decrypted_file": os.path.basename(decrypted_path)
    })