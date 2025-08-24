"""
COWN Quantum Encryption System
Hệ thống mã hóa lượng tử sử dụng QKD keys

Features:
- One-Time Pad (OTP) với quantum keys
- AES encryption với quantum key enhancement
- ChaCha20-Poly1305 với quantum keys
- Message authentication với quantum signatures
- Advanced security metrics
"""

import os
import hashlib
import hmac
import secrets
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.backends import default_backend
import logging

from quantum.protocols.qkd_protocol import qkd_manager, QuantumKey, ProtocolType

logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    QUANTUM_OTP = "quantum_otp"
    AES_QUANTUM = "aes_quantum"
    CHACHA20_QUANTUM = "chacha20_quantum"

class SecurityLevel(Enum):
    """Security levels for encryption"""
    STANDARD = "standard"
    HIGH = "high"
    QUANTUM = "quantum"
    ULTRA_QUANTUM = "ultra_quantum"

@dataclass
class EncryptionMetrics:
    """Metrics for encryption operations"""
    algorithm: EncryptionAlgorithm
    key_length: int
    message_length: int
    encryption_time: float
    security_level: float
    quantum_enhanced: bool

@dataclass
class QuantumEncryptedData:
    """Encrypted data with quantum security"""
    ciphertext: bytes
    algorithm: EncryptionAlgorithm
    key_id: str
    nonce: Optional[bytes] = None
    tag: Optional[bytes] = None
    quantum_signature: Optional[bytes] = None

