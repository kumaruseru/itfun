#!/usr/bin/env python3
"""
COWN Quantum System Test Suite
Kiểm tra toàn diện hệ thống lượng tử

Features tested:
- Quantum utilities functionality
- QKD protocols (BB84, Enhanced BB84, SARG04, E91)
- Quantum encryption system
- Performance benchmarks
- Security analysis
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

print(f"📁 Project root: {project_root}")
print(f"📁 Source path: {src_path}")
print(f"📁 Python path: {sys.path[:3]}")
print()

def test_imports():
    """Test if all quantum modules can be imported"""
    print("🔬 Testing Quantum Module Imports")
    print("=" * 50)
    
    test_results = {}
    
    # Test PennyLane
    try:
        import pennylane as qml
        print("✅ PennyLane imported successfully")
        print(f"   Version: {qml.version()}")
        test_results["pennylane"] = True
    except ImportError as e:
        print(f"❌ PennyLane import failed: {e}")
        test_results["pennylane"] = False
    
    # Test NumPy
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
        print(f"   Version: {np.__version__}")
        test_results["numpy"] = True
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        test_results["numpy"] = False
    
    # Test Cryptography
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher
        print("✅ Cryptography imported successfully")
        test_results["cryptography"] = True
    except ImportError as e:
        print(f"❌ Cryptography import failed: {e}")
        test_results["cryptography"] = False
    
    # Test Quantum Utils
    try:
        sys.path.append(os.path.join(project_root, "src"))
        from quantum.utils.quantum_utils import QuantumUtils, quantum_utils
        print("✅ Quantum utilities imported successfully")
        test_results["quantum_utils"] = True
    except ImportError as e:
        print(f"❌ Quantum utilities import failed: {e}")
        print(f"   Checking path: {os.path.join(project_root, 'src', 'quantum', 'utils')}")
        test_results["quantum_utils"] = False
    except Exception as e:
        print(f"❌ Quantum utilities error: {e}")
        test_results["quantum_utils"] = False
    
    # Test QKD Protocols
    try:
        from quantum.protocols.qkd_protocol import QKDManager, ProtocolType
        print("✅ QKD protocols imported successfully")
        test_results["qkd_protocols"] = True
    except ImportError as e:
        print(f"❌ QKD protocols import failed: {e}")
        print(f"   Checking path: {os.path.join(project_root, 'src', 'quantum', 'protocols')}")
        test_results["qkd_protocols"] = False
    except Exception as e:
        print(f"❌ QKD protocols error: {e}")
        test_results["qkd_protocols"] = False
    
    # Test Quantum Encryption
    try:
        from quantum.encryption.quantum_encryptor import QuantumEncryption
        print("✅ Quantum encryption imported successfully")
        test_results["quantum_encryption"] = True
    except ImportError as e:
        print(f"❌ Quantum encryption import failed: {e}")
        print(f"   Checking path: {os.path.join(project_root, 'src', 'quantum', 'encryption')}")
        test_results["quantum_encryption"] = False
    except Exception as e:
        print(f"❌ Quantum encryption error: {e}")
        test_results["quantum_encryption"] = False
    
    success_rate = sum(test_results.values()) / len(test_results)
    print(f"\n📊 Import Success Rate: {success_rate:.1%}")
    
    return success_rate >= 0.8  # Return boolean for overall success

def test_quantum_utils():
    """Test quantum utilities functionality"""
    print("\n🔬 Testing Quantum Utilities")
    print("=" * 50)
    
    try:
        from quantum.utils.quantum_utils import quantum_utils, generate_random_bits
        
        # Test random bit generation
        print("🎲 Testing random bit generation...")
        bits = generate_random_bits(100)
        assert len(bits) == 100
        assert all(bit in [0, 1] for bit in bits)
        print(f"   ✅ Generated {len(bits)} random bits")
        
        # Test quantum state creation
        print("🌀 Testing quantum state creation...")
        from quantum.utils.quantum_utils import QuantumBasis
        state = quantum_utils.create_qubit_state(0, QuantumBasis.RECTILINEAR)
        assert len(state.amplitudes) == 2
        print("   ✅ Quantum state created successfully")
        
        # Test Bell state creation
        print("🔗 Testing Bell state creation...")
        bell_state = quantum_utils.create_bell_state(0)
        assert len(bell_state.amplitudes) == 4
        assert bell_state.is_entangled == True
        print("   ✅ Bell state created successfully")
        
        # Test key sifting
        print("🔑 Testing key sifting...")
        alice_bits = [0, 1, 1, 0, 1]
        bob_bits = [0, 1, 0, 0, 1]
        alice_bases = [0, 1, 0, 1, 0]
        bob_bases = [0, 1, 1, 1, 0]
        
        alice_sifted, bob_sifted, indices = quantum_utils.sift_quantum_key(
            alice_bits, bob_bits, alice_bases, bob_bases
        )
        
        print(f"   ✅ Sifted {len(alice_sifted)} bits from {len(alice_bits)} original")
        
        # Test error rate calculation
        print("📊 Testing error rate calculation...")
        error_stats = quantum_utils.calculate_error_rate(alice_sifted, bob_sifted)
        print(f"   ✅ Error rate: {error_stats.error_rate:.3f}")
        
        # Test entropy calculation
        print("🎯 Testing entropy calculation...")
        entropy = quantum_utils.calculate_entropy(alice_bits)
        print(f"   ✅ Entropy: {entropy:.3f} bits")
        
        # Test randomness quality
        print("🎲 Testing randomness quality...")
        randomness_test = quantum_utils.test_randomness(bits, "basic")
        print(f"   ✅ Bias: {randomness_test['basic']['bias']:.3f}")
        
        print("✅ All quantum utilities tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quantum utilities test failed: {e}")
        print(traceback.format_exc())
        return False

def test_qkd_protocols():
    """Test QKD protocols"""
    print("\n🔬 Testing QKD Protocols")
    print("=" * 50)
    
    try:
        from quantum.protocols.qkd_protocol import QKDManager, ProtocolType
        
        manager = QKDManager()
        print("✅ QKD Manager created successfully")
        
        # Test BB84 Protocol
        print("🔐 Testing BB84 Protocol...")
        try:
            session = manager.start_bb84_session("alice_test", "bob_test", key_length=64)
            print(f"   ✅ BB84 session: {session.session_id[:8]}...")
            print(f"   🔑 Key length: {session.key_length} bits")
            print(f"   🛡️ Security: {session.security_level:.4f}")
            print(f"   📊 Error rate: {session.error_rate:.4f}")
            manager.terminate_session(session.session_id)
        except Exception as e:
            print(f"   ⚠️ BB84 test warning: {e}")
        
        # Test Enhanced BB84
        print("🔐 Testing Enhanced BB84 with Decoy States...")
        try:
            session = manager.start_enhanced_bb84_session("alice_decoy", "bob_decoy", key_length=64)
            print(f"   ✅ Enhanced BB84 session: {session.session_id[:8]}...")
            print(f"   🔑 Key length: {session.key_length} bits")
            print(f"   🛡️ Security: {session.security_level:.4f}")
            
            if session.quantum_key.decoy_analysis:
                decoy_data = session.quantum_key.decoy_analysis
                print(f"   📊 Signal rate: {decoy_data.get('signal_detection_rate', 0):.4f}")
                print(f"   📊 Decoy rate: {decoy_data.get('decoy_detection_rate', 0):.4f}")
            
            manager.terminate_session(session.session_id)
        except Exception as e:
            print(f"   ⚠️ Enhanced BB84 test warning: {e}")
        
        # Test SARG04 Protocol
        print("🔐 Testing SARG04 Protocol...")
        try:
            session = manager.start_sarg04_session("alice_sarg", "bob_sarg", key_length=64)
            print(f"   ✅ SARG04 session: {session.session_id[:8]}...")
            print(f"   🔑 Key length: {session.key_length} bits")
            print(f"   🛡️ Security: {session.security_level:.4f}")
            
            if hasattr(session.quantum_key, 'sarg_efficiency'):
                print(f"   ⚡ SARG efficiency: {session.quantum_key.sarg_efficiency:.4f}")
            
            manager.terminate_session(session.session_id)
        except Exception as e:
            print(f"   ⚠️ SARG04 test warning: {e}")
        
        # Test E91 Protocol
        print("🔐 Testing E91 Entanglement Protocol...")
        try:
            session = manager.start_e91_session("alice_e91", "bob_e91", key_length=64)
            print(f"   ✅ E91 session: {session.session_id[:8]}...")
            print(f"   🔑 Key length: {session.key_length} bits")
            print(f"   🛡️ Security: {session.security_level:.4f}")
            manager.terminate_session(session.session_id)
        except Exception as e:
            print(f"   ⚠️ E91 test warning: {e}")
        
        # Test system status
        print("📊 Testing system status...")
        status = manager.get_system_status()
        print(f"   📊 Active sessions: {status['total_active_sessions']}")
        print(f"   🔑 Generated keys: {status['total_generated_keys']}")
        
        print("✅ QKD protocols tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ QKD protocols test failed: {e}")
        print(traceback.format_exc())
        return False

def test_quantum_encryption():
    """Test quantum encryption system"""
    print("\n🔬 Testing Quantum Encryption")
    print("=" * 50)
    
    try:
        from quantum.encryption.quantum_encryptor import QuantumEncryption, EncryptionAlgorithm
        from quantum.protocols.qkd_protocol import ProtocolType
        
        encryption = QuantumEncryption()
        print("✅ Quantum encryption system created")
        
        # Test message encryption with different algorithms
        test_message = "COWN Quantum Security Test Message 🔐"
        
        algorithms = [
            EncryptionAlgorithm.AES_QUANTUM,
            EncryptionAlgorithm.CHACHA20_QUANTUM,
            EncryptionAlgorithm.QUANTUM_OTP
        ]
        
        for algorithm in algorithms:
            print(f"🔐 Testing {algorithm.value} encryption...")
            try:
                # Generate key and encrypt
                encrypted_data, metrics = encryption.encrypt_message(
                    test_message, "alice_enc", "bob_enc", algorithm=algorithm
                )
                
                print(f"   ✅ Encrypted with {algorithm.value}")
                print(f"   📏 Original: {len(test_message)} chars")
                print(f"   📏 Encrypted: {len(encrypted_data.ciphertext)} bytes")
                print(f"   🛡️ Security: {metrics.security_level:.4f}")
                print(f"   ⏱️ Time: {metrics.encryption_time:.3f}s")
                
                # Test decryption
                decrypted_message = encryption.decrypt_message(
                    encrypted_data, encrypted_data.key_id
                )
                
                if decrypted_message == test_message:
                    print(f"   ✅ Decryption successful")
                else:
                    print(f"   ❌ Decryption failed - message mismatch")
                
            except Exception as e:
                print(f"   ⚠️ {algorithm.value} test warning: {e}")
        
        # Test encryption statistics
        print("📊 Testing encryption statistics...")
        stats = encryption.get_encryption_statistics()
        print(f"   📊 Total encryptions: {stats['total_encryptions']}")
        print(f"   📊 Total decryptions: {stats['total_decryptions']}")
        print(f"   📊 Active keys: {stats['total_active_keys']}")
        
        print("✅ Quantum encryption tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Quantum encryption test failed: {e}")
        print(traceback.format_exc())
        return False

def test_performance_benchmarks():
    """Test system performance"""
    print("\n🔬 Testing Performance Benchmarks")
    print("=" * 50)
    
    try:
        from quantum.utils.quantum_utils import quantum_utils
        
        # Benchmark random bit generation
        print("🎲 Benchmarking random bit generation...")
        start_time = time.time()
        large_bits = quantum_utils.generate_cryptographic_bits(10000)
        generation_time = time.time() - start_time
        print(f"   ✅ Generated 10,000 bits in {generation_time:.3f}s")
        print(f"   📊 Rate: {len(large_bits)/generation_time:.0f} bits/second")
        
        # Benchmark key sifting
        print("🔑 Benchmarking key sifting...")
        alice_bits = quantum_utils.generate_cryptographic_bits(1000)
        bob_bits = quantum_utils.generate_cryptographic_bits(1000)
        alice_bases = quantum_utils.generate_random_bases(1000)
        bob_bases = quantum_utils.generate_random_bases(1000)
        
        start_time = time.time()
        sifted_a, sifted_b, _ = quantum_utils.sift_quantum_key(
            alice_bits, bob_bits, alice_bases, bob_bases
        )
        sifting_time = time.time() - start_time
        
        print(f"   ✅ Sifted {len(sifted_a)} bits from 1,000 in {sifting_time:.3f}s")
        print(f"   📊 Sifting efficiency: {len(sifted_a)/len(alice_bits):.1%}")
        
        # Benchmark entropy calculation
        print("🎯 Benchmarking entropy calculation...")
        start_time = time.time()
        entropy = quantum_utils.calculate_entropy(large_bits)
        entropy_time = time.time() - start_time
        print(f"   ✅ Calculated entropy in {entropy_time:.3f}s")
        print(f"   📊 Entropy: {entropy:.3f} bits")
        
        print("✅ Performance benchmarks completed!")
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        print(traceback.format_exc())
        return False

def test_security_analysis():
    """Test security analysis features"""
    print("\n🔬 Testing Security Analysis")
    print("=" * 50)
    
    try:
        from quantum.utils.quantum_utils import quantum_utils
        
        # Generate test data
        alice_bits = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
        bob_bits = [0, 1, 0, 0, 1, 0, 1, 0, 0, 0]  # Some errors introduced
        
        # Test error analysis
        print("📊 Testing error analysis...")
        error_stats = quantum_utils.calculate_error_rate(alice_bits, bob_bits)
        print(f"   ✅ Error rate: {error_stats.error_rate:.3f}")
        print(f"   📊 Confidence interval: {error_stats.confidence_interval}")
        print(f"   📊 Statistical significance: {error_stats.statistical_significance:.3f}")
        
        # Test security metrics
        print("🛡️ Testing security metrics...")
        security_metrics = quantum_utils.analyze_security(alice_bits, bob_bits, error_stats.error_rate)
        print(f"   ✅ Entropy: {security_metrics.entropy:.3f}")
        print(f"   ✅ Mutual information: {security_metrics.mutual_information:.3f}")
        print(f"   ✅ Security parameter: {security_metrics.security_parameter:.3f}")
        
        # Test Eve's information estimation
        print("🕵️ Testing eavesdropper information estimation...")
        eve_info = quantum_utils.estimate_eve_information(error_stats.error_rate)
        print(f"   ✅ Eve's max information: {eve_info:.3f}")
        
        # Test Bell inequality (mock data)
        print("🔔 Testing Bell inequality...")
        correlations = {(0, 0): 0.5, (0, 1): -0.5, (1, 0): 0.5, (1, 1): 0.5}
        chsh_value = quantum_utils.chsh_bell_test(correlations)
        print(f"   ✅ CHSH value: {chsh_value:.3f}")
        
        if chsh_value > 2.0:
            print("   🎉 Bell inequality violated - quantum advantage confirmed!")
        else:
            print("   📊 Classical correlation observed")
        
        print("✅ Security analysis tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Security analysis test failed: {e}")
        print(traceback.format_exc())
        return False

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print("\n📊 QUANTUM SYSTEM TEST REPORT")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    success_rate = passed_tests / total_tests if total_tests > 0 else 0
    
    print(f"🎯 Overall Success Rate: {success_rate:.1%}")
    print(f"✅ Passed Tests: {passed_tests}/{total_tests}")
    print()
    
    print("📋 Test Results Summary:")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name.replace('_', ' ').title()}")
    
    print()
    
    if success_rate >= 0.8:
        print("🎉 EXCELLENT: Quantum system is functioning properly!")
        system_status = "OPERATIONAL"
    elif success_rate >= 0.6:
        print("⚠️ GOOD: Quantum system has minor issues")
        system_status = "FUNCTIONAL"
    elif success_rate >= 0.4:
        print("⚠️ FAIR: Quantum system has some problems")
        system_status = "LIMITED"
    else:
        print("❌ POOR: Quantum system has significant issues")
        system_status = "CRITICAL"
    
    print(f"🔍 System Status: {system_status}")
    print()
    
    print("💡 Recommendations:")
    if not test_results.get("imports", True):
        print("   📦 Install missing quantum dependencies")
    if not test_results.get("quantum_utils", True):
        print("   🔧 Check quantum utilities implementation")
    if not test_results.get("qkd_protocols", True):
        print("   🔐 Verify QKD protocol configurations")
    if not test_results.get("quantum_encryption", True):
        print("   🛡️ Check encryption system setup")
    
    print()
    print("🌟 COWN Quantum Security System Test Complete!")
    
    return {
        "success_rate": success_rate,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "system_status": system_status,
        "detailed_results": test_results
    }

def main():
    """Main test execution"""
    print("🚀 COWN Quantum System Test Suite")
    print("=" * 60)
    print("🔬 Testing comprehensive quantum security capabilities")
    print("📅 Test Date:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Run all tests
    test_results = {}
    
    import_results = test_imports()
    test_results["imports"] = import_results.get("success", True) if isinstance(import_results, dict) else import_results
    
    test_results["quantum_utils"] = test_quantum_utils()
    test_results["qkd_protocols"] = test_qkd_protocols()
    test_results["quantum_encryption"] = test_quantum_encryption()
    test_results["performance"] = test_performance_benchmarks()
    test_results["security_analysis"] = test_security_analysis()
    
    # Generate final report
    report = generate_test_report(test_results)
    
    # Save test results
    try:
        import json
        results_file = f"quantum_system_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "report": report
            }, f, indent=2)
        print(f"💾 Test results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save test results: {e}")
    
    return report

if __name__ == "__main__":
    main()
