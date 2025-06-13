from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from trustpoint_core.oid import AlgorithmIdentifier, NamedCurve
from trustpoint_core.serializer import PrivateKeySerializer


def generate_private_key(algorithm_oid_str: str, curve_name: str | None, key_size: int | None) -> str:
    algorithm_enum = AlgorithmIdentifier.from_dotted_string(algorithm_oid_str)

    if algorithm_enum.public_key_algo_oid.name == 'ECC':
        if not curve_name:
            raise ValueError('ECC curve name is required.')

        try:
            curve_obj = next(c.value.curve for c in NamedCurve if c.value.ossl_curve_name.lower() == curve_name.lower())
        except StopIteration:
            available = [c.value.ossl_curve_name for c in NamedCurve]
            raise ValueError(f'Unsupported ECC curve: {curve_name}. Available: {available}')

        private_key = ec.generate_private_key(curve_obj())
    else:
        if not key_size:
            raise ValueError('RSA key length is required.')
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    pem = PrivateKeySerializer(private_key).as_pkcs8_pem()
    return pem.decode('utf-8')


def load_private_key_object(pem_str: str):
    """Loads a PEM-encoded private key string into private key object."""
    return load_pem_private_key(pem_str.encode('utf-8'), password=None)
