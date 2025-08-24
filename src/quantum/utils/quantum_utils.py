"""
COWN Quantum Utilities
Các tiện ích hỗ trợ cho hệ thống lượng tử COWN

Features:
- Quantum state manipulation utilities
- Key generation and validation
- Error analysis and correction tools
- Security metrics calculation
- Random number generation
- Quantum protocol helpers
- Performance benchmarking utilities
"""

import os
import sys
import time
import hashlib
import secrets
import numpy as np
import logging
from typing import List, Dict, Any, Tuple, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json
import base64

try:
    import pennylane as qml
    PENNYLANE_AVAILABLE = True
except ImportError:
    PENNYLANE_AVAILABLE = False
    print("Warning: PennyLane not available. Some quantum features may be limited.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantumBasis(Enum):
    """Quantum measurement bases"""
    RECTILINEAR = 0  # {|0⟩, |1⟩}
    DIAGONAL = 1     # {|+⟩, |-⟩}
    CIRCULAR = 2     # {|R⟩, |L⟩}

class SecurityLevel(Enum):
    """Security levels for quantum operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class QuantumState:
    """Quantum state representation"""
    amplitudes: np.ndarray
    basis: QuantumBasis
    is_entangled: bool = False
    fidelity: float = 1.0

@dataclass
class ErrorStatistics:
    """Error analysis statistics"""
    total_bits: int
    error_count: int
    error_rate: float
    confidence_interval: Tuple[float, float]
    statistical_significance: float

@dataclass
class SecurityMetrics:
    """Security analysis metrics"""
    entropy: float
    mutual_information: float
    eve_information_bound: float
    privacy_amplification_ratio: float
    security_parameter: float

class QuantumUtils:
    """
    Comprehensive quantum utilities for COWN system
    """
    
    def __init__(self):
        self.rng = secrets.SystemRandom()
        
    # =================================================================
    # RANDOM NUMBER GENERATION
    # =================================================================
    
    def generate_cryptographic_bits(self, length: int) -> List[int]:
        """Generate cryptographically secure random bits"""
        return [self.rng.getrandbits(1) for _ in range(length)]
    
    def generate_random_bases(self, length: int, num_bases: int = 2) -> List[int]:
        """Generate random measurement bases"""
        return [self.rng.randrange(num_bases) for _ in range(length)]
    
    def generate_quantum_seed(self, length: int = 256) -> bytes:
        """Generate quantum-enhanced random seed"""
        # Use system entropy + time-based entropy
        entropy_sources = [
            secrets.token_bytes(length // 4),
            str(time.time_ns()).encode(),
            str(os.urandom(32)).encode(),
            hashlib.sha256(str(self.rng.getstate()).encode()).digest()
        ]
        
        combined = b''.join(entropy_sources)
        return hashlib.sha256(combined).digest()[:length]
    
    # =================================================================
    # QUANTUM STATE OPERATIONS
    # =================================================================
    
    def create_qubit_state(self, bit: int, basis: QuantumBasis) -> QuantumState:
        """Create single qubit state in specified basis"""
        if basis == QuantumBasis.RECTILINEAR:
            # Z basis: |0⟩ or |1⟩
            if bit == 0:
                amplitudes = np.array([1.0, 0.0], dtype=complex)
            else:
                amplitudes = np.array([0.0, 1.0], dtype=complex)
        
        elif basis == QuantumBasis.DIAGONAL:
            # X basis: |+⟩ or |-⟩
            if bit == 0:
                amplitudes = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
            else:
                amplitudes = np.array([1/np.sqrt(2), -1/np.sqrt(2)], dtype=complex)
        
        elif basis == QuantumBasis.CIRCULAR:
            # Y basis: |R⟩ or |L⟩
            if bit == 0:
                amplitudes = np.array([1/np.sqrt(2), 1j/np.sqrt(2)], dtype=complex)
            else:
                amplitudes = np.array([1/np.sqrt(2), -1j/np.sqrt(2)], dtype=complex)
        
        return QuantumState(amplitudes=amplitudes, basis=basis)
    
    def create_bell_state(self, bell_type: int = 0) -> QuantumState:
        """Create Bell state pair"""
        # Bell states: |Φ+⟩, |Φ-⟩, |Ψ+⟩, |Ψ-⟩
        if bell_type == 0:  # |Φ+⟩ = (|00⟩ + |11⟩)/√2
            amplitudes = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        elif bell_type == 1:  # |Φ-⟩ = (|00⟩ - |11⟩)/√2
            amplitudes = np.array([1/np.sqrt(2), 0, 0, -1/np.sqrt(2)], dtype=complex)
        elif bell_type == 2:  # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
            amplitudes = np.array([0, 1/np.sqrt(2), 1/np.sqrt(2), 0], dtype=complex)
        else:  # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
            amplitudes = np.array([0, 1/np.sqrt(2), -1/np.sqrt(2), 0], dtype=complex)
        
        return QuantumState(amplitudes=amplitudes, basis=QuantumBasis.RECTILINEAR, is_entangled=True)
    
    def measure_qubit(self, state: QuantumState, measurement_basis: QuantumBasis) -> Tuple[int, float]:
        """
        Measure qubit in specified basis
        Returns: (measurement_result, probability)
        """
        # Calculate measurement probabilities
        if measurement_basis == state.basis:
            # Same basis - deterministic result
            prob_0 = abs(state.amplitudes[0])**2
            prob_1 = abs(state.amplitudes[1])**2
        else:
            # Different basis - transform amplitudes
            if state.basis == QuantumBasis.RECTILINEAR and measurement_basis == QuantumBasis.DIAGONAL:
                # Z→X measurement
                prob_0 = 0.5  # Always 50-50 for orthogonal bases
                prob_1 = 0.5
            elif state.basis == QuantumBasis.DIAGONAL and measurement_basis == QuantumBasis.RECTILINEAR:
                # X→Z measurement
                prob_0 = 0.5
                prob_1 = 0.5
            else:
                # General case
                prob_0 = 0.5
                prob_1 = 0.5
        
        # Random measurement outcome
        measurement = 0 if self.rng.random() < prob_0 else 1
        probability = prob_0 if measurement == 0 else prob_1
        
        return measurement, probability
    
    def calculate_fidelity(self, state1: QuantumState, state2: QuantumState) -> float:
        """Calculate fidelity between two quantum states"""
        return abs(np.vdot(state1.amplitudes, state2.amplitudes))**2
    
    # =================================================================
    # KEY SIFTING AND ERROR ANALYSIS
    # =================================================================
    
    def sift_quantum_key(self, alice_bits: List[int], bob_bits: List[int],
                        alice_bases: List[int], bob_bases: List[int]) -> Tuple[List[int], List[int], List[int]]:
        """
        Perform key sifting - keep only matching basis measurements
        Returns: (alice_sifted, bob_sifted, matching_indices)
        """
        alice_sifted = []
        bob_sifted = []
        matching_indices = []
        
        for i, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases)):
            if a_basis == b_basis:
                alice_sifted.append(alice_bits[i])
                bob_sifted.append(bob_bits[i])
                matching_indices.append(i)
        
        return alice_sifted, bob_sifted, matching_indices
    
    def calculate_error_rate(self, alice_bits: List[int], bob_bits: List[int], 
                           sample_fraction: float = 0.5) -> ErrorStatistics:
        """
        Calculate quantum bit error rate (QBER) with statistical analysis
        """
        if len(alice_bits) != len(bob_bits) or len(alice_bits) == 0:
            return ErrorStatistics(0, 0, 1.0, (0.0, 1.0), 0.0)
        
        total_bits = len(alice_bits)
        
        # Use subset for error estimation
        sample_size = max(1, int(total_bits * sample_fraction))
        sample_indices = self.rng.sample(range(total_bits), sample_size)
        
        # Count errors in sample
        errors = sum(1 for i in sample_indices if alice_bits[i] != bob_bits[i])
        error_rate = errors / sample_size
        
        # Calculate confidence interval (Wilson score)
        if sample_size > 0:
            z = 1.96  # 95% confidence
            n = sample_size
            p = error_rate
            
            center = (p + z*z/(2*n)) / (1 + z*z/n)
            margin = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
            
            confidence_interval = (max(0, center - margin), min(1, center + margin))
            
            # Statistical significance (z-score)
            if p > 0 and p < 1:
                significance = abs(p - 0.5) / np.sqrt(p * (1-p) / n)
            else:
                significance = 0.0
        else:
            confidence_interval = (0.0, 1.0)
            significance = 0.0
        
        return ErrorStatistics(
            total_bits=total_bits,
            error_count=errors,
            error_rate=error_rate,
            confidence_interval=confidence_interval,
            statistical_significance=significance
        )
    
    def estimate_eve_information(self, error_rate: float) -> float:
        """
        Estimate maximum information available to eavesdropper
        Based on quantum no-cloning theorem constraints
        """
        if error_rate <= 0:
            return 0.0
        elif error_rate >= 0.5:
            return 1.0
        else:
            # Shannon entropy of error distribution
            h_error = -error_rate * np.log2(error_rate) - (1-error_rate) * np.log2(1-error_rate)
            return min(1.0, 2 * h_error)
    
    # =================================================================
    # PRIVACY AMPLIFICATION AND ERROR CORRECTION
    # =================================================================
    
    def privacy_amplification(self, key: List[int], target_length: int, 
                            eve_info: float = 0.0) -> bytes:
        """
        Perform privacy amplification using universal hash functions
        """
        if len(key) < target_length:
            # Extend key if too short
            key = key * ((target_length // len(key)) + 1)
        
        # Convert to bytes
        key_bytes = bytes(key[:max(target_length, len(key))])
        
        # Calculate number of hash rounds based on Eve's information
        security_parameter = max(1.0 - eve_info, 0.1)
        rounds = max(1, int(np.ceil(-np.log2(security_parameter))))
        
        # Multi-round hashing
        final_key = b""
        for round_num in range(rounds):
            # Combine key with round number for different hash inputs
            hash_input = key_bytes + round_num.to_bytes(4, 'big')
            round_hash = hashlib.sha256(hash_input).digest()
            final_key += round_hash
        
        return final_key[:target_length]
    
    def hamming_error_correction(self, bits: List[int]) -> List[int]:
        """
        Simple Hamming error correction for demonstration
        """
        # This is a simplified version - real implementations would be more complex
        corrected_bits = bits.copy()
        
        # Basic parity check correction
        for i in range(0, len(bits) - 2, 3):
            if i + 2 < len(bits):
                # Simple majority vote for 3-bit groups
                group = bits[i:i+3]
                majority = 1 if sum(group) >= 2 else 0
                corrected_bits[i:i+3] = [majority] * 3
        
        return corrected_bits
    
    # =================================================================
    # SECURITY METRICS AND ANALYSIS
    # =================================================================
    
    def calculate_entropy(self, data: Union[List[int], bytes]) -> float:
        """Calculate Shannon entropy"""
        if isinstance(data, bytes):
            data = list(data)
        
        if not data:
            return 0.0
        
        # Count occurrences
        counts = {}
        for item in data:
            counts[item] = counts.get(item, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        total = len(data)
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    def calculate_mutual_information(self, alice_bits: List[int], bob_bits: List[int]) -> float:
        """Calculate mutual information between Alice and Bob's keys"""
        if len(alice_bits) != len(bob_bits) or not alice_bits:
            return 0.0
        
        # Calculate joint probabilities
        n = len(alice_bits)
        p00 = sum(1 for a, b in zip(alice_bits, bob_bits) if a == 0 and b == 0) / n
        p01 = sum(1 for a, b in zip(alice_bits, bob_bits) if a == 0 and b == 1) / n
        p10 = sum(1 for a, b in zip(alice_bits, bob_bits) if a == 1 and b == 0) / n
        p11 = sum(1 for a, b in zip(alice_bits, bob_bits) if a == 1 and b == 1) / n
        
        # Marginal probabilities
        pa0 = p00 + p01
        pa1 = p10 + p11
        pb0 = p00 + p10
        pb1 = p01 + p11
        
        # Mutual information
        mi = 0.0
        for pab, pa, pb in [(p00, pa0, pb0), (p01, pa0, pb1), (p10, pa1, pb0), (p11, pa1, pb1)]:
            if pab > 0 and pa > 0 and pb > 0:
                mi += pab * np.log2(pab / (pa * pb))
        
        return mi
    
    def analyze_security(self, alice_bits: List[int], bob_bits: List[int], 
                        error_rate: float) -> SecurityMetrics:
        """Comprehensive security analysis"""
        # Calculate entropy
        alice_entropy = self.calculate_entropy(alice_bits)
        bob_entropy = self.calculate_entropy(bob_bits)
        
        # Mutual information
        mutual_info = self.calculate_mutual_information(alice_bits, bob_bits)
        
        # Eve's information bound
        eve_info_bound = self.estimate_eve_information(error_rate)
        
        # Privacy amplification ratio
        if alice_entropy > 0:
            privacy_ratio = max(0.0, (alice_entropy - eve_info_bound) / alice_entropy)
        else:
            privacy_ratio = 0.0
        
        # Overall security parameter
        security_param = mutual_info * (1 - eve_info_bound) * privacy_ratio
        
        return SecurityMetrics(
            entropy=alice_entropy,
            mutual_information=mutual_info,
            eve_information_bound=eve_info_bound,
            privacy_amplification_ratio=privacy_ratio,
            security_parameter=security_param
        )
    
    # =================================================================
    # PROTOCOL HELPERS
    # =================================================================
    
    def generate_bb84_states(self, bits: List[int], bases: List[int]) -> List[QuantumState]:
        """Generate BB84 quantum states"""
        states = []
        for bit, basis in zip(bits, bases):
            if basis == 0:
                state = self.create_qubit_state(bit, QuantumBasis.RECTILINEAR)
            else:
                state = self.create_qubit_state(bit, QuantumBasis.DIAGONAL)
            states.append(state)
        return states
    
    def simulate_quantum_channel(self, states: List[QuantumState], 
                                noise_probability: float = 0.0) -> List[QuantumState]:
        """Simulate noisy quantum channel"""
        noisy_states = []
        for state in states:
            if self.rng.random() < noise_probability:
                # Apply bit flip noise
                if len(state.amplitudes) == 2:
                    noisy_amplitudes = np.array([state.amplitudes[1], state.amplitudes[0]])
                    noisy_state = QuantumState(
                        amplitudes=noisy_amplitudes,
                        basis=state.basis,
                        fidelity=state.fidelity * (1 - noise_probability)
                    )
                else:
                    noisy_state = state
                noisy_states.append(noisy_state)
            else:
                noisy_states.append(state)
        return noisy_states
    
    def chsh_bell_test(self, correlations: Dict[Tuple[int, int], float]) -> float:
        """
        Perform CHSH Bell inequality test
        Input: correlations[(alice_setting, bob_setting)] = correlation_value
        """
        # CHSH inequality: |E(a,b) - E(a,b') + E(a',b) + E(a',b')| ≤ 2
        # For quantum mechanics, max violation gives 2√2 ≈ 2.828
        
        try:
            chsh_value = abs(
                correlations.get((0, 0), 0) - correlations.get((0, 1), 0) +
                correlations.get((1, 0), 0) + correlations.get((1, 1), 0)
            )
            return chsh_value
        except:
            return 0.0
    
    # =================================================================
    # BENCHMARKING AND TESTING
    # =================================================================
    
    def benchmark_protocol(self, protocol_func, iterations: int = 100, 
                          key_length: int = 256) -> Dict[str, float]:
        """Benchmark quantum protocol performance"""
        times = []
        success_count = 0
        error_rates = []
        security_levels = []
        
        for _ in range(iterations):
            try:
                start_time = time.time()
                result = protocol_func(key_length)
                execution_time = time.time() - start_time
                
                times.append(execution_time)
                success_count += 1
                
                if hasattr(result, 'error_rate'):
                    error_rates.append(result.error_rate)
                if hasattr(result, 'security_level'):
                    security_levels.append(result.security_level)
                    
            except Exception as e:
                logger.warning(f"Protocol execution failed: {e}")
        
        return {
            "success_rate": success_count / iterations,
            "average_time": np.mean(times) if times else 0.0,
            "min_time": np.min(times) if times else 0.0,
            "max_time": np.max(times) if times else 0.0,
            "std_time": np.std(times) if times else 0.0,
            "average_error_rate": np.mean(error_rates) if error_rates else 0.0,
            "average_security": np.mean(security_levels) if security_levels else 0.0
        }
    
    def test_randomness(self, data: List[int], test_type: str = "all") -> Dict[str, Any]:
        """Test randomness quality of generated data"""
        if not data:
            return {"error": "No data provided"}
        
        results = {}
        
        # Basic statistics
        ones = sum(data)
        zeros = len(data) - ones
        bias = abs(ones - zeros) / len(data)
        
        results["basic"] = {
            "length": len(data),
            "ones": ones,
            "zeros": zeros,
            "bias": bias,
            "entropy": self.calculate_entropy(data)
        }
        
        # Runs test
        if test_type in ["all", "runs"]:
            runs = 1
            for i in range(1, len(data)):
                if data[i] != data[i-1]:
                    runs += 1
            
            expected_runs = 2 * ones * zeros / len(data) + 1
            runs_variance = (expected_runs - 1) * (expected_runs - 2) / (len(data) - 1)
            
            if runs_variance > 0:
                runs_z_score = abs(runs - expected_runs) / np.sqrt(runs_variance)
            else:
                runs_z_score = 0
            
            results["runs_test"] = {
                "runs": runs,
                "expected_runs": expected_runs,
                "z_score": runs_z_score,
                "p_value": 2 * (1 - 0.5 * (1 + np.sign(runs_z_score) * np.sqrt(1 - np.exp(-2 * runs_z_score**2 / np.pi))))
            }
        
        # Serial correlation test
        if test_type in ["all", "serial"] and len(data) > 1:
            autocorr = np.corrcoef(data[:-1], data[1:])[0, 1] if len(data) > 2 else 0
            results["serial_correlation"] = {
                "autocorrelation": autocorr,
                "is_random": abs(autocorr) < 0.1
            }
        
        return results
    
    # =================================================================
    # UTILITY FUNCTIONS
    # =================================================================
    
    def bits_to_bytes(self, bits: List[int]) -> bytes:
        """Convert bit list to bytes"""
        # Pad to multiple of 8
        padded_bits = bits + [0] * (8 - len(bits) % 8) if len(bits) % 8 != 0 else bits
        
        byte_array = []
        for i in range(0, len(padded_bits), 8):
            byte_bits = padded_bits[i:i+8]
            byte_value = sum(bit * (2 ** (7-j)) for j, bit in enumerate(byte_bits))
            byte_array.append(byte_value)
        
        return bytes(byte_array)
    
    def bytes_to_bits(self, data: bytes) -> List[int]:
        """Convert bytes to bit list"""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits
    
    def encode_base64(self, data: bytes) -> str:
        """Base64 encode binary data"""
        return base64.b64encode(data).decode('utf-8')
    
    def decode_base64(self, encoded: str) -> bytes:
        """Base64 decode string to binary"""
        return base64.b64decode(encoded.encode('utf-8'))
    
    def format_hex(self, data: bytes, group_size: int = 8) -> str:
        """Format binary data as grouped hex"""
        hex_str = data.hex().upper()
        return ' '.join(hex_str[i:i+group_size] for i in range(0, len(hex_str), group_size))
    
    def validate_quantum_parameters(self, **kwargs) -> Dict[str, bool]:
        """Validate quantum protocol parameters"""
        validation = {}
        
        # Key length validation
        if 'key_length' in kwargs:
            key_len = kwargs['key_length']
            validation['key_length_valid'] = isinstance(key_len, int) and 64 <= key_len <= 4096
        
        # Error rate validation  
        if 'error_rate' in kwargs:
            error_rate = kwargs['error_rate']
            validation['error_rate_valid'] = isinstance(error_rate, (int, float)) and 0 <= error_rate <= 0.5
        
        # Security level validation
        if 'security_level' in kwargs:
            sec_level = kwargs['security_level']
            validation['security_level_valid'] = isinstance(sec_level, (int, float)) and 0 <= sec_level <= 1
        
        return validation
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get quantum system information"""
        return {
            "pennylane_available": PENNYLANE_AVAILABLE,
            "numpy_version": np.__version__,
            "python_version": sys.version,
            "entropy_sources": ["secrets", "os.urandom", "time.time_ns"],
            "supported_protocols": ["BB84", "Enhanced BB84", "SARG04", "E91"],
            "security_levels": [level.value for level in SecurityLevel],
            "measurement_bases": [basis.name for basis in QuantumBasis]
        }

# Global quantum utilities instance
quantum_utils = QuantumUtils()

# Convenience functions
def generate_random_bits(length: int) -> List[int]:
    """Generate cryptographically secure random bits"""
    return quantum_utils.generate_cryptographic_bits(length)

def calculate_qber(alice_bits: List[int], bob_bits: List[int]) -> float:
    """Calculate quantum bit error rate"""
    return quantum_utils.calculate_error_rate(alice_bits, bob_bits).error_rate

def sift_key(alice_bits: List[int], bob_bits: List[int], 
            alice_bases: List[int], bob_bases: List[int]) -> Tuple[List[int], List[int]]:
    """Perform key sifting"""
    alice_sifted, bob_sifted, _ = quantum_utils.sift_quantum_key(
        alice_bits, bob_bits, alice_bases, bob_bases
    )
    return alice_sifted, bob_sifted

def analyze_key_security(alice_bits: List[int], bob_bits: List[int]) -> Dict[str, float]:
    """Analyze key security"""
    error_stats = quantum_utils.calculate_error_rate(alice_bits, bob_bits)
    security_metrics = quantum_utils.analyze_security(alice_bits, bob_bits, error_stats.error_rate)
    
    return {
        "error_rate": error_stats.error_rate,
        "entropy": security_metrics.entropy,
        "mutual_information": security_metrics.mutual_information,
        "security_parameter": security_metrics.security_parameter
    }

def test_bell_inequality(correlations: Dict[Tuple[int, int], float]) -> Dict[str, float]:
    """Test Bell inequality violation"""
    chsh_value = quantum_utils.chsh_bell_test(correlations)
    classical_limit = 2.0
    quantum_limit = 2 * np.sqrt(2)
    
    return {
        "chsh_value": chsh_value,
        "classical_limit": classical_limit,
        "quantum_limit": quantum_limit,
        "violates_classical": chsh_value > classical_limit,
        "quantum_advantage": max(0, chsh_value - classical_limit)
    }

# Export main utilities
__all__ = [
    'QuantumUtils', 'QuantumBasis', 'SecurityLevel', 'QuantumState',
    'ErrorStatistics', 'SecurityMetrics', 'quantum_utils',
    'generate_random_bits', 'calculate_qber', 'sift_key', 
    'analyze_key_security', 'test_bell_inequality'
]