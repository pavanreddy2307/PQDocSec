from cryptography.hazmat.primitives import hashes


def sha256_hash_file(file_path):
    """
    Computes SHA-256 hash of a file.
    Returns hash bytes.
    """
    digest = hashes.Hash(hashes.SHA256())

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            digest.update(chunk)

    return digest.finalize()
