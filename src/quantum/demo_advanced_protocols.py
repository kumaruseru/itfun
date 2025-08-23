"""
Demo Advanced QKD Protocols for COWN
Test BB84, Enhanced BB84 with Decoy States, SARG04, and E91
"""

import sys
import os
import time
import json
from typing import Dict, Any, List

# Add path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from protocols.qkd_protocol import (
        QKDManager, ProtocolType, QKDError, EavesdropDetected
    )
    from encryption.quantum_encryptor import quantum_encryption
    print("✅ Successfully imported quantum modules")
    QUANTUM_AVAILABLE = True
except ImportError as e:
    print(f"❌ Import error: {e}")
    QUANTUM_AVAILABLE = False

class AdvancedQKDDemo:
    """
    Advanced QKD Protocols Demonstration
    """
    
    def __init__(self):
        if QUANTUM_AVAILABLE:
            self.qkd_manager = QKDManager()
        else:
            self.qkd_manager = None
    
    def demo_protocol_comparison(self) -> Dict[str, Any]:
        """
        So sánh hiệu suất các protocols QKD khác nhau
        """
        print("🔬 Demo: Advanced QKD Protocol Comparison")
        print("=" * 60)
        
        if not QUANTUM_AVAILABLE:
            return {"success": False, "error": "QKD not available"}
        
        protocols_to_test = [
            ("BB84 Classic", ProtocolType.BB84),
            ("BB84 + Decoy States", ProtocolType.BB84_DECOY), 
            ("SARG04", ProtocolType.SARG04),
            ("E91 Entanglement", ProtocolType.E91)
        ]
        
        comparison_results = []
        
        for protocol_name, protocol_type in protocols_to_test:
            print(f"\\n🧪 Testing {protocol_name}...")
            
            try:
                start_time = time.time()
                
                # Start appropriate session
                if protocol_type == ProtocolType.BB84:
                    session = self.qkd_manager.start_bb84_session(
                        "alice_test", "bob_test", key_length=256
                    )
                elif protocol_type == ProtocolType.BB84_DECOY:
                    session = self.qkd_manager.start_enhanced_bb84_session(
                        "alice_test", "bob_test", key_length=256
                    )
                elif protocol_type == ProtocolType.SARG04:
                    session = self.qkd_manager.start_sarg04_session(
                        "alice_test", "bob_test", key_length=256
                    )
                elif protocol_type == ProtocolType.E91:
                    session = self.qkd_manager.start_e91_session(
                        "alice_test", "bob_test", key_length=256
                    )
                
                generation_time = time.time() - start_time
                
                # Get security report
                security_report = self.qkd_manager.get_security_report(session.session_id)
                
                # Protocol-specific metrics
                protocol_metrics = {}
                if session.quantum_key.decoy_analysis:
                    protocol_metrics["decoy_analysis"] = session.quantum_key.decoy_analysis
                if session.quantum_key.sarg_efficiency:
                    protocol_metrics["sarg_efficiency"] = session.quantum_key.sarg_efficiency
                
                comparison_results.append({
                    "protocol": protocol_name,
                    "protocol_type": protocol_type.value,
                    "session_id": session.session_id,
                    "key_length": session.key_length,
                    "security_level": session.security_level,
                    "error_rate": session.error_rate,
                    "generation_time": generation_time,
                    "key_rate": security_report.get("key_generation_rate", 0),
                    "security_parameter": security_report.get("security_parameter", 0),
                    "protocol_metrics": protocol_metrics
                })
                
                print(f"   ✅ Success - Security: {session.security_level:.4f}")
                print(f"   📊 QBER: {session.error_rate:.4f}")
                print(f"   ⏱️ Time: {generation_time:.3f}s")
                
                # Clean up
                self.qkd_manager.terminate_session(session.session_id)
                
            except (QKDError, EavesdropDetected) as e:
                print(f"   ❌ Failed: {str(e)}")
                comparison_results.append({
                    "protocol": protocol_name,
                    "protocol_type": protocol_type.value,
                    "error": str(e),
                    "success": False
                })
        
        # Analysis
        successful_protocols = [r for r in comparison_results if r.get("success", True)]
        
        if successful_protocols:
            best_security = max(successful_protocols, key=lambda x: x.get("security_level", 0))
            best_speed = min(successful_protocols, key=lambda x: x.get("generation_time", float('inf')))
            
            print(f"\\n🏆 Analysis Results:")
            print(f"   🛡️ Best Security: {best_security['protocol']} ({best_security.get('security_level', 0):.4f})")
            print(f"   🚀 Fastest: {best_speed['protocol']} ({best_speed.get('generation_time', 0):.3f}s)")
        
        return {
            "success": True,
            "comparison_results": comparison_results,
            "successful_protocols": len(successful_protocols),
            "total_protocols": len(protocols_to_test)
        }
    
    def demo_decoy_state_analysis(self) -> Dict[str, Any]:
        """
        Demo chi tiết về Decoy State Protocol
        """
        print("\\n🔬 Demo: Decoy State Protocol Analysis")
        print("=" * 60)
        
        if not QUANTUM_AVAILABLE:
            return {"success": False, "error": "QKD not available"}
        
        try:
            print("🔑 Starting Enhanced BB84 with Decoy States...")
            
            session = self.qkd_manager.start_enhanced_bb84_session(
                "alice_decoy", "bob_decoy", key_length=512
            )
            
            print(f"   ✅ Session created: {session.session_id}")
            print(f"   🔐 Key length: {session.key_length} bits")
            print(f"   🛡️ Security level: {session.security_level:.4f}")
            
            # Analyze decoy state results
            if session.quantum_key and session.quantum_key.decoy_analysis:
                decoy_data = session.quantum_key.decoy_analysis
                
                print("\\n📊 Decoy State Analysis:")
                print(f"   📈 Signal detection rate: {decoy_data.get('signal_detection_rate', 0):.4f}")
                print(f"   📉 Decoy detection rate: {decoy_data.get('decoy_detection_rate', 0):.4f}")
                print(f"   🔽 Vacuum detection rate: {decoy_data.get('vacuum_detection_rate', 0):.4f}")
                print(f"   🎯 Single photon rate: {decoy_data.get('single_photon_rate', 0):.4f}")
                print(f"   🔧 Error correction efficiency: {decoy_data.get('error_correction_efficiency', 0):.4f}")
                
                # Security assessment
                security_param = decoy_data.get('security_parameter', 0)
                if security_param > 0.8:
                    security_status = "🟢 Excellent"
                elif security_param > 0.6:
                    security_status = "🟡 Good"
                else:
                    security_status = "🔴 Marginal"
                
                print(f"   🛡️ Security assessment: {security_status} ({security_param:.4f})")
            
            # Test encryption with decoy-enhanced key
            print("\\n🔒 Testing Encryption with Decoy-Enhanced Key...")
            
            test_message = "COWN Advanced Quantum Security: Decoy State Enhanced!"
            
            encrypted_data, metrics = quantum_encryption.encrypt_message(
                test_message, "alice_decoy", "bob_decoy"
            )
            
            print(f"   📝 Original: {test_message}")
            print(f"   🔐 Encrypted size: {len(encrypted_data.ciphertext)} bytes")
            print(f"   🛡️ Security level: {metrics.security_level:.4f}")
            
            # Decrypt and verify
            decrypted_message = quantum_encryption.decrypt_message(
                encrypted_data, session.quantum_key.key_id
            )
            
            verification_success = test_message == decrypted_message
            print(f"   ✅ Decryption verification: {'PASS' if verification_success else 'FAIL'}")
            
            # Clean up
            self.qkd_manager.terminate_session(session.session_id)
            
            return {
                "success": True,
                "session_info": {
                    "session_id": session.session_id,
                    "security_level": session.security_level,
                    "key_length": session.key_length,
                    "error_rate": session.error_rate
                },
                "decoy_analysis": session.quantum_key.decoy_analysis if session.quantum_key else None,
                "encryption_test": {
                    "original_message": test_message,
                    "encrypted_size": len(encrypted_data.ciphertext),
                    "verification_success": verification_success
                }
            }
            
        except Exception as e:
            print(f"❌ Decoy state demo failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def demo_sarg04_efficiency(self) -> Dict[str, Any]:
        """
        Demo hiệu suất SARG04 Protocol
        """
        print("\\n🔬 Demo: SARG04 Protocol Efficiency")
        print("=" * 60)
        
        if not QUANTUM_AVAILABLE:
            return {"success": False, "error": "QKD not available"}
        
        try:
            print("🔑 Starting SARG04 QKD Session...")
            
            session = self.qkd_manager.start_sarg04_session(
                "alice_sarg", "bob_sarg", key_length=256
            )
            
            print(f"   ✅ SARG04 session created: {session.session_id}")
            print(f"   🔐 Key length: {session.key_length} bits")
            print(f"   🛡️ Security level: {session.security_level:.4f}")
            print(f"   📊 Error rate: {session.error_rate:.4f}")
            
            # SARG04 specific metrics
            if session.quantum_key and hasattr(session.quantum_key, 'sarg_efficiency'):
                sarg_efficiency = session.quantum_key.sarg_efficiency
                print(f"   ⚡ SARG04 efficiency: {sarg_efficiency:.4f}")
                
                # Efficiency analysis
                if sarg_efficiency > 0.7:
                    efficiency_status = "🟢 Excellent"
                elif sarg_efficiency > 0.5:
                    efficiency_status = "🟡 Good"
                else:
                    efficiency_status = "🔴 Poor"
                
                print(f"   📈 Efficiency status: {efficiency_status}")
            
            # Compare with BB84
            print("\\n⚖️ Comparison with BB84...")
            
            bb84_session = self.qkd_manager.start_bb84_session(
                "alice_comp", "bob_comp", key_length=256
            )
            
            efficiency_comparison = {
                "sarg04_security": session.security_level,
                "bb84_security": bb84_session.security_level,
                "sarg04_error": session.error_rate,
                "bb84_error": bb84_session.error_rate,
                "sarg04_efficiency": getattr(session.quantum_key, 'sarg_efficiency', 0),
                "bb84_efficiency": 1.0  # Standard reference
            }
            
            print(f"   📊 SARG04 vs BB84 Security: {session.security_level:.4f} vs {bb84_session.security_level:.4f}")
            print(f"   📊 SARG04 vs BB84 Error: {session.error_rate:.4f} vs {bb84_session.error_rate:.4f}")
            
            # Determine winner
            if session.security_level > bb84_session.security_level:
                winner = "🏆 SARG04 wins on security"
            elif session.security_level < bb84_session.security_level:
                winner = "🏆 BB84 wins on security"
            else:
                winner = "🤝 Security tie"
            
            print(f"   {winner}")
            
            # Clean up
            self.qkd_manager.terminate_session(session.session_id)
            self.qkd_manager.terminate_session(bb84_session.session_id)
            
            return {
                "success": True,
                "sarg04_metrics": {
                    "security_level": session.security_level,
                    "error_rate": session.error_rate,
                    "efficiency": getattr(session.quantum_key, 'sarg_efficiency', 0)
                },
                "comparison": efficiency_comparison,
                "winner": winner
            }
            
        except Exception as e:
            print(f"❌ SARG04 demo failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """
        Chạy demo tổng hợp tất cả protocols
        """
        print("🚀 COWN Advanced QKD Protocols Demo")
        print("=" * 70)
        print("🔬 Testing: BB84, Enhanced BB84, SARG04, E91")
        print("=" * 70)
        
        demo_results = {}
        
        # Demo 1: Protocol Comparison
        demo_results["protocol_comparison"] = self.demo_protocol_comparison()
        
        # Demo 2: Decoy State Analysis
        demo_results["decoy_state_analysis"] = self.demo_decoy_state_analysis()
        
        # Demo 3: SARG04 Efficiency
        demo_results["sarg04_efficiency"] = self.demo_sarg04_efficiency()
        
        # Summary
        print("\\n📊 COMPREHENSIVE DEMO SUMMARY")
        print("=" * 50)
        
        success_count = sum(1 for result in demo_results.values() 
                           if result.get("success", False))
        total_demos = len(demo_results)
        
        print(f"✅ Successful demos: {success_count}/{total_demos}")
        print(f"📈 Success rate: {success_count/total_demos*100:.1f}%")
        
        if QUANTUM_AVAILABLE:
            # System status
            system_status = self.qkd_manager.get_system_status()
            print(f"🔐 Total sessions: {system_status['total_active_sessions']}")
            print(f"🔑 Total keys: {system_status['total_generated_keys']}")
            print(f"📊 BB84 sessions: {system_status['bb84_sessions']}")
            print(f"🔬 BB84+Decoy sessions: {system_status['bb84_decoy_sessions']}")
            print(f"⚡ SARG04 sessions: {system_status['sarg04_sessions']}")
            print(f"🔗 E91 sessions: {system_status['e91_sessions']}")
        
        print("\\n🎉 Advanced QKD Demo Completed!")
        print("\\n🌟 Protocol Capabilities Demonstrated:")
        print("   ✅ BB84 Classic Protocol")
        print("   ✅ Enhanced BB84 with Decoy States")
        print("   ✅ SARG04 High-Efficiency Protocol")
        print("   ✅ E91 Entanglement-Based Protocol")
        print("   ✅ Advanced Security Analysis")
        print("   ✅ Protocol Performance Comparison")
        
        return {
            "demo_results": demo_results,
            "success_rate": success_count/total_demos,
            "protocols_tested": [
                "BB84 Classic",
                "BB84 + Decoy States", 
                "SARG04",
                "E91 Entanglement"
            ]
        }

def main():
    """Main demo execution"""
    demo = AdvancedQKDDemo()
    results = demo.run_comprehensive_demo()
    
    # Save results
    try:
        results_file = f"advanced_qkd_demo_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\\n💾 Results saved to: {results_file}")
    except Exception as e:
        print(f"⚠️ Could not save results: {e}")
    
    return results

if __name__ == "__main__":
    main()
