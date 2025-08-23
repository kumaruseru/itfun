"""
Simple QKD Test
Test basic functionality without complex quantum operations
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from protocols.qkd_protocol import QKDManager, ProtocolType
    print("✅ QKD Manager imported successfully")
    
    # Test basic import
    manager = QKDManager()
    print("✅ QKD Manager created")
    
    # Test system status
    status = manager.get_system_status()
    print(f"📊 System Status: {status}")
    
    # Test simple BB84 with smaller key
    print("\n🔬 Testing Simple BB84...")
    try:
        session = manager.start_bb84_session("alice", "bob", key_length=64)
        print(f"✅ BB84 Session created: {session.session_id}")
        print(f"🔐 Key length: {session.key_length}")
        print(f"🛡️ Security: {session.security_level:.4f}")
        print(f"📊 Error rate: {session.error_rate:.4f}")
        
        # Terminate session
        manager.terminate_session(session.session_id)
        print("✅ Session terminated")
        
    except Exception as e:
        print(f"❌ BB84 failed: {e}")
    
    # Test SARG04 with smaller key
    print("\n🔬 Testing Simple SARG04...")
    try:
        session = manager.start_sarg04_session("alice2", "bob2", key_length=64)
        print(f"✅ SARG04 Session created: {session.session_id}")
        print(f"🔐 Key length: {session.key_length}")
        print(f"🛡️ Security: {session.security_level:.4f}")
        print(f"📊 Error rate: {session.error_rate:.4f}")
        
        if hasattr(session.quantum_key, 'sarg_efficiency'):
            print(f"⚡ SARG efficiency: {session.quantum_key.sarg_efficiency:.4f}")
        
        # Terminate session
        manager.terminate_session(session.session_id)
        print("✅ Session terminated")
        
    except Exception as e:
        print(f"❌ SARG04 failed: {e}")
    
    print("\n🎉 Simple QKD Test Completed!")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Test failed: {e}")
