import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import padding
from base64 import urlsafe_b64encode, urlsafe_b64decode
import getpass

# Constants
KEY_LENGTH = 32  # 256 bits
IV_LENGTH = 16   # AES block size
SALT_LENGTH = 16 # For PBKDF2
ITERATIONS = 100000

def derive_key(password: str, salt: bytes) -> bytes:
    """Derives a secret key from the password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def encrypt_file(filepath: str, password: str):
    """Encrypts a file using AES-256-CBC."""
    # Read the file content
    with open(filepath, 'rb') as file:
        plaintext = file.read()

    # Generate salt and IV
    salt = os.urandom(SALT_LENGTH)
    iv = os.urandom(IV_LENGTH)

    # Derive the key from password
    key = derive_key(password, salt)

    # Pad the plaintext
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_plaintext = padder.update(plaintext) + padder.finalize()

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Write salt + iv + ciphertext to a new file
    encrypted_file = filepath + ".enc"
    with open(encrypted_file, 'wb') as file:
        file.write(salt + iv + ciphertext)

    print(f"[+] File encrypted successfully: {encrypted_file}")

def decrypt_file(filepath: str, password: str):
    """Decrypts a file encrypted with encrypt_file()."""
    with open(filepath, 'rb') as file:
        data = file.read()

    # Extract salt, iv, and ciphertext
    salt = data[:SALT_LENGTH]
    iv = data[SALT_LENGTH:SALT_LENGTH+IV_LENGTH]
    ciphertext = data[SALT_LENGTH+IV_LENGTH:]

    # Derive the key from password
    key = derive_key(password, salt)

    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

    # Write decrypted content to a new file
    decrypted_file = filepath.replace(".enc", ".dec")
    with open(decrypted_file, 'wb') as file:
        file.write(plaintext)

    print(f"[+] File decrypted successfully: {decrypted_file}")

def main():
    print("=== AES-256 File Encryptor / Decryptor ===")
    print("1. Encrypt File")
    print("2. Decrypt File")
    choice = input("Select an option (1/2): ")

    if choice not in ['1', '2']:
        print("[-] Invalid choice.")
        return

    filepath = input("Enter file path: ")
    if not os.path.isfile(filepath):
        print("[-] File not found.")
        return

    password = getpass.getpass("Enter password: ")

    if choice == '1':
        encrypt_file(filepath, password)
    elif choice == '2':
        decrypt_file(filepath, password)

if __name__ == "__main__":
    main()
