/*
COWN Quantum Controller
API endpoints cho hệ thống lượng tử

Features:
- QKD session management
- Quantum encryption/decryption
- Security analysis
- Performance monitoring
- Key management
*/

const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class QuantumController {
    constructor() {
        this.pythonPath = process.env.PYTHON_PATH || 'python';
        this.quantumScriptPath = path.join(__dirname, '..', '..', 'quantum');
    }

    // Utility method to execute Python quantum scripts
    async executePythonScript(scriptName, args = []) {
        return new Promise((resolve, reject) => {
            const scriptPath = path.join(this.quantumScriptPath, scriptName);
            const python = spawn(this.pythonPath, [scriptPath, ...args]);
            
            let stdout = '';
            let stderr = '';
            
            python.stdout.on('data', (data) => {
                stdout += data.toString();
            });
            
            python.stderr.on('data', (data) => {
                stderr += data.toString();
            });
            
            python.on('close', (code) => {
                if (code === 0) {
                    try {
                        resolve(JSON.parse(stdout));
                    } catch (e) {
                        resolve({ success: true, output: stdout });
                    }
                } else {
                    reject(new Error(`Python script failed: ${stderr}`));
                }
            });
        });
    }

    // Start QKD session
    async startQKDSession(req, res) {
        try {
            const { alice_id, bob_id, protocol = 'BB84', key_length = 256 } = req.body;
            
            if (!alice_id || !bob_id) {
                return res.status(400).json({
                    success: false,
                    error: 'alice_id and bob_id are required'
                });
            }

            // Create Python script to start QKD session
            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

from protocols.qkd_protocol import qkd_manager, ProtocolType

try:
    if '${protocol}' == 'BB84':
        session = qkd_manager.start_bb84_session('${alice_id}', '${bob_id}', ${key_length})
    else:
        session = qkd_manager.start_e91_session('${alice_id}', '${bob_id}', ${key_length})
    
    result = {
        'success': True,
        'session': {
            'session_id': session.session_id,
            'alice_id': session.alice_id,
            'bob_id': session.bob_id,
            'protocol': session.protocol.value,
            'key_length': session.key_length,
            'security_level': session.security_level,
            'error_rate': session.error_rate,
            'status': session.status
        }
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            // Write and execute script
            const tempScript = path.join(this.quantumScriptPath, 'temp_qkd_start.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_qkd_start.py');
            
            // Clean up
            await fs.unlink(tempScript);
            
            if (result.success) {
                res.json(result);
            } else {
                res.status(500).json(result);
            }
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Encrypt message with quantum security
    async encryptMessage(req, res) {
        try {
            const { 
                message, 
                alice_id, 
                bob_id, 
                algorithm = 'AES_QUANTUM',
                protocol = 'BB84' 
            } = req.body;
            
            if (!message || !alice_id || !bob_id) {
                return res.status(400).json({
                    success: false,
                    error: 'message, alice_id, and bob_id are required'
                });
            }

            const scriptContent = `
import sys
import json
import base64
sys.path.append('${this.quantumScriptPath}')

from encryption.quantum_encryptor import quantum_encryption, EncryptionAlgorithm, ProtocolType

try:
    # Map algorithm name
    algo_map = {
        'QUANTUM_OTP': EncryptionAlgorithm.QUANTUM_OTP,
        'AES_QUANTUM': EncryptionAlgorithm.AES_QUANTUM,
        'CHACHA20_QUANTUM': EncryptionAlgorithm.CHACHA20_QUANTUM
    }
    
    protocol_map = {
        'BB84': ProtocolType.BB84,
        'E91': ProtocolType.E91
    }
    
    algorithm = algo_map.get('${algorithm}', EncryptionAlgorithm.AES_QUANTUM)
    protocol = protocol_map.get('${protocol}', ProtocolType.BB84)
    
    encrypted_data, metrics = quantum_encryption.encrypt_message(
        '''${message}''', '${alice_id}', '${bob_id}', algorithm, protocol
    )
    
    result = {
        'success': True,
        'encrypted_data': {
            'ciphertext': base64.b64encode(encrypted_data.ciphertext).decode(),
            'key_id': encrypted_data.key_id,
            'algorithm': encrypted_data.algorithm.value,
            'nonce': base64.b64encode(encrypted_data.nonce).decode() if encrypted_data.nonce else None,
            'quantum_signature': base64.b64encode(encrypted_data.quantum_signature).decode(),
            'metadata': encrypted_data.metadata
        },
        'metrics': {
            'algorithm': metrics.algorithm.value,
            'key_length': metrics.key_length,
            'message_length': metrics.message_length,
            'encryption_time': metrics.encryption_time,
            'security_level': metrics.security_level,
            'quantum_enhanced': metrics.quantum_enhanced
        }
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_encrypt.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_encrypt.py');
            
            await fs.unlink(tempScript);
            
            if (result.success) {
                res.json(result);
            } else {
                res.status(500).json(result);
            }
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Decrypt message
    async decryptMessage(req, res) {
        try {
            const { encrypted_data, key_id } = req.body;
            
            if (!encrypted_data || !key_id) {
                return res.status(400).json({
                    success: false,
                    error: 'encrypted_data and key_id are required'
                });
            }

            const scriptContent = `
import sys
import json
import base64
sys.path.append('${this.quantumScriptPath}')

from encryption.quantum_encryptor import quantum_encryption, QuantumEncryptedData, EncryptionAlgorithm

try:
    # Reconstruct encrypted data object
    algo_map = {
        'quantum_otp': EncryptionAlgorithm.QUANTUM_OTP,
        'aes_quantum': EncryptionAlgorithm.AES_QUANTUM,
        'chacha20_quantum': EncryptionAlgorithm.CHACHA20_QUANTUM
    }
    
    encrypted_obj = QuantumEncryptedData(
        ciphertext=base64.b64decode('${encrypted_data.ciphertext}'),
        key_id='${encrypted_data.key_id}',
        algorithm=algo_map['${encrypted_data.algorithm}'],
        nonce=base64.b64decode('${encrypted_data.nonce}') if '${encrypted_data.nonce}' != 'None' else None,
        auth_tag=base64.b64decode('${encrypted_data.auth_tag}') if '${encrypted_data.auth_tag}' else None,
        quantum_signature=base64.b64decode('${encrypted_data.quantum_signature}'),
        metadata=${JSON.stringify(encrypted_data.metadata)}
    )
    
    decrypted_message = quantum_encryption.decrypt_message(encrypted_obj, '${key_id}')
    
    result = {
        'success': True,
        'message': decrypted_message
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_decrypt.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_decrypt.py');
            
            await fs.unlink(tempScript);
            
            if (result.success) {
                res.json(result);
            } else {
                res.status(500).json(result);
            }
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get QKD system statistics
    async getQKDStatistics(req, res) {
        try {
            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

from protocols.qkd_protocol import qkd_manager

try:
    stats = qkd_manager.get_session_statistics()
    result = {
        'success': True,
        'statistics': stats
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_stats.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_stats.py');
            
            await fs.unlink(tempScript);
            
            res.json(result);
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get encryption statistics
    async getEncryptionStatistics(req, res) {
        try {
            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

from encryption.quantum_encryptor import quantum_encryption

try:
    stats = quantum_encryption.get_encryption_statistics()
    result = {
        'success': True,
        'statistics': stats
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_enc_stats.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_enc_stats.py');
            
            await fs.unlink(tempScript);
            
            res.json(result);
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Terminate QKD session
    async terminateSession(req, res) {
        try {
            const { session_id } = req.params;
            
            if (!session_id) {
                return res.status(400).json({
                    success: false,
                    error: 'session_id is required'
                });
            }

            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

from protocols.qkd_protocol import qkd_manager

try:
    success = qkd_manager.terminate_session('${session_id}')
    result = {
        'success': success,
        'session_id': '${session_id}'
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_terminate.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_terminate.py');
            
            await fs.unlink(tempScript);
            
            res.json(result);
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Security analysis endpoint
    async analyzeSecuritys(req, res) {
        try {
            const { error_rate, key_length, protocol } = req.query;
            
            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

from utils.quantum_utils import security_analyzer

try:
    metrics = security_analyzer.analyze_qkd_security(
        ${parseFloat(error_rate) || 0.0}, 
        ${parseInt(key_length) || 256}, 
        '${protocol || 'BB84'}'
    )
    
    attack_resistance = security_analyzer.estimate_attack_resistance(
        metrics.overall_security,
        ${parseInt(key_length) || 256}
    )
    
    result = {
        'success': True,
        'security_metrics': {
            'information_theoretic_security': metrics.information_theoretic_security,
            'computational_security': metrics.computational_security,
            'quantum_resistance': metrics.quantum_resistance,
            'overall_security': metrics.overall_security,
            'vulnerabilities': metrics.vulnerabilities
        },
        'attack_resistance': attack_resistance
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_security.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_security.py');
            
            await fs.unlink(tempScript);
            
            res.json(result);
            
        } catch (error) {
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Health check endpoint
    async healthCheck(req, res) {
        try {
            const scriptContent = `
import sys
import json
sys.path.append('${this.quantumScriptPath}')

try:
    import pennylane as qml
    import numpy as np
    from protocols.qkd_protocol import qkd_manager
    from encryption.quantum_encryptor import quantum_encryption
    
    # Test basic functionality
    device = qml.device("default.qubit", wires=2)
    
    result = {
        'success': True,
        'status': 'healthy',
        'components': {
            'pennylane': True,
            'qkd_protocols': True,
            'quantum_encryption': True,
            'device_available': True
        },
        'system_info': {
            'active_sessions': len(qkd_manager.active_sessions),
            'quantum_keys': len(qkd_manager.quantum_keys),
            'encryption_cache': len(quantum_encryption.encryption_cache)
        }
    }
    print(json.dumps(result))
    
except Exception as e:
    result = {
        'success': False,
        'status': 'unhealthy',
        'error': str(e)
    }
    print(json.dumps(result))
`;

            const tempScript = path.join(this.quantumScriptPath, 'temp_health.py');
            await fs.writeFile(tempScript, scriptContent);
            
            const result = await this.executePythonScript('temp_health.py');
            
            await fs.unlink(tempScript);
            
            res.json(result);
            
        } catch (error) {
            res.status(500).json({
                success: false,
                status: 'unhealthy',
                error: error.message
            });
        }
    }
}

module.exports = new QuantumController();
