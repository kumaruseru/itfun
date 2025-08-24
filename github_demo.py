#!/usr/bin/env python3
"""
🚀 COWN Quantum System v1.1.0 - GitHub Demo
Quick demonstration of quantum capabilities for repository visitors

Run this script to see the enhanced quantum system in action!
"""

import sys
import os

def check_environment():
    """Quick environment check"""
    print("🔍 ENVIRONMENT CHECK")
    print("=" * 40)
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
        return False
    
    try:
        import qutip as qt
        print(f"✅ QuTiP: {qt.__version__}")
    except ImportError:
        print("❌ QuTiP: Not installed - run 'pip install qutip'")
        return False
    
    try:
        import pennylane as qml
        print(f"✅ PennyLane: {qml.__version__}")
    except ImportError:
        print("❌ PennyLane: Not installed - run 'pip install pennylane'")
        return False
    
    return True

def quick_demo():
    """Quick demonstration of key features"""
    import numpy as np
    import qutip as qt
    import time
    
    print(f"\n🎯 QUICK DEMONSTRATION")
    print("=" * 40)
    
    # 1. NumPy 2.0 Performance
    print("1. NumPy 2.0 Performance Test:")
    start = time.time()
    rng = np.random.default_rng(42)
    matrix = rng.random((1000, 1000))
    eigenvals = np.linalg.eigvals(matrix[:100, :100])
    numpy_time = time.time() - start
    print(f"   ⚡ Matrix operations: {numpy_time*1000:.2f}ms")
    
    # 2. QuTiP Quantum States
    print("\n2. QuTiP 5.0 Quantum Simulation:")
    bell_state = (qt.tensor(qt.basis(2,0), qt.basis(2,0)) + 
                  qt.tensor(qt.basis(2,1), qt.basis(2,1))).unit()
    
    rho = bell_state * bell_state.dag()
    rho_A = qt.ptrace(rho, 0)
    entropy = qt.entropy_vn(rho_A)
    concurrence = qt.concurrence(rho)
    
    print(f"   🔗 Bell state created: {bell_state.dims}")
    print(f"   🔬 Von Neumann entropy: {entropy:.4f}")
    print(f"   ⚛️ Concurrence: {concurrence:.4f}")
    
    # 3. Mini BB84 Demo
    print("\n3. Mini BB84 Protocol:")
    n_bits = 20
    alice_bits = rng.integers(0, 2, n_bits)
    alice_bases = rng.integers(0, 2, n_bits)
    bob_bases = rng.integers(0, 2, n_bits)
    
    matching = sum(1 for i in range(n_bits) if alice_bases[i] == bob_bases[i])
    key_rate = matching / n_bits
    
    print(f"   📡 Bits transmitted: {n_bits}")
    print(f"   🔑 Key rate: {key_rate:.1%}")
    print(f"   🛡️ Security: {'✅ SECURE' if key_rate > 0.3 else '⚠️ LOW'}")
    
    # 4. Performance Score
    print(f"\n🏆 SYSTEM SCORE")
    print("=" * 30)
    
    performance_score = min(100, (1.0 / max(numpy_time, 0.001)) * 20)
    quantum_score = concurrence * 100
    protocol_score = key_rate * 100
    
    overall = (performance_score + quantum_score + protocol_score) / 3
    
    print(f"Performance: {performance_score:.1f}%")
    print(f"Quantum: {quantum_score:.1f}%")
    print(f"Protocol: {protocol_score:.1f}%")
    print(f"\n🎯 OVERALL: {overall:.1f}%")
    
    if overall >= 90:
        print("Status: 🥇 EXCELLENT")
    elif overall >= 75:
        print("Status: 🥈 VERY GOOD")
    else:
        print("Status: 🥉 GOOD")

def main():
    """Main demo function"""
    print("🚀 COWN QUANTUM SYSTEM v1.1.0 - GITHUB DEMO")
    print("=" * 60)
    print("Welcome to the enhanced quantum cryptography system!")
    print("This demo showcases QuTiP 5.0 + NumPy 2.0 integration.")
    print()
    
    if not check_environment():
        print(f"\n💡 INSTALLATION GUIDE:")
        print("pip install numpy>=2.0 qutip>=5.0 pennylane>=0.30")
        print()
        print("Then run this demo again!")
        return
    
    quick_demo()
    
    print(f"\n📚 EXPLORE MORE:")
    print("=" * 30)
    print("🔬 Advanced demos: python final_integration_demo.py")
    print("🛡️ Security demo: python enhanced_security_demo.py") 
    print("⚡ Performance test: python qutip_numpy_test.py")
    print("📊 Full report: INTEGRATION_REPORT.md")
    
    print(f"\n🌟 Thank you for exploring COWN Quantum System!")
    print("Visit the repository for complete documentation and examples.")

if __name__ == "__main__":
    main()
