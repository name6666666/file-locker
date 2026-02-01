from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os
import time
import hmac
from typing import Tuple


def encrip(data: bytes, password: str, header: str) -> bytes:
    """
    加密数据
    
    Args:
        data: 要加密的原始数据
        password: 加密密码
        header: 文件头信息
        
    Returns:
        加密后的数据，包含盐值、IV、标签和加密内容
    """
    # 第一层：PBKDF2HMAC派生主密钥
    salt1: bytes = os.urandom(32)
    kdf1: PBKDF2HMAC = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt1,
        iterations=500000,
        backend=default_backend()
    )
    key1: bytes = kdf1.derive(password.encode())

    yield 1
    
    # 第二层：使用不同参数再次派生
    salt2: bytes = os.urandom(32)
    kdf2: PBKDF2HMAC = PBKDF2HMAC(
        algorithm=hashes.SHA3_512(),
        length=32,
        salt=salt2,
        iterations=300000,
        backend=default_backend()
    )
    key2: bytes = kdf2.derive(key1)

    yield 2
    
    # 第三层：HMAC-SHA512处理
    salt3: bytes = os.urandom(32)
    hmac_key: bytes = hmac.new(key2, salt3, hashes.SHA512().name).digest()

    yield 3
    
    # 第四层：使用AES-256-GCM加密
    iv: bytes = os.urandom(16)
    cipher: Cipher = Cipher(algorithms.AES(hmac_key[:32]), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    yield 4
    
    # 准备数据
    header_bytes: bytes = header.encode()
    header_length: bytes = len(header_bytes).to_bytes(4, byteorder='big')
    combined_data: bytes = header_length + header_bytes + data

    yield 5
    
    # 添加额外的混淆数据
    obfuscation_data: bytes = os.urandom(64)  # 64字节随机数据
    final_data: bytes = obfuscation_data + combined_data + obfuscation_data[::-1]  # 前后添加混淆数据

    yield 6
    
    # 加密数据
    encrypted_data: bytes = encryptor.update(final_data) + encryptor.finalize()
    tag: bytes = encryptor.tag

    yield 7
    
    # 添加随机延迟
    time.sleep(0.1)
    
    # 返回所有必要的数据
    yield salt1 + salt2 + salt3 + iv + tag + encrypted_data


def decrip(encrypted_data: bytes, password: str) -> Tuple[bytes, str]:
    """
    解密数据
    
    Args:
        encrypted_data: 加密后的数据
        password: 解密密码
        
    Returns:
        原始数据和文件头的元组
    """
    # 提取参数
    salt1: bytes = encrypted_data[:32]
    salt2: bytes = encrypted_data[32:64]
    salt3: bytes = encrypted_data[64:96]
    iv: bytes = encrypted_data[96:112]
    tag: bytes = encrypted_data[112:128]
    ciphertext: bytes = encrypted_data[128:]

    yield 1
    
    # 派生密钥
    kdf1: PBKDF2HMAC = PBKDF2HMAC(
        algorithm=hashes.SHA512(),
        length=32,
        salt=salt1,
        iterations=500000,
        backend=default_backend()
    )
    key1: bytes = kdf1.derive(password.encode())
    
    kdf2: PBKDF2HMAC = PBKDF2HMAC(
        algorithm=hashes.SHA3_512(),
        length=32,
        salt=salt2,
        iterations=300000,
        backend=default_backend()
    )
    key2: bytes = kdf2.derive(key1)

    yield 2
    
    # HMAC处理
    hmac_key: bytes = hmac.new(key2, salt3, hashes.SHA512().name).digest()

    yield 3
    
    # 解密
    cipher: Cipher = Cipher(algorithms.AES(hmac_key[:32]), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()

    yield 4
    
    # 解密数据
    decrypted_data: bytes = decryptor.update(ciphertext) + decryptor.finalize()

    yield 5
    
    # 移除混淆数据
    final_data: bytes = decrypted_data[64:-64]  # 移除前后的混淆数据

    yield 6
    
    # 添加随机延迟
    time.sleep(0.1)
    
    # 提取文件头和数据
    header_length: int = int.from_bytes(final_data[:4], byteorder='big')
    header_bytes: bytes = final_data[4:4+header_length]
    header: str = header_bytes.decode()
    data: bytes = final_data[4+header_length:]

    yield 7
    
    yield data, header