class QuantumEncryption:
    """
    Advanced quantum encryption system for COWN
    """
    
    def __init__(self):
        self.qkd_manager = qkd_manager
        self.encryption_count = 0
        self.decryption_count = 0
        self.active_keys = set()
        
    def generate_quantum_key(self, alice_id: str, bob_id: str, 
                           key_length: int = 256, 
                           protocol: ProtocolType = ProtocolType.BB84) -> QuantumKey:
        """Generate quantum key using specified protocol"""
        if protocol == ProtocolType.BB84:
            session = self.qkd_manager.start_bb84_session(alice_id, bob_id, key_length)
        elif protocol == ProtocolType.BB84_DECOY:
            session = self.qkd_manager.start_enhanced_bb84_session(alice_id, bob_id, key_length)
        elif protocol == ProtocolType.SARG04:
            session = self.qkd_manager.start_sarg04_session(alice_id, bob_id, key_length)
        elif protocol == ProtocolType.E91:
            session = self.qkd_manager.start_e91_session(alice_id, bob_id, key_length)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
        
        self.active_keys.add(session.quantum_key.key_id)
        return session.quantum_key
    
    def quantum_otp_encrypt(self, message: bytes, quantum_key: QuantumKey) -> QuantumEncryptedData:
        """One-Time Pad encryption with quantum key"""
        key_bytes = quantum_key.final_key
        
        # Extend key if needed
        if len(key_bytes) < len(message):
            key_bytes = (key_bytes * ((len(message) // len(key_bytes)) + 1))[:len(message)]
        
        # XOR encryption
        ciphertext = bytes(a ^ b for a, b in zip(message, key_bytes))
        
        return QuantumEncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.QUANTUM_OTP,
            key_id=quantum_key.key_id
        )
    
    def quantum_otp_decrypt(self, encrypted_data: QuantumEncryptedData, 
                           quantum_key: QuantumKey) -> bytes:
        """One-Time Pad decryption"""
        key_bytes = quantum_key.final_key
        
        # Extend key if needed
        if len(key_bytes) < len(encrypted_data.ciphertext):
            key_bytes = (key_bytes * ((len(encrypted_data.ciphertext) // len(key_bytes)) + 1))[:len(encrypted_data.ciphertext)]
        
        # XOR decryption
        plaintext = bytes(a ^ b for a, b in zip(encrypted_data.ciphertext, key_bytes))
        
        return plaintext
    
    def aes_quantum_encrypt(self, message: bytes, quantum_key: QuantumKey) -> QuantumEncryptedData:
        """AES encryption enhanced with quantum key"""
        # Derive AES key from quantum key
        aes_key = self._derive_aes_key(quantum_key.final_key)
        
        # Generate random IV
        iv = secrets.token_bytes(16)
        
        # AES encryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Pad message to block size
        padding_len = 16 - (len(message) % 16)
        padded_message = message + bytes([padding_len] * padding_len)
        
        ciphertext = encryptor.update(padded_message) + encryptor.finalize()
        
        return QuantumEncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.AES_QUANTUM,
            key_id=quantum_key.key_id,
            nonce=iv
        )
    
    def aes_quantum_decrypt(self, encrypted_data: QuantumEncryptedData, 
                           quantum_key: QuantumKey) -> bytes:
        """AES decryption with quantum key"""
        aes_key = self._derive_aes_key(quantum_key.final_key)
        
        # AES decryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(encrypted_data.nonce), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_plaintext = decryptor.update(encrypted_data.ciphertext) + decryptor.finalize()
        
        # Remove padding
        padding_len = padded_plaintext[-1]
        plaintext = padded_plaintext[:-padding_len]
        
        return plaintext
    
    def chacha20_quantum_encrypt(self, message: bytes, quantum_key: QuantumKey) -> QuantumEncryptedData:
        """ChaCha20-Poly1305 encryption with quantum key"""
        chacha_key = self._derive_chacha_key(quantum_key.final_key)
        
        # Generate random nonce
        nonce = secrets.token_bytes(12)
        
        # ChaCha20-Poly1305 encryption
        cipher = ChaCha20Poly1305(chacha_key)
        ciphertext = cipher.encrypt(nonce, message, None)
        
        return QuantumEncryptedData(
            ciphertext=ciphertext,
            algorithm=EncryptionAlgorithm.CHACHA20_QUANTUM,
            key_id=quantum_key.key_id,
            nonce=nonce
        )
    
    def chacha20_quantum_decrypt(self, encrypted_data: QuantumEncryptedData, 
                                quantum_key: QuantumKey) -> bytes:
        """ChaCha20-Poly1305 decryption"""
        chacha_key = self._derive_chacha_key(quantum_key.final_key)
        
        # ChaCha20-Poly1305 decryption
        cipher = ChaCha20Poly1305(chacha_key)
        plaintext = cipher.decrypt(encrypted_data.nonce, encrypted_data.ciphertext, None)
        
        return plaintext
    
    def _derive_aes_key(self, quantum_key: bytes) -> bytes:
        """Derive AES key from quantum key"""
        return hashlib.sha256(quantum_key + b"AES").digest()[:32]
    
    def _derive_chacha_key(self, quantum_key: bytes) -> bytes:
        """Derive ChaCha20 key from quantum key"""
        return hashlib.sha256(quantum_key + b"CHACHA20").digest()[:32]
    
    def _generate_quantum_signature(self, data: bytes, quantum_key: QuantumKey) -> bytes:
        """Generate quantum-enhanced signature"""
        signature_key = hashlib.sha256(quantum_key.final_key + b"SIGNATURE").digest()
        return hmac.new(signature_key, data, hashlib.sha256).digest()
    
    def _verify_quantum_signature(self, data: bytes, quantum_key: QuantumKey, 
                                 signature: bytes) -> bool:
        """Verify quantum signature"""
        expected_signature = self._generate_quantum_signature(data, quantum_key)
        return hmac.compare_digest(expected_signature, signature)
    
    def encrypt_message(self, message: str, alice_id: str, bob_id: str,
                       algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_QUANTUM,
                       protocol: ProtocolType = ProtocolType.BB84) -> Tuple[QuantumEncryptedData, EncryptionMetrics]:
        """Encrypt message with quantum security"""
        start_time = time.time()
        
        # Generate quantum key
        quantum_key = self.generate_quantum_key(alice_id, bob_id, 256, protocol)
        
        # Convert message to bytes
        message_bytes = message.encode('utf-8')
        
        # Encrypt based on algorithm
        if algorithm == EncryptionAlgorithm.QUANTUM_OTP:
            encrypted_data = self.quantum_otp_encrypt(message_bytes, quantum_key)
        elif algorithm == EncryptionAlgorithm.AES_QUANTUM:
            encrypted_data = self.aes_quantum_encrypt(message_bytes, quantum_key)
        elif algorithm == EncryptionAlgorithm.CHACHA20_QUANTUM:
            encrypted_data = self.chacha20_quantum_encrypt(message_bytes, quantum_key)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Add quantum signature
        encrypted_data.quantum_signature = self._generate_quantum_signature(
            encrypted_data.ciphertext, quantum_key
        )
        
        encryption_time = time.time() - start_time
        self.encryption_count += 1
        
        # Calculate metrics
        metrics = EncryptionMetrics(
            algorithm=algorithm,
            key_length=quantum_key.length,
            message_length=len(message_bytes),
            encryption_time=encryption_time,
            security_level=quantum_key.security_level,
            quantum_enhanced=True
        )
        
        return encrypted_data, metrics
    
    def decrypt_message(self, encrypted_data: QuantumEncryptedData, 
                       key_id: str) -> str:
        """Decrypt message with quantum key"""
        # Get quantum key
        quantum_key = self.qkd_manager.get_quantum_key(key_id)
        if not quantum_key:
            raise ValueError(f"Quantum key not found: {key_id}")
        
        # Verify quantum signature
        if encrypted_data.quantum_signature:
            if not self._verify_quantum_signature(
                encrypted_data.ciphertext, quantum_key, encrypted_data.quantum_signature
            ):
                raise ValueError("Quantum signature verification failed")
        
        # Decrypt based on algorithm
        if encrypted_data.algorithm == EncryptionAlgorithm.QUANTUM_OTP:
            plaintext_bytes = self.quantum_otp_decrypt(encrypted_data, quantum_key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.AES_QUANTUM:
            plaintext_bytes = self.aes_quantum_decrypt(encrypted_data, quantum_key)
        elif encrypted_data.algorithm == EncryptionAlgorithm.CHACHA20_QUANTUM:
            plaintext_bytes = self.chacha20_quantum_decrypt(encrypted_data, quantum_key)
        else:
            raise ValueError(f"Unsupported algorithm: {encrypted_data.algorithm}")
        
        self.decryption_count += 1
        
        return plaintext_bytes.decode('utf-8')
    
    def get_encryption_statistics(self) -> Dict[str, Any]:
        """Get encryption system statistics"""
        return {
            "total_encryptions": self.encryption_count,
            "total_decryptions": self.decryption_count,
            "total_active_keys": len(self.active_keys),
            "supported_algorithms": [alg.value for alg in EncryptionAlgorithm],
            "supported_protocols": [prot.value for prot in ProtocolType]
        }

# Global quantum encryption instance
quantum_encryption = QuantumEncryption()
