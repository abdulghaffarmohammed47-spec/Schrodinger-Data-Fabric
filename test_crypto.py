"""
Unit tests for cryptographic engine
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.security.crypto_engine import (
    SymmetricEncryption, KeyDerivation, HybridEncryption,
    ShamirSecretSharing, IntegrityVerification
)


class TestSymmetricEncryption:
    """Test ChaCha20-Poly1305 encryption"""
    
    def test_generate_key(self):
        """Test key generation"""
        key = SymmetricEncryption.generate_key()
        assert len(key) == 32
        assert isinstance(key, bytes)
    
    def test_encrypt_decrypt(self):
        """Test encryption and decryption"""
        key = SymmetricEncryption.generate_key()
        plaintext = b"Hello, World! This is a secret message."
        
        # Encrypt
        encrypted = SymmetricEncryption.encrypt(plaintext, key)
        assert "nonce" in encrypted
        assert "ciphertext" in encrypted
        assert "algorithm" in encrypted
        
        # Decrypt
        decrypted = SymmetricEncryption.decrypt(encrypted, key)
        assert decrypted == plaintext
    
    def test_encrypt_with_aad(self):
        """Test encryption with associated data"""
        key = SymmetricEncryption.generate_key()
        plaintext = b"Secret data"
        aad = b"Additional authenticated data"
        
        encrypted = SymmetricEncryption.encrypt(plaintext, key, aad)
        decrypted = SymmetricEncryption.decrypt(encrypted, key, aad)
        
        assert decrypted == plaintext


class TestKeyDerivation:
    """Test Argon2id key derivation"""
    
    def test_derive_key(self):
        """Test key derivation"""
        password = "secure_password_123"
        key, salt = KeyDerivation.derive_key(password)
        
        assert len(key) == 32
        assert len(salt) == 16
        assert isinstance(key, bytes)
        assert isinstance(salt, bytes)
    
    def test_derive_key_consistency(self):
        """Test key derivation consistency"""
        password = "test_password"
        key1, salt = KeyDerivation.derive_key(password)
        key2, _ = KeyDerivation.derive_key(password, salt)
        
        assert key1 == key2


class TestHybridEncryption:
    """Test RSA + ChaCha20 hybrid encryption"""
    
    def test_generate_rsa_keypair(self):
        """Test RSA key pair generation"""
        private_key, public_key = HybridEncryption.generate_rsa_keypair()
        
        assert b"-----BEGIN PRIVATE KEY-----" in private_key
        assert b"-----BEGIN PUBLIC KEY-----" in public_key
    
    def test_hybrid_encrypt_decrypt(self):
        """Test hybrid encryption and decryption"""
        hybrid = HybridEncryption()
        private_key, public_key = hybrid.generate_rsa_keypair()
        
        plaintext = b"Sensitive data that needs protection"
        
        # Encrypt
        encrypted = hybrid.encrypt_hybrid(plaintext, public_key)
        assert "encrypted_key" in encrypted
        assert "encrypted_data" in encrypted
        
        # Decrypt
        decrypted = hybrid.decrypt_hybrid(encrypted, private_key)
        assert decrypted == plaintext


class TestShamirSecretSharing:
    """Test Shamir's Secret Sharing"""
    
    def test_split_secret(self):
        """Test secret splitting"""
        secret = b"This is a secret that will be split into shares"
        threshold = 3
        shares_count = 5
        
        shards = ShamirSecretSharing.split_secret(secret, threshold, shares_count)
        
        assert len(shards) == shares_count
        for shard in shards:
            assert "data" in shard
            assert "metadata" in shard
            assert shard["metadata"]["threshold"] == threshold
            assert shard["metadata"]["total"] == shares_count
    
    def test_reconstruct_secret(self):
        """Test secret reconstruction"""
        secret = b"Test secret for reconstruction"
        threshold = 3
        shares_count = 5
        
        shards = ShamirSecretSharing.split_secret(secret, threshold, shares_count)
        
        # Reconstruct with threshold shards
        reconstructed = ShamirSecretSharing.reconstruct_secret(shards[:threshold])
        assert reconstructed == secret
    
    def test_insufficient_shares(self):
        """Test reconstruction with insufficient shares"""
        secret = b"Secret data"
        threshold = 3
        shares_count = 5
        
        shards = ShamirSecretSharing.split_secret(secret, threshold, shares_count)
        
        # Try to reconstruct with fewer than threshold shards
        with pytest.raises(ValueError):
            ShamirSecretSharing.reconstruct_secret(shards[:threshold-1])


class TestIntegrityVerification:
    """Test HMAC and Merkle tree integrity"""
    
    def test_compute_hmac(self):
        """Test HMAC computation"""
        data = b"Important data"
        key = b"secret_key"
        
        hmac_sig = IntegrityVerification.compute_hmac(data, key)
        assert isinstance(hmac_sig, str)
        assert len(hmac_sig) == 64  # SHA256 hex length
    
    def test_verify_hmac(self):
        """Test HMAC verification"""
        data = b"Important data"
        key = b"secret_key"
        
        hmac_sig = IntegrityVerification.compute_hmac(data, key)
        assert IntegrityVerification.verify_hmac(data, key, hmac_sig)
    
    def test_verify_hmac_tampered(self):
        """Test HMAC verification with tampered data"""
        data = b"Important data"
        key = b"secret_key"
        
        hmac_sig = IntegrityVerification.compute_hmac(data, key)
        tampered_data = b"Tampered data"
        
        assert not IntegrityVerification.verify_hmac(tampered_data, key, hmac_sig)
    
    def test_merkle_root(self):
        """Test Merkle tree root computation"""
        blocks = [
            b"Block 1",
            b"Block 2",
            b"Block 3",
            b"Block 4"
        ]
        
        root = IntegrityVerification.compute_merkle_root(blocks)
        assert isinstance(root, str)
        assert len(root) == 64  # SHA256 hex length
    
    def test_merkle_root_consistency(self):
        """Test Merkle tree root consistency"""
        blocks = [b"Block 1", b"Block 2", b"Block 3"]
        
        root1 = IntegrityVerification.compute_merkle_root(blocks)
        root2 = IntegrityVerification.compute_merkle_root(blocks)
        
        assert root1 == root2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
