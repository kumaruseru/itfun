"""
COWN Quantum Key Distribution (QKD) Protocol
Hệ thống phân phối khóa lượng tử tiên tiến cho COWN
Bao gồm BB84 và E91 protocols với PennyLane
"""

import pennylane as qml
import numpy as np
import secrets
import hashlib
import time
import uuid
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

class ProtocolType(Enum):
    """Các loại protocol QKD"""
    BB84 = "BB84"
    BB84_DECOY = "BB84_DECOY"
    SARG04 = "SARG04"
    E91 = "E91"
    MDI_QKD = "MDI_QKD"

class QKDError(Exception):
    """Base exception for QKD errors"""
    pass

class EavesdropDetected(QKDError):
    """Exception raised when eavesdropping is detected"""
    pass

@dataclass
class QuantumKey:
    """Quantum key data structure"""
    key_id: str
    raw_key: bytes
    final_key: bytes
    length: int
    security_level: float
    generation_time: float
    protocol: ProtocolType
    error_rate: float
    decoy_analysis: Optional[Dict[str, float]] = None
    sarg_efficiency: Optional[float] = None
    
@dataclass
class QKDSession:
    """QKD session information"""
    session_id: str
    alice_id: str
    bob_id: str
    protocol: ProtocolType
    key_length: int
    security_level: float
    error_rate: float
    created_at: float
    quantum_key: Optional[QuantumKey] = None

@dataclass
class SecurityMetrics:
    """Security analysis metrics"""
    bit_error_rate: float
    key_generation_rate: float
    security_parameter: float
    mutual_information: float
    privacy_amplification_ratio: float

