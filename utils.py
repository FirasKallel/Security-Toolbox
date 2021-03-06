import binascii
import os
from base64 import *
from hashlib import *
from typing import Union, Tuple
from Crypto.Cipher import AES, DES, Blowfish, CAST
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKeyWithSerialization, RSAPublicKey


class SymetricCipher:
    def pad(self, word, base):
        return word + ((base - len(word) % base) * ' ')


class Encoding:
    def code(self, msg: str, base: int) -> Union[str, None]:
        if base == 64:
            return b64encode(msg.encode('ascii')).decode("utf-8")
        elif base == 32:
            return b32encode(msg.encode('ascii')).decode("utf-8")
        elif base == 16:
            return b16encode(msg.encode('ascii')).decode("utf-8")
        else:
            print("Wrong Base")
            return None

    def decode(self, coded_msg: str, base: int) -> Union[str, None]:
        if base == 64:
            try:
                d = b64decode(coded_msg.encode('ascii')).decode("utf-8")
            except:
                d = "La base demandé n'est pas compatible. Veuillez réessayer en choisissant la bonne base"
            return d
        elif base == 32:
            try:
                d = b32decode(coded_msg.encode('ascii')).decode("utf-8")
            except:
                d = "La base demandé n'est pas compatible. Veuillez réessayer en choisissant la bonne base"
            return d
        elif base == 16:
            try :
                d = b16decode(coded_msg.encode('ascii')).decode("utf-8")
            except:
                d = "La base demandé n'est pas compatible. Veuillez réessayer en choisissant la bonne base"
            return d
        else:
            print("Wrong Base")
            return None


class Hashing:
    def hash_msg(self, msg: str, algo: str) -> str:
        if algo == "SHA256":
            return sha3_256(msg.encode('ascii')).hexdigest()
        elif algo == "SHA512":
            return sha3_512(msg.encode('ascii')).hexdigest()
        elif algo == "BLAKE2b":
            return blake2b(msg.encode('ascii')).hexdigest()
        elif algo == "BLAKE2s":
            return blake2s(msg.encode('ascii')).hexdigest()
        elif algo == "MD5":
            return md5(msg.encode('ascii')).hexdigest()


class BruteForce:
    def search_for_original(self, hashed_msg: str, algo: str, dict_path: str = "pentbox-wlist.txt") -> Union[None, str]:
        hash_method = None
        if algo == "SHA256":
            hash_method = sha3_256
        elif algo == "SHA512":
            hash_method = sha3_512
        elif algo == "BLAKE2b":
            hash_method = blake2b
        elif algo == "BLAKE2s":
            hash_method = blake2s
        elif algo == "MD5":
            hash_method = md5
        with open(dict_path, 'r') as file:
            for word in file:
                word = word[:-1]
                if hash_method(word.encode('ascii')).hexdigest() == hashed_msg:
                    return word
        return None


class AESCipher(SymetricCipher):
    MODE = AES.MODE_CBC

    def encrypt(self, msg, key_size, password):
        if key_size == 256:
            salt = os.urandom(16)
            password = sha256(password.encode('ascii')).digest()
        elif key_size == 128:
            salt = os.urandom(16)
            password = md5(password.encode('ascii')).digest()
        else:
            print("wrong key size")
            return None
        crypter = AES.new(password, mode=self.MODE, IV=salt)
        return binascii.b2a_base64(salt).decode("utf-8")[:-1], binascii.b2a_base64(
            crypter.encrypt(self.pad(msg, key_size))).decode(
            "utf-8")[:-1]

    def decrypt(self, content, key_size, salt, password):
        salt = binascii.a2b_base64(salt)
        content = binascii.a2b_base64(content)
        if key_size == 256:
            password = sha256(password.encode('ascii')).digest()
        elif key_size == 128:
            password = md5(password.encode('ascii')).digest()
        else:
            print("wrong key size")
            return None
        crypter = AES.new(password, mode=self.MODE, IV=salt)
        return crypter.decrypt(content).decode("utf-8")


class DESCipher(SymetricCipher):
    MODE = DES.MODE_CBC

    def encrypt(self, msg, password):
        salt = os.urandom(8)
        password = blake2b(password.encode("ascii"), digest_size=8).digest()
        crypter = DES.new(password, mode=self.MODE, IV=salt)
        return binascii.b2a_base64(salt).decode("utf-8")[:-1], binascii.b2a_base64(
            crypter.encrypt(self.pad(msg, 8))).decode(
            "utf-8")[:-1]

    def decrypt(self, content, salt, password):
        salt = binascii.a2b_base64(salt)
        content = binascii.a2b_base64(content)
        password = blake2b(password.encode("ascii"), digest_size=8).digest()
        crypter = DES.new(password, mode=self.MODE, IV=salt)
        return crypter.decrypt(content).decode("utf-8")


