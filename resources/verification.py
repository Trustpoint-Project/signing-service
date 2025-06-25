import base64

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding

algo = input('Public key algorithm [RSA / ECC]: ').strip().upper()
hash_algo = input('Expected hash type [SHA256 / SHA384 / SHA512 / SHA224]: ').strip().upper()


digest_hex = input('\nEnter the hashed message (Hex format): ').strip()
digest = bytes.fromhex(digest_hex)


signature_b64 = input('Enter the signature (Base64): ').strip()
signature = base64.b64decode(signature_b64)


print('\nEnter the certificate (PEM format):')
pem_lines = []
while True:
    line = input()
    pem_lines.append(line)
    if 'END CERTIFICATE' in line:
        break
cert_pem = '\n'.join(pem_lines).encode()

try:
    cert = x509.load_pem_x509_certificate(cert_pem)
    public_key = cert.public_key()
except Exception as e:
    print(f'Failed to load certificate: {e}')
    exit(1)


hash_algos = {
    'SHA256': hashes.SHA256(),
    'SHA384': hashes.SHA384(),
    'SHA512': hashes.SHA512(),
    'SHA224': hashes.SHA224(),
}

chosen_hash = hash_algos[hash_algo]


try:
    if algo == 'RSA':
        public_key.verify(signature, digest, padding.PKCS1v15(), chosen_hash)
    elif algo == 'ECC':
        public_key.verify(signature, digest, ec.ECDSA(chosen_hash))
    else:
        print('Unsupported algorithm')
        exit(1)

    print('\nSignature is VALID.')
except Exception as e:
    print(f'\nSignature verification FAILED: {e}')
