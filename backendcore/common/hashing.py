from hashlib import sha256


def hash_str_and_salt(str_to_hash: str, salt: str) -> str:
    """
    Hashes a string along with some salt.
    """
    if not isinstance(str_to_hash, str):
        raise TypeError('String to hash must be a string: '
                        + f'{type(str_to_hash)=}')
    if not isinstance(salt, str):
        raise TypeError(f'Salt must be a string: {type(salt)=}')
    if not str_to_hash:
        raise ValueError('String to hash cannot be empty.')
    salted_str = str_to_hash + salt
    return sha256(salted_str.encode('utf-8')).hexdigest()