class BlowfishCipher(SymetricCipher):
    MODE = Blowfish.MODE_CBC

    def encrypt(self, msg, key_size, password):
        if key_size == 256:
            salt = os.urandom(8)
            password = sha256(password.encode('ascii')).digest()
        elif key_size == 128:
            salt = os.urandom(8)
            password = md5(password.encode('ascii')).digest()
        else:
            print("wrong key size")
            return None
        crypter = Blowfish.new(password, mode=self.MODE, IV=salt)
        return binascii.b2a_base64(salt).decode("utf-8")[:-1], binascii.b2a_base64(
            crypter.encrypt(self.pad(msg, key_size))).decode(
            "utf-8")[:-1]

    def decrypt(self, content, key_size, salt, password):
        salt = binascii.a2b_base64(salt)
        content = binascii.a2b_base64(content)
        if key_size == 256:
            password = sha256(password.encode('ascii')).digest()
        elif key_size == 128:
            password = md5(password.encode('ascii')).digest()
        else:
            print("wrong key size")
            return None
        crypter = Blowfish.new(password, mode=self.MODE, IV=salt)
        return crypter.decrypt(content).decode("utf-8")


class CASTCipher(SymetricCipher):
    MODE = CAST.MODE_CBC

    def encrypt(self, msg, password):
        salt = os.urandom(8)
        password = blake2b(password.encode("ascii"), digest_size=8).digest()
        crypter = CAST.new(password, mode=self.MODE, IV=salt)
        return binascii.b2a_base64(salt).decode("utf-8")[:-1], binascii.b2a_base64(
            crypter.encrypt(self.pad(msg, 8))).decode(
            "utf-8")[:-1]

    def decrypt(self, content, salt, password):
        salt = binascii.a2b_base64(salt)
        content = binascii.a2b_base64(content)
        password = blake2b(password.encode("ascii"), digest_size=8).digest()
        crypter = CAST.new(password, mode=self.MODE, IV=salt)
        return crypter.decrypt(content).decode("utf-8")


class RSA:
    def generate_keys(self, key_size: int, password: str, path: str = None) -> Union[
        Tuple[None, None, RSAPrivateKeyWithSerialization],
        Tuple[str, str, RSAPrivateKeyWithSerialization]
    ]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode("ascii"))
        )
        public_key = private_key.public_key()
        public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        if path:
            with open(path + '/private_key.pem', 'wb') as f:
                f.write(private)
            with open(path + '/public_key.pem', 'wb') as f:
                f.write(public)
            return None, None, private_key
        else:
            return private.decode("utf-8"), public.decode("utf-8"), private_key

    def read_private_key(self, path: str, password: str = None) -> Union[RSAPrivateKeyWithSerialization, None]:
        if password:
            password = password.encode("ascii")
        try:
            with open(path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=password,
                    backend=default_backend()
                )
        except TypeError:
            print("Password was not given but private key is encrypted")
            return None
        except ValueError as e:
            if e.args[0] == "Bad decrypt. Incorrect password?":
                print("The password you provided is incorrect")
            else:
                print("The private key you provided may be in an incorrect format")
            return None
        return private_key

    def read_public_key(self, path: str) -> Union[None, RSAPublicKey]:
        try:
            with open(path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(
                    key_file.read(),
                    backend=default_backend()
                )
        except ValueError:
            print("The public key you provided may be in an incorrect format")
            return None
        return public_key

    def encrypt(self, msg: str, public_key: RSAPublicKey) -> str:
        encrypted = public_key.encrypt(
            msg.encode("ascii"),
            padding=padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return binascii.b2a_base64(encrypted).decode("utf-8")

    def decrypt(self, encrypted: str, private_key: RSAPrivateKeyWithSerialization) -> str:
        original_message = private_key.decrypt(
            binascii.a2b_base64(encrypted),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return original_message.decode("utf-8")

    def sign(self, msg: str, private_key: RSAPrivateKeyWithSerialization) -> str:
        signed = private_key.sign(
            msg.encode("ascii"),
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            algorithm=hashes.SHA256()
        )
        return binascii.b2a_base64(signed).decode("utf-8")

    def verify(self, msg: str, signed: str, public_key: RSAPublicKey) -> bool:
        try:
            public_key.verify(
                binascii.a2b_base64(signed),
                msg.encode("ascii"),
                padding=padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                algorithm=hashes.SHA256()
            )
        except InvalidSignature:
            return False
        return True


encoding_utils = Encoding()
hashing_utils = Hashing()
brute_force_utils = BruteForce()
rsa_utils = RSA()
aes_utils = AESCipher()
des_utils = DESCipher()
blowfish_utils = BlowfishCipher()
cast_utils = CASTCipher()
