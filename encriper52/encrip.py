from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import time
import hmac
from typing import Tuple, Union
from secure_memory import SecureBytes, secure_wipe, lock_memory, unlock_memory


def encrip(data: bytes, password: Union[str, SecureBytes], header: str) -> bytes:
    """
    加密数据
    
    Args:
        data: 要加密的原始数据
        password: 加密密码
        header: 文件头信息
        
    Returns:
        加密后的数据，包含盐值、IV、标签和加密内容
    """
    password_bytes = bytearray(str(password).encode())
    lock_memory(password_bytes)
    
    try:
        salt1: bytes = os.urandom(32)
        kdf1: PBKDF2HMAC = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt1,
            iterations=500000,
            backend=default_backend()
        )
        key1: bytearray = bytearray(kdf1.derive(bytes(password_bytes)))
        lock_memory(key1)
        
        secure_wipe(password_bytes)
        
        yield 1
        
        salt2: bytes = os.urandom(32)
        kdf2: PBKDF2HMAC = PBKDF2HMAC(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt2,
            iterations=300000,
            backend=default_backend()
        )
        key2: bytearray = bytearray(kdf2.derive(bytes(key1)))
        lock_memory(key2)
        
        secure_wipe(key1)
        
        yield 2
        
        salt3: bytes = os.urandom(32)
        hmac_key: bytearray = bytearray(hmac.new(bytes(key2), salt3, hashes.SHA512().name).digest())
        lock_memory(hmac_key)
        
        secure_wipe(key2)
        
        yield 3
        
        iv: bytes = os.urandom(16)
        cipher: Cipher = Cipher(algorithms.AES(bytes(hmac_key[:32])), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        secure_wipe(hmac_key)
        
        yield 4
        
        header_bytes: bytes = header.encode()
        header_length: bytes = len(header_bytes).to_bytes(4, byteorder='big')
        combined_data: bytes = header_length + header_bytes + data
        
        yield 5
        
        obfuscation_data: bytes = os.urandom(64)
        final_data: bytes = obfuscation_data + combined_data + obfuscation_data[::-1]
        
        yield 6
        
        encrypted_data: bytes = encryptor.update(final_data) + encryptor.finalize()
        tag: bytes = encryptor.tag
        
        yield 7
        
        time.sleep(0.1)
        
        yield salt1 + salt2 + salt3 + iv + tag + encrypted_data
    finally:
        if 'password_bytes' in locals():
            secure_wipe(password_bytes)


def decrip(encrypted_data: bytes, password: Union[str, SecureBytes]) -> Tuple[bytes, str]:
    """
    解密数据
    
    Args:
        encrypted_data: 加密后的数据
        password: 解密密码
        
    Returns:
        原始数据和文件头的元组
    """
    password_bytes = bytearray(str(password).encode())
    lock_memory(password_bytes)
    
    try:
        salt1: bytes = encrypted_data[:32]
        salt2: bytes = encrypted_data[32:64]
        salt3: bytes = encrypted_data[64:96]
        iv: bytes = encrypted_data[96:112]
        tag: bytes = encrypted_data[112:128]
        ciphertext: bytes = encrypted_data[128:]

        yield 1
        
        kdf1: PBKDF2HMAC = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt1,
            iterations=500000,
            backend=default_backend()
        )
        key1: bytearray = bytearray(kdf1.derive(bytes(password_bytes)))
        lock_memory(key1)
        
        secure_wipe(password_bytes)
        
        kdf2: PBKDF2HMAC = PBKDF2HMAC(
            algorithm=hashes.SHA3_512(),
            length=32,
            salt=salt2,
            iterations=300000,
            backend=default_backend()
        )
        key2: bytearray = bytearray(kdf2.derive(bytes(key1)))
        lock_memory(key2)
        
        secure_wipe(key1)

        yield 2
        
        hmac_key: bytearray = bytearray(hmac.new(bytes(key2), salt3, hashes.SHA512().name).digest())
        lock_memory(hmac_key)
        
        secure_wipe(key2)

        yield 3
        
        cipher: Cipher = Cipher(algorithms.AES(bytes(hmac_key[:32])), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        secure_wipe(hmac_key)

        yield 4
        
        decrypted_data: bytes = decryptor.update(ciphertext) + decryptor.finalize()

        yield 5
        
        final_data: bytes = decrypted_data[64:-64]

        yield 6
        
        time.sleep(0.1)
        
        header_length: int = int.from_bytes(final_data[:4], byteorder='big')
        header_bytes: bytes = final_data[4:4+header_length]
        header: str = header_bytes.decode()
        data: bytes = final_data[4+header_length:]

        yield 7
        
        yield data, header
    finally:
        if 'password_bytes' in locals():
            secure_wipe(password_bytes)



check:bytes = b'''trj496j4rt4a65u4rrtj646841@$&1rtj484564158t4j84rh44tpiuou84wesdbh469awqt49rd8h65s
fht4844jrtjt5145416tj6f54thr46fr5th46&f56gh&&*f65r4t%r4u1654j6$^j56rf4h41fjmjna6n48pokl4y8fj4y86fg4
1fmnfyjftHRJRH77trr4h4t48j47$%&%$&*rtj8d4ty89k4ty8hrrtDRTJ48rtj8t4t8Uiy484jtj48tu4h48rt48r%^57hrt@%
bv1xzsw83aq489y41j48y449kijhy^**hr58f$f$gsh46rh5tr68tu44444poqfv4xc6xdfht6re6y457564u61yjmdgky)*hhg
(*^(gBUGU*&&GG*HIO[dht65urt64jr*(^&*(Y_vbufbsg^RF&^M>:"LPrhrtr4u1654j66ithfh&*GGfh4t4ju#$FVYgd))]))
j4t8y9iktd964fg1nmsrjt4saewru4h8to48up4uik4fh4h84j8ykgn49tj9ytikuy44etuuikuytyjutrujtut4ryhe4r4yrt9
KJKJTRTUTUhrtujjtr&%*&(&(jtyjt8484h88tu4ty41hJYTUr59r5yyYHTTRUHRTJJ5rtu4t4h&*^&%%^&&&*^jjtjtyhtrf))'''