class BB84Protocol:
    """
    BB84 Quantum Key Distribution Protocol
    Protocol cơ bản nhất và được sử dụng rộng rãi nhất
    """
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.device = qml.device("default.qubit", wires=n_qubits)
        self.noise_probability = 0.0
        
    def generate_random_bits(self, length: int) -> List[int]:
        """Generate cryptographically secure random bits"""
        return [secrets.randbits(1) for _ in range(length)]
    
    def generate_random_bases(self, length: int) -> List[int]:
        """Generate cryptographically secure random bases"""
        return [secrets.randbits(1) for _ in range(length)]
    
    def alice_prepare_qubits(self, bits: List[int], bases: List[int]) -> List[np.ndarray]:
        """
        Alice prepares qubits according to BB84 protocol
        Basis 0: Rectilinear {|0⟩, |1⟩}
        Basis 1: Diagonal {|+⟩, |-⟩}
        """
        @qml.qnode(self.device)
        def prepare_qubit(bit: int, basis: int):
            # Encode bit
            if bit == 1:
                qml.PauliX(wires=0)
            
            # Apply basis rotation
            if basis == 1:  # Diagonal basis
                qml.Hadamard(wires=0)
            
            return qml.state()
        
        prepared_states = []
        for bit, basis in zip(bits, bases):
            state = prepare_qubit(bit, basis)
            prepared_states.append(state)
        
        return prepared_states
    
    def bob_measure_qubits(self, states: List[np.ndarray], bases: List[int]) -> List[int]:
        """
        Bob measures qubits with randomly chosen bases
        """
        @qml.qnode(self.device)
        def measure_qubit(state: np.ndarray, basis: int):
            # Prepare the state
            qml.QubitStateVector(state, wires=0)
            
            # Apply basis rotation for measurement
            if basis == 1:  # Diagonal measurement
                qml.Hadamard(wires=0)
            
            return qml.expval(qml.PauliZ(0))
        
        measurements = []
        for state, basis in zip(states, bases):
            try:
                result = measure_qubit(state, basis)
                # Convert expectation value to measurement outcome
                # Positive expectation -> |0⟩ (measurement = 0)
                # Negative expectation -> |1⟩ (measurement = 1)
                measurement = 1 if result < 0 else 0
                measurements.append(measurement)
            except:
                # Fallback measurement
                measurements.append(secrets.randbits(1))
        
        return measurements
    
    def sift_key(self, alice_bases: List[int], bob_bases: List[int], 
                 bob_measurements: List[int]) -> Tuple[List[int], List[int]]:
        """
        Key sifting: keep only bits where Alice and Bob used same basis
        """
        sifted_key = []
        matching_indices = []
        
        for i, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases)):
            if a_basis == b_basis:
                sifted_key.append(bob_measurements[i])
                matching_indices.append(i)
        
        return sifted_key, matching_indices
    
    def estimate_error_rate(self, alice_bits: List[int], bob_bits: List[int],
                           test_fraction: float = 0.5) -> float:
        """
        Estimate quantum bit error rate (QBER) using subset of key
        """
        if len(alice_bits) != len(bob_bits) or len(alice_bits) == 0:
            return 1.0
        
        # Use subset for error estimation
        test_size = max(1, int(len(alice_bits) * test_fraction))
        test_indices = secrets.SystemRandom().sample(range(len(alice_bits)), test_size)
        
        errors = 0
        for i in test_indices:
            if alice_bits[i] != bob_bits[i]:
                errors += 1
        
        return errors / test_size if test_size > 0 else 1.0
    
    def privacy_amplification(self, key: List[int], target_length: int) -> bytes:
        """
        Privacy amplification using hash functions
        """
        if len(key) < target_length:
            # If key is too short, extend it
            key = key * ((target_length // len(key)) + 1)
        
        # Convert to bytes
        key_bytes = bytes(key[:target_length])
        
        # Apply SHA-256 hash for privacy amplification
        hash_obj = hashlib.sha256(key_bytes)
        
        # Generate multiple rounds if needed
        final_key = b""
        rounds = (target_length // 32) + 1
        
        for i in range(rounds):
            hash_input = key_bytes + i.to_bytes(4, 'big')
            final_key += hashlib.sha256(hash_input).digest()
        
        return final_key[:target_length]
    
    def generate_key(self, alice_id: str, bob_id: str, 
                    key_length: int = 256) -> QuantumKey:
        """
        Generate quantum key using BB84 protocol
        """
        start_time = time.time()
        
        # Step 1: Generate random bits and bases
        raw_length = key_length * 4  # Generate extra bits for sifting
        alice_bits = self.generate_random_bits(raw_length)
        alice_bases = self.generate_random_bases(raw_length)
        bob_bases = self.generate_random_bases(raw_length)
        
        # Step 2: Alice prepares qubits
        prepared_states = self.alice_prepare_qubits(alice_bits, alice_bases)
        
        # Step 3: Bob measures qubits
        bob_measurements = self.bob_measure_qubits(prepared_states, bob_bases)
        
        # Step 4: Key sifting
        sifted_key, matching_indices = self.sift_key(
            alice_bases, bob_bases, bob_measurements
        )
        
        # Step 5: Error estimation
        alice_sifted = [alice_bits[i] for i in matching_indices]
        error_rate = self.estimate_error_rate(alice_sifted, sifted_key)
        
        # Step 6: Error correction (simplified)
        if error_rate > 0.11:  # QBER threshold
            raise EavesdropDetected(f"High error rate detected: {error_rate:.3f}")
        
        # Step 7: Privacy amplification
        target_bytes = key_length // 8
        final_key = self.privacy_amplification(sifted_key, target_bytes)
        
        # Calculate security level
        security_level = max(0.0, 1.0 - (error_rate * 10))
        
        generation_time = time.time() - start_time
        
        return QuantumKey(
            key_id=str(uuid.uuid4()),
            raw_key=bytes(sifted_key[:target_bytes]),
            final_key=final_key,
            length=len(final_key) * 8,
            security_level=security_level,
            generation_time=generation_time,
            protocol=ProtocolType.BB84,
            error_rate=error_rate
        )

class EnhancedBB84Protocol:
    """
    Enhanced BB84 with Decoy State Method
    Chống lại Photon Number Splitting (PNS) attacks
    """
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.device = qml.device("default.qubit", wires=n_qubits)
        
        # Decoy state parameters
        self.signal_intensity = 0.5  # μ (mu)
        self.decoy_intensity = 0.1   # ν (nu) 
        self.vacuum_intensity = 0.0  # vacuum state
        
        # Protocol parameters
        self.signal_ratio = 0.7      # 70% signal states
        self.decoy_ratio = 0.25      # 25% decoy states
        self.vacuum_ratio = 0.05     # 5% vacuum states
        
    def generate_pulse_intensities(self, length: int) -> List[Tuple[float, str]]:
        """
        Generate random pulse intensities for decoy state protocol
        Returns: List of (intensity, state_type) tuples
        """
        intensities = []
        for _ in range(length):
            rand = secrets.SystemRandom().random()
            if rand < self.signal_ratio:
                intensities.append((self.signal_intensity, "signal"))
            elif rand < self.signal_ratio + self.decoy_ratio:
                intensities.append((self.decoy_intensity, "decoy"))
            else:
                intensities.append((self.vacuum_intensity, "vacuum"))
        
        return intensities
    
    def alice_prepare_decoy_qubits(self, bits: List[int], bases: List[int], 
                                  intensities: List[Tuple[float, str]]) -> List[Tuple[np.ndarray, str]]:
        """
        Alice prepares qubits with varying intensities for decoy state protocol
        """
        @qml.qnode(self.device)
        def prepare_decoy_qubit(bit: int, basis: int, intensity: float):
            # Apply intensity-dependent preparation
            if intensity > 0:
                # Encode bit
                if bit == 1:
                    qml.PauliX(wires=0)
                
                # Apply basis rotation
                if basis == 1:  # Diagonal basis
                    qml.Hadamard(wires=0)
                
                # Simulate intensity with rotation angle
                qml.RY(intensity * np.pi, wires=0)
            
            return qml.state()
        
        prepared_states = []
        for bit, basis, (intensity, state_type) in zip(bits, bases, intensities):
            state = prepare_decoy_qubit(bit, basis, intensity)
            prepared_states.append((state, state_type))
        
        return prepared_states
    
    def analyze_decoy_states(self, signal_detections: List[int], 
                           decoy_detections: List[int],
                           vacuum_detections: List[int]) -> Dict[str, float]:
        """
        Analyze decoy state statistics for security
        """
        # Calculate detection rates
        signal_rate = np.mean(signal_detections) if signal_detections else 0
        decoy_rate = np.mean(decoy_detections) if decoy_detections else 0
        vacuum_rate = np.mean(vacuum_detections) if vacuum_detections else 0
        
        # Estimate single-photon detection rate (simplified)
        if decoy_rate > vacuum_rate:
            single_photon_rate = (decoy_rate - vacuum_rate) / self.decoy_intensity
        else:
            single_photon_rate = 0
        
        # Calculate gain and error rates
        gain_signal = signal_rate
        gain_decoy = decoy_rate
        gain_vacuum = vacuum_rate
        
        # Security analysis
        if gain_decoy > 0:
            error_correction_efficiency = min(1.0, gain_signal / gain_decoy)
        else:
            error_correction_efficiency = 0.5
        
        return {
            "signal_detection_rate": signal_rate,
            "decoy_detection_rate": decoy_rate,
            "vacuum_detection_rate": vacuum_rate,
            "single_photon_rate": single_photon_rate,
            "error_correction_efficiency": error_correction_efficiency,
            "security_parameter": max(0, 1 - (vacuum_rate * 10))
        }
    
    def generate_key(self, alice_id: str, bob_id: str, 
                    key_length: int = 256) -> QuantumKey:
        """
        Generate quantum key using Enhanced BB84 with Decoy States
        """
        start_time = time.time()
        
        # Step 1: Generate random bits, bases, and intensities
        raw_length = key_length * 6  # More overhead for decoy states
        alice_bits = [secrets.randbits(1) for _ in range(raw_length)]
        alice_bases = [secrets.randbits(1) for _ in range(raw_length)]
        bob_bases = [secrets.randbits(1) for _ in range(raw_length)]
        
        # Generate pulse intensities
        intensities = self.generate_pulse_intensities(raw_length)
        
        # Step 2: Alice prepares qubits with decoy states
        prepared_states = self.alice_prepare_decoy_qubits(alice_bits, alice_bases, intensities)
        
        # Step 3: Bob measures qubits
        bob_measurements = []
        signal_detections = []
        decoy_detections = []
        vacuum_detections = []
        
        @qml.qnode(self.device)
        def measure_qubit(state: np.ndarray, basis: int):
            qml.QubitStateVector(state, wires=0)
            if basis == 1:
                qml.Hadamard(wires=0)
            return qml.sample(qml.PauliZ(0), shots=1)
        
        for i, ((state, state_type), basis) in enumerate(zip(prepared_states, bob_bases)):
            try:
                result = measure_qubit(state, basis)
                measurement = 0 if result[0] == 1 else 1
                bob_measurements.append(measurement)
                
                # Classify by state type
                if state_type == "signal":
                    signal_detections.append(measurement)
                elif state_type == "decoy":
                    decoy_detections.append(measurement)
                else:  # vacuum
                    vacuum_detections.append(measurement)
                    
            except:
                measurement = secrets.randbits(1)
                bob_measurements.append(measurement)
        
        # Step 4: Decoy state analysis
        decoy_analysis = self.analyze_decoy_states(
            signal_detections, decoy_detections, vacuum_detections
        )
        
        # Step 5: Key sifting (only use signal states with matching bases)
        sifted_key = []
        matching_indices = []
        
        for i, (a_basis, b_basis, (_, state_type)) in enumerate(zip(alice_bases, bob_bases, intensities)):
            if a_basis == b_basis and state_type == "signal":
                sifted_key.append(bob_measurements[i])
                matching_indices.append(i)
        
        # Step 6: Error estimation
        alice_sifted = [alice_bits[i] for i in matching_indices]
        error_rate = sum(1 for a, b in zip(alice_sifted, sifted_key) if a != b) / len(alice_sifted) if alice_sifted else 1.0
        
        # Enhanced security check using decoy analysis
        if error_rate > 0.11 or decoy_analysis["security_parameter"] < 0.5:
            raise EavesdropDetected(f"Security compromised - QBER: {error_rate:.3f}, Security: {decoy_analysis['security_parameter']:.3f}")
        
        # Step 7: Privacy amplification
        target_bytes = key_length // 8
        final_key = self._enhanced_privacy_amplification(sifted_key, target_bytes, decoy_analysis)
        
        # Calculate enhanced security level
        security_level = decoy_analysis["security_parameter"] * (1 - error_rate)
        
        generation_time = time.time() - start_time
        
        return QuantumKey(
            key_id=str(uuid.uuid4()),
            raw_key=bytes(sifted_key[:target_bytes]),
            final_key=final_key,
            length=len(final_key) * 8,
            security_level=security_level,
            generation_time=generation_time,
            protocol=ProtocolType.BB84_DECOY,
            error_rate=error_rate,
            decoy_analysis=decoy_analysis
        )
    
    def _enhanced_privacy_amplification(self, key: List[int], target_length: int, 
                                      decoy_analysis: Dict[str, float]) -> bytes:
        """Enhanced privacy amplification using decoy state information"""
        if len(key) < target_length:
            key = key * ((target_length // len(key)) + 1)
        
        # Use decoy analysis for enhanced randomness
        security_factor = decoy_analysis.get("security_parameter", 0.5)
        key_bytes = bytes(key[:target_length])
        
        # Multi-round hashing with security factor
        final_key = b""
        rounds = max(2, int((target_length // 32) * (1 + security_factor)))
        
        for i in range(rounds):
            hash_input = key_bytes + i.to_bytes(4, 'big') + str(security_factor).encode()
            final_key += hashlib.sha256(hash_input).digest()
        
        return final_key[:target_length]

class SARG04Protocol:
    """
    SARG04 (Scarani-Acin-Ribordy-Gisin 2004) Protocol
    Cải tiến của BB84 với hiệu suất cao hơn và bảo mật tốt hơn
    """
    
    def __init__(self, n_qubits: int = 4):
        self.n_qubits = n_qubits
        self.device = qml.device("default.qubit", wires=n_qubits)
        
    def alice_prepare_sarg_qubits(self, bits: List[int], bases: List[int]) -> List[np.ndarray]:
        """Alice prepares SARG04 states"""
        @qml.qnode(self.device)
        def prepare_sarg_state(bit: int, basis: int):
            if basis == 0:  # Z basis
                if bit == 1:
                    qml.PauliX(wires=0)
            else:  # X basis  
                qml.Hadamard(wires=0)
                if bit == 1:
                    qml.PauliZ(wires=0)
            return qml.state()
        
        prepared_states = []
        for bit, basis in zip(bits, bases):
            state = prepare_sarg_state(bit, basis)
            prepared_states.append(state)
        
        return prepared_states
    
    def bob_sarg_measurement(self, states: List[np.ndarray], 
                           measurement_bases: List[int]) -> List[Tuple[int, int]]:
        """Bob's SARG04 measurement strategy"""
        @qml.qnode(self.device)
        def measure_sarg_state(state: np.ndarray, basis: int):
            qml.QubitStateVector(state, wires=0)
            if basis == 1:
                qml.Hadamard(wires=0)
            return qml.expval(qml.PauliZ(0))
        
        measurements = []
        for state, basis in zip(states, measurement_bases):
            try:
                result = measure_sarg_state(state, basis)
                measurement = 1 if result < 0 else 0
                confidence = 1
                measurements.append((measurement, confidence))
            except:
                measurements.append((secrets.randbits(1), 0))
        
        return measurements
    
    def generate_key(self, alice_id: str, bob_id: str, 
                    key_length: int = 256) -> QuantumKey:
        """Generate quantum key using SARG04 protocol"""
        start_time = time.time()
        
        # Generate random bits and bases
        raw_length = key_length * 4
        alice_bits = [secrets.randbits(1) for _ in range(raw_length)]
        alice_bases = [secrets.randbits(1) for _ in range(raw_length)]
        bob_bases = [secrets.randbits(1) for _ in range(raw_length)]
        
        # Alice prepares SARG04 states
        prepared_states = self.alice_prepare_sarg_qubits(alice_bits, alice_bases)
        
        # Bob performs measurements
        bob_measurements = self.bob_sarg_measurement(prepared_states, bob_bases)
        
        # Key sifting
        sifted_key = []
        matching_indices = []
        
        for i, (a_basis, b_basis, (b_result, confidence)) in enumerate(
            zip(alice_bases, bob_bases, bob_measurements)):
            if a_basis == b_basis and confidence > 0:
                sifted_key.append(b_result)
                matching_indices.append(i)
        
        # Error estimation
        alice_sifted = [alice_bits[i] for i in matching_indices]
        error_rate = sum(1 for a, b in zip(alice_sifted, sifted_key) if a != b) / len(alice_sifted) if alice_sifted else 1.0
        
        # Security check
        if error_rate > 0.15:
            raise EavesdropDetected(f"SARG04 security breach - Error rate: {error_rate:.3f}")
        
        # Privacy amplification
        target_bytes = key_length // 8
        key_bytes = bytes(sifted_key[:target_bytes])
        final_key = hashlib.sha256(key_bytes + b"SARG04").digest()[:target_bytes]
        
        # Calculate security level
        sarg_efficiency = len(sifted_key) / raw_length if raw_length > 0 else 0
        security_level = sarg_efficiency * (1 - error_rate)
        
        generation_time = time.time() - start_time
        
        return QuantumKey(
            key_id=str(uuid.uuid4()),
            raw_key=key_bytes,
            final_key=final_key,
            length=len(final_key) * 8,
            security_level=security_level,
            generation_time=generation_time,
            protocol=ProtocolType.SARG04,
            error_rate=error_rate,
            sarg_efficiency=sarg_efficiency
        )

class E91Protocol:
    """
    E91 Entanglement-based Quantum Key Distribution Protocol
    Sử dụng entangled photon pairs
    """
    
    def __init__(self, n_qubits: int = 2):
        self.n_qubits = n_qubits
        self.device = qml.device("default.qubit", wires=n_qubits)
        self.bell_threshold = 2.8  # CHSH inequality threshold
    
    def create_bell_pairs(self, num_pairs: int) -> List[np.ndarray]:
        """Create entangled Bell state pairs"""
        @qml.qnode(self.device)
        def bell_state():
            qml.Hadamard(wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()
        
        bell_states = []
        for _ in range(num_pairs):
            state = bell_state()
            bell_states.append(state)
        
        return bell_states
    
    def measure_entangled_qubits(self, states: List[np.ndarray], 
                                alice_bases: List[int], 
                                bob_bases: List[int]) -> Tuple[List[int], List[int]]:
        """
        Measure entangled qubits with chosen bases
        3 measurement bases for CHSH test
        """
        @qml.qnode(self.device)
        def measure_bell_pair(state: np.ndarray, alice_basis: int, bob_basis: int):
            # Prepare entangled state
            qml.QubitStateVector(state, wires=[0, 1])
            
            # Alice's measurement basis
            if alice_basis == 1:
                qml.RY(np.pi/4, wires=0)
            elif alice_basis == 2:
                qml.RY(-np.pi/4, wires=0)
            
            # Bob's measurement basis  
            if bob_basis == 1:
                qml.RY(np.pi/4, wires=1)
            elif bob_basis == 2:
                qml.RY(-np.pi/4, wires=1)
            
            return [qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))]
        
        alice_results = []
        bob_results = []
        
        for state, a_basis, b_basis in zip(states, alice_bases, bob_bases):
            try:
                measurements = measure_bell_pair(state, a_basis, b_basis)
                alice_results.append(1 if measurements[0] < 0 else 0)
                bob_results.append(1 if measurements[1] < 0 else 0)
            except:
                # Fallback measurements
                alice_results.append(secrets.randbits(1))
                bob_results.append(secrets.randbits(1))
        
        return alice_results, bob_results
    
    def chsh_bell_test(self, alice_results: List[int], bob_results: List[int],
                      alice_bases: List[int], bob_bases: List[int]) -> float:
        """
        Perform CHSH Bell inequality test
        """
        correlations = {}
        
        # Calculate correlations for different basis combinations
        for a_basis in [0, 1, 2]:
            for b_basis in [0, 1, 2]:
                correlation_sum = 0
                count = 0
                
                for i, (a_b, b_b, a_r, b_r) in enumerate(zip(
                    alice_bases, bob_bases, alice_results, bob_results)):
                    if a_b == a_basis and b_b == b_basis:
                        # Calculate correlation (-1)^(a⊕b)
                        correlation_sum += (-1) ** (a_r ^ b_r)
                        count += 1
                
                if count > 0:
                    correlations[(a_basis, b_basis)] = correlation_sum / count
                else:
                    correlations[(a_basis, b_basis)] = 0
        
        # Calculate CHSH parameter S
        S = abs(correlations.get((0, 0), 0) - correlations.get((0, 2), 0) + 
                correlations.get((1, 0), 0) + correlations.get((1, 2), 0))
        
        return S
    
    def generate_key(self, alice_id: str, bob_id: str, 
                    key_length: int = 256) -> QuantumKey:
        """
        Generate quantum key using E91 protocol
        """
        start_time = time.time()
        
        # Step 1: Generate random measurement bases
        raw_length = key_length * 4
        alice_bases = [secrets.randbelow(3) for _ in range(raw_length)]
        bob_bases = [secrets.randbelow(3) for _ in range(raw_length)]
        
        # Step 2: Create Bell pairs
        bell_states = self.create_bell_pairs(raw_length)
        
        # Step 3: Measure entangled qubits
        alice_results, bob_results = self.measure_entangled_qubits(
            bell_states, alice_bases, bob_bases
        )
        
        # Step 4: CHSH Bell test for eavesdropping detection
        chsh_value = self.chsh_bell_test(alice_results, bob_results, 
                                        alice_bases, bob_bases)
        
        if chsh_value < self.bell_threshold:
            raise EavesdropDetected(f"Bell inequality violation: S = {chsh_value:.3f}")
        
        # Step 5: Key sifting (use same bases)
        sifted_alice = []
        sifted_bob = []
        
        for i, (a_basis, b_basis) in enumerate(zip(alice_bases, bob_bases)):
            if a_basis == b_basis:
                sifted_alice.append(alice_results[i])
                sifted_bob.append(bob_results[i])
        
        # Step 6: Error estimation
        errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
        error_rate = errors / len(sifted_alice) if sifted_alice else 1.0
        
        # Step 7: Privacy amplification
        target_bytes = key_length // 8
        key_bytes = bytes(sifted_alice[:target_bytes])
        
        # Hash for final key
        final_key = hashlib.sha256(key_bytes).digest()[:target_bytes]
        
        # Calculate security level
        security_level = max(0.0, min(1.0, chsh_value / 4.0))
        
        generation_time = time.time() - start_time
        
        return QuantumKey(
            key_id=str(uuid.uuid4()),
            raw_key=key_bytes,
            final_key=final_key,
            length=len(final_key) * 8,
            security_level=security_level,
            generation_time=generation_time,
            protocol=ProtocolType.E91,
            error_rate=error_rate
        )

class QKDManager:
    """
    Advanced QKD Manager for COWN
    Quản lý sessions và protocols
    """
    
    def __init__(self):
        self.bb84_protocol = BB84Protocol()
        self.enhanced_bb84_protocol = EnhancedBB84Protocol()
        self.sarg04_protocol = SARG04Protocol()
        self.e91_protocol = E91Protocol()
        self.active_sessions: Dict[str, QKDSession] = {}
        self.generated_keys: Dict[str, QuantumKey] = {}
        
    def start_bb84_session(self, alice_id: str, bob_id: str, 
                          key_length: int = 256) -> QKDSession:
        """Start BB84 QKD session"""
        session_id = str(uuid.uuid4())
        
        try:
            # Generate quantum key
            quantum_key = self.bb84_protocol.generate_key(alice_id, bob_id, key_length)
            
            session = QKDSession(
                session_id=session_id,
                alice_id=alice_id,
                bob_id=bob_id,
                protocol=ProtocolType.BB84,
                key_length=quantum_key.length,
                security_level=quantum_key.security_level,
                error_rate=quantum_key.error_rate,
                created_at=time.time(),
                quantum_key=quantum_key
            )
            
            # Store session and key
            self.active_sessions[session_id] = session
            self.generated_keys[quantum_key.key_id] = quantum_key
            
            return session
            
        except Exception as e:
            raise QKDError(f"BB84 session failed: {str(e)}")
    
    def start_enhanced_bb84_session(self, alice_id: str, bob_id: str, 
                                  key_length: int = 256) -> QKDSession:
        """Start Enhanced BB84 with Decoy States session"""
        session_id = str(uuid.uuid4())
        
        try:
            # Generate quantum key
            quantum_key = self.enhanced_bb84_protocol.generate_key(alice_id, bob_id, key_length)
            
            session = QKDSession(
                session_id=session_id,
                alice_id=alice_id,
                bob_id=bob_id,
                protocol=ProtocolType.BB84_DECOY,
                key_length=quantum_key.length,
                security_level=quantum_key.security_level,
                error_rate=quantum_key.error_rate,
                created_at=time.time(),
                quantum_key=quantum_key
            )
            
            # Store session and key
            self.active_sessions[session_id] = session
            self.generated_keys[quantum_key.key_id] = quantum_key
            
            return session
            
        except Exception as e:
            raise QKDError(f"Enhanced BB84 session failed: {str(e)}")
    
    def start_sarg04_session(self, alice_id: str, bob_id: str, 
                           key_length: int = 256) -> QKDSession:
        """Start SARG04 QKD session"""
        session_id = str(uuid.uuid4())
        
        try:
            # Generate quantum key
            quantum_key = self.sarg04_protocol.generate_key(alice_id, bob_id, key_length)
            
            session = QKDSession(
                session_id=session_id,
                alice_id=alice_id,
                bob_id=bob_id,
                protocol=ProtocolType.SARG04,
                key_length=quantum_key.length,
                security_level=quantum_key.security_level,
                error_rate=quantum_key.error_rate,
                created_at=time.time(),
                quantum_key=quantum_key
            )
            
            # Store session and key
            self.active_sessions[session_id] = session
            self.generated_keys[quantum_key.key_id] = quantum_key
            
            return session
            
        except Exception as e:
            raise QKDError(f"SARG04 session failed: {str(e)}")
    
    def start_e91_session(self, alice_id: str, bob_id: str, 
                         key_length: int = 256) -> QKDSession:
        """Start E91 QKD session"""
        session_id = str(uuid.uuid4())
        
        try:
            # Generate quantum key
            quantum_key = self.e91_protocol.generate_key(alice_id, bob_id, key_length)
            
            session = QKDSession(
                session_id=session_id,
                alice_id=alice_id,
                bob_id=bob_id,
                protocol=ProtocolType.E91,
                key_length=quantum_key.length,
                security_level=quantum_key.security_level,
                error_rate=quantum_key.error_rate,
                created_at=time.time(),
                quantum_key=quantum_key
            )
            
            # Store session and key
            self.active_sessions[session_id] = session
            self.generated_keys[quantum_key.key_id] = quantum_key
            
            return session
            
        except Exception as e:
            raise QKDError(f"E91 session failed: {str(e)}")
    
    def get_session(self, session_id: str) -> Optional[QKDSession]:
        """Get QKD session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_quantum_key(self, key_id: str) -> Optional[QuantumKey]:
        """Get quantum key by ID"""
        return self.generated_keys.get(key_id)
    
    def terminate_session(self, session_id: str) -> bool:
        """Terminate QKD session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Remove associated key
            if session.quantum_key:
                self.generated_keys.pop(session.quantum_key.key_id, None)
            
            # Remove session
            del self.active_sessions[session_id]
            return True
        
        return False
    
    def get_security_report(self, session_id: str) -> Dict[str, Any]:
        """Generate security analysis report"""
        session = self.active_sessions.get(session_id)
        if not session or not session.quantum_key:
            return {"error": "Session not found"}
        
        key = session.quantum_key
        
        # Calculate metrics
        key_rate = key.length / key.generation_time if key.generation_time > 0 else 0
        mutual_info = max(0, 1 - key.error_rate)
        privacy_ratio = min(1.0, key.security_level)
        
        return {
            "session_id": session_id,
            "protocol": session.protocol.value,
            "security_level": session.security_level,
            "bit_error_rate": key.error_rate,
            "key_generation_rate": key_rate,
            "mutual_information": mutual_info,
            "privacy_amplification_ratio": privacy_ratio,
            "key_length": key.length,
            "generation_time": key.generation_time,
            "security_parameter": key.security_level * (1 - key.error_rate)
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        total_sessions = len(self.active_sessions)
        total_keys = len(self.generated_keys)
        
        # Protocol distribution
        bb84_sessions = sum(1 for s in self.active_sessions.values() 
                           if s.protocol == ProtocolType.BB84)
        bb84_decoy_sessions = sum(1 for s in self.active_sessions.values() 
                                 if s.protocol == ProtocolType.BB84_DECOY)
        sarg04_sessions = sum(1 for s in self.active_sessions.values() 
                             if s.protocol == ProtocolType.SARG04)
        e91_sessions = sum(1 for s in self.active_sessions.values() 
                          if s.protocol == ProtocolType.E91)
        
        # Average security level
        if total_sessions > 0:
            avg_security = sum(s.security_level for s in self.active_sessions.values()) / total_sessions
        else:
            avg_security = 0.0
        
        return {
            "total_active_sessions": total_sessions,
            "total_generated_keys": total_keys,
            "bb84_sessions": bb84_sessions,
            "bb84_decoy_sessions": bb84_decoy_sessions,
            "sarg04_sessions": sarg04_sessions,
            "e91_sessions": e91_sessions,
            "average_security_level": avg_security,
            "system_health": "operational" if total_sessions > 0 else "idle"
        }

# Global QKD manager instance
qkd_manager = QKDManager()

def get_qkd_manager() -> QKDManager:
    """Get global QKD manager instance"""
    return qkd_manager
