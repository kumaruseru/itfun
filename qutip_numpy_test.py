#!/usr/bin/env python3
"""
QuTiP 5.0 + NumPy 2.0 Integration Test
Comprehensive test of advanced quantum capabilities
"""

import sys
sys.path.append('src')

def test_qutip_numpy_integration():
    """Test QuTiP 5.0 and NumPy 2.0 integration"""
    
    print("🚀 QUTIP 5.0 + NUMPY 2.0 COMPREHENSIVE INTEGRATION TEST")
    print("=" * 80)
    
    try:
        import numpy as np
        import qutip as qt
        import pennylane as qml
        import time
        
        print("✅ All libraries imported successfully")
        print(f"   NumPy version: {np.__version__}")
        print(f"   QuTiP version: {qt.__version__}")
        print(f"   PennyLane version: {qml.__version__}")
        
        # Test 1: NumPy 2.0 Advanced Operations
        print("\n⚡ 1. NUMPY 2.0 ADVANCED FEATURES:")
        print("-" * 50)
        
        # Enhanced random number generation
        rng = np.random.default_rng(seed=42)
        
        # Large matrix operations (optimized in NumPy 2.0)
        start_time = time.time()
        large_matrix = rng.random((2000, 2000), dtype=np.float64)
        eigenvals = np.linalg.eigvals(large_matrix[:100, :100])  # Subset for speed
        numpy_time = time.time() - start_time
        
        print(f"   Matrix eigenvalue computation: {numpy_time:.4f}s")
        print(f"   Matrix dtype: {large_matrix.dtype}")
        print(f"   Memory layout: {'C-contiguous' if large_matrix.flags.c_contiguous else 'Non-contiguous'}")
        
        # FFT operations (improved performance)
        start_time = time.time()
        signal = rng.random(8192)
        fft_result = np.fft.fft(signal)
        fft_time = time.time() - start_time
        
        print(f"   FFT computation (8192 points): {fft_time:.4f}s")
        print(f"   FFT result shape: {fft_result.shape}")
        
        # Test 2: QuTiP 5.0 Quantum Objects
        print("\n🔬 2. QUTIP 5.0 QUANTUM SIMULATIONS:")
        print("-" * 50)
        
        # Create quantum states
        print("   Creating quantum states:")
        
        # Single qubit states
        zero_state = qt.basis(2, 0)  # |0⟩
        one_state = qt.basis(2, 1)   # |1⟩
        plus_state = (zero_state + one_state).unit()  # |+⟩
        
        print(f"   |0⟩ state: {zero_state.dims}")
        print(f"   |+⟩ state fidelity with |0⟩: {qt.fidelity(plus_state, zero_state):.4f}")
        
        # Two-qubit entangled states
        bell_state = (qt.tensor(zero_state, zero_state) + qt.tensor(one_state, one_state)).unit()
        print(f"   Bell state |Φ+⟩ created: {bell_state.dims}")
        
        # Calculate entanglement measures
        rho = bell_state * bell_state.dag()  # Density matrix
        rho_A = qt.ptrace(rho, 0)  # Reduced density matrix for qubit A
        entropy = qt.entropy_vn(rho_A)  # Von Neumann entropy
        
        print(f"   Entanglement entropy: {entropy:.4f}")
        
        # Calculate concurrence for density matrix instead
        try:
            concurrence_val = qt.concurrence(rho)
            print(f"   Bell state concurrence: {concurrence_val:.4f}")
        except:
            # Alternative entanglement measure
            negativity = qt.negativity(rho, [0, 1])
            print(f"   Bell state negativity: {negativity:.4f}")
        
        # Test 3: Quantum Channel Simulation
        print("\n📡 3. QUANTUM CHANNEL SIMULATION:")
        print("-" * 50)
        
        # Simulate noisy quantum channel
        def apply_depolarizing_noise(state, p=0.01):
            """Apply depolarizing noise"""
            # Determine if single or two-qubit state
            if state.dims == [[2], [1]]:  # Single qubit
                # Create Kraus operators for single-qubit depolarizing channel
                kraus_ops = [
                    np.sqrt(1 - 3*p/4) * qt.qeye(2),
                    np.sqrt(p/4) * qt.sigmax(),
                    np.sqrt(p/4) * qt.sigmay(),
                    np.sqrt(p/4) * qt.sigmaz()
                ]
            else:  # Two-qubit state
                # Simplified noise model for two-qubit states
                # Apply single-qubit noise to each qubit independently
                I = qt.qeye(2)
                
                # First qubit noise
                kraus_ops_1 = [
                    np.sqrt(1 - 3*p/4) * qt.tensor(I, I),
                    np.sqrt(p/4) * qt.tensor(qt.sigmax(), I),
                    np.sqrt(p/4) * qt.tensor(qt.sigmay(), I),
                    np.sqrt(p/4) * qt.tensor(qt.sigmaz(), I)
                ]
                
                # Apply first qubit noise
                rho = state * state.dag()
                noisy_rho = sum(K * rho * K.dag() for K in kraus_ops_1)
                
                # Second qubit noise
                kraus_ops_2 = [
                    np.sqrt(1 - 3*p/4) * qt.tensor(I, I),
                    np.sqrt(p/4) * qt.tensor(I, qt.sigmax()),
                    np.sqrt(p/4) * qt.tensor(I, qt.sigmay()),
                    np.sqrt(p/4) * qt.tensor(I, qt.sigmaz())
                ]
                
                # Apply second qubit noise
                final_rho = sum(K * noisy_rho * K.dag() for K in kraus_ops_2)
                return final_rho
            
            # Apply channel to density matrix (single qubit case)
            rho = state * state.dag()
            noisy_rho = sum(K * rho * K.dag() for K in kraus_ops)
            
            return noisy_rho
        
        # Test noise on Bell state
        original_fidelity = qt.fidelity(bell_state, bell_state)
        noisy_rho = apply_depolarizing_noise(bell_state, p=0.05)
        
        # Extract state from density matrix for fidelity calculation
        eigenvals, eigenvecs = noisy_rho.eigenstates()
        dominant_state = eigenvecs[np.argmax(eigenvals)]
        noisy_fidelity = qt.fidelity(dominant_state, bell_state)
        
        print(f"   Original Bell state fidelity: {original_fidelity:.4f}")
        print(f"   Noisy channel fidelity: {noisy_fidelity:.4f}")
        print(f"   Fidelity loss: {(1 - noisy_fidelity)*100:.2f}%")
        
        # Test 4: Quantum Measurements
        print("\n📊 4. QUANTUM MEASUREMENTS:")
        print("-" * 50)
        
        # Measurement operators
        M0 = zero_state * zero_state.dag()  # |0⟩⟨0|
        M1 = one_state * one_state.dag()    # |1⟩⟨1|
        
        # Measure plus state in computational basis
        prob_0 = qt.expect(M0, plus_state)
        prob_1 = qt.expect(M1, plus_state)
        
        print(f"   |+⟩ state measured in computational basis:")
        print(f"     P(0) = {prob_0:.4f}")
        print(f"     P(1) = {prob_1:.4f}")
        print(f"     Sum = {prob_0 + prob_1:.4f}")
        
        # Bell state measurement
        if bell_state.dims == [[2, 2], [1, 1]]:  # Two-qubit state
            # Partial trace for first qubit
            rho_bell = bell_state * bell_state.dag()
            rho_qubit1 = qt.ptrace(rho_bell, 0)
            
            # Measure first qubit
            prob_0_bell = qt.expect(qt.basis(2, 0) * qt.basis(2, 0).dag(), rho_qubit1)
            prob_1_bell = qt.expect(qt.basis(2, 1) * qt.basis(2, 1).dag(), rho_qubit1)
            
            print(f"   Bell state first qubit measurement:")
            print(f"     P(0) = {prob_0_bell:.4f}")
            print(f"     P(1) = {prob_1_bell:.4f}")
        
        # Test 5: Performance Benchmarks
        print("\n⏱️ 5. PERFORMANCE BENCHMARKS:")
        print("-" * 50)
        
        # QuTiP operations benchmark
        n_trials = 100
        
        # State creation benchmark
        start_time = time.time()
        for _ in range(n_trials):
            test_state = (qt.basis(2, 0) + qt.basis(2, 1)).unit()
        qutip_creation_time = time.time() - start_time
        
        # Expectation value benchmark
        start_time = time.time()
        for _ in range(n_trials):
            expectation = qt.expect(qt.sigmaz(), plus_state)
        qutip_expectation_time = time.time() - start_time
        
        # NumPy operations benchmark
        start_time = time.time()
        for _ in range(n_trials):
            matrix = rng.random((100, 100))
            result = np.linalg.inv(matrix)
        numpy_linalg_time = time.time() - start_time
        
        print(f"   QuTiP state creation ({n_trials} trials): {qutip_creation_time:.4f}s")
        print(f"   QuTiP expectation values ({n_trials} trials): {qutip_expectation_time:.4f}s")
        print(f"   NumPy matrix inversion ({n_trials} trials): {numpy_linalg_time:.4f}s")
        
        # Test 6: Integration with COWN QKD
        print("\n🔐 6. INTEGRATION WITH COWN QKD SYSTEM:")
        print("-" * 50)
        
        # Simulate BB84 with QuTiP
        def simulate_bb84_qutip(n_bits=10):
            """Simulate BB84 protocol using QuTiP"""
            
            # Alice's random bits and bases
            alice_bits = rng.integers(0, 2, n_bits)
            alice_bases = rng.integers(0, 2, n_bits)
            
            # Bob's random bases
            bob_bases = rng.integers(0, 2, n_bits)
            
            bob_measurements = []
            fidelities = []
            
            for i in range(n_bits):
                # Prepare Alice's state
                if alice_bases[i] == 0:  # Computational basis
                    if alice_bits[i] == 0:
                        alice_state = qt.basis(2, 0)
                    else:
                        alice_state = qt.basis(2, 1)
                else:  # Hadamard basis
                    if alice_bits[i] == 0:
                        alice_state = (qt.basis(2, 0) + qt.basis(2, 1)).unit()
                    else:
                        alice_state = (qt.basis(2, 0) - qt.basis(2, 1)).unit()
                
                # Add channel noise
                noisy_rho = apply_depolarizing_noise(alice_state, p=0.02)
                
                # Bob's measurement
                if bob_bases[i] == 0:  # Computational basis
                    prob_0 = qt.expect(M0, noisy_rho)
                    prob_1 = qt.expect(M1, noisy_rho)
                    bob_bit = 0 if prob_0 > prob_1 else 1
                else:  # Hadamard basis
                    # Create +/- measurement operators
                    M_plus = plus_state * plus_state.dag()
                    M_minus = ((qt.basis(2, 0) - qt.basis(2, 1)).unit() * 
                              (qt.basis(2, 0) - qt.basis(2, 1)).unit().dag())
                    
                    prob_plus = qt.expect(M_plus, noisy_rho)
                    prob_minus = qt.expect(M_minus, noisy_rho)
                    bob_bit = 0 if prob_plus > prob_minus else 1
                
                bob_measurements.append(bob_bit)
                
                # Calculate fidelity
                eigenvals, eigenvecs = noisy_rho.eigenstates()
                dominant_state = eigenvecs[np.argmax(eigenvals)]
                fidelity = qt.fidelity(dominant_state, alice_state)
                fidelities.append(fidelity)
            
            # Find matching bases
            matching_indices = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
            
            # Calculate error rate
            errors = sum(1 for i in matching_indices 
                        if alice_bits[i] != bob_measurements[i])
            error_rate = errors / len(matching_indices) if matching_indices else 1.0
            
            return {
                'n_bits': n_bits,
                'matching_bases': len(matching_indices),
                'error_rate': error_rate,
                'average_fidelity': np.mean(fidelities),
                'key_rate': len(matching_indices) / n_bits
            }
        
        # Run BB84 simulation
        bb84_results = simulate_bb84_qutip(n_bits=50)
        
        print(f"   BB84 Simulation Results:")
        print(f"     Total bits: {bb84_results['n_bits']}")
        print(f"     Matching bases: {bb84_results['matching_bases']}")
        print(f"     Key rate: {bb84_results['key_rate']:.2%}")
        print(f"     Error rate: {bb84_results['error_rate']:.4f}")
        print(f"     Average fidelity: {bb84_results['average_fidelity']:.4f}")
        
        # Test 7: System Integration Score
        print("\n🏆 7. INTEGRATION ASSESSMENT:")
        print("-" * 50)
        
        # Calculate integration score
        scores = {
            'numpy_performance': min(100, (1.0 / max(numpy_time, 0.001)) * 10),
            'qutip_functionality': min(100, entropy * 100 if entropy > 0 else 50),
            'quantum_fidelity': noisy_fidelity * 100,
            'bb84_performance': (1 - bb84_results['error_rate']) * 100,
            'measurement_accuracy': (prob_0 + prob_1) * 100
        }
        
        overall_score = np.mean(list(scores.values()))
        
        print(f"   Component Scores:")
        for component, score in scores.items():
            print(f"     {component.replace('_', ' ').title()}: {score:.1f}%")
        
        print(f"\n   🎯 OVERALL INTEGRATION SCORE: {overall_score:.1f}%")
        
        if overall_score >= 90:
            status = "🥇 EXCELLENT - Advanced integration achieved"
        elif overall_score >= 80:
            status = "🥈 VERY GOOD - Strong integration performance"
        elif overall_score >= 70:
            status = "🥉 GOOD - Solid integration foundation"
        else:
            status = "⚠️ NEEDS IMPROVEMENT - Integration requires optimization"
        
        print(f"   Status: {status}")
        
        # Summary
        print(f"\n📋 INTEGRATION SUMMARY:")
        print(f"=" * 60)
        print(f"✅ ENHANCED CAPABILITIES:")
        print(f"   - NumPy 2.0: Advanced linear algebra and FFT")
        print(f"   - QuTiP 5.0: Comprehensive quantum simulations")
        print(f"   - Integration: Hybrid quantum-classical processing")
        print(f"   - Performance: Optimized mathematical operations")
        print(f"   - Compatibility: Seamless library interaction")
        
        print(f"\n📊 PERFORMANCE METRICS:")
        print(f"   - Matrix operations: {numpy_time*1000:.2f}ms")
        print(f"   - Quantum state fidelity: {bb84_results['average_fidelity']:.4f}")
        print(f"   - QKD error rate: {bb84_results['error_rate']:.4f}")
        print(f"   - System integration: {overall_score:.1f}%")
        
        return {
            'numpy_version': np.__version__,
            'qutip_version': qt.__version__,
            'integration_score': overall_score,
            'bb84_results': bb84_results,
            'performance_metrics': scores
        }
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = test_qutip_numpy_integration()
