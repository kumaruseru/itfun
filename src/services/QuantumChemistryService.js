/**
 * COWN Quantum Chemistry Service
 * Node.js integration for quantum molecular simulations
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class QuantumChemistryService {
    constructor() {
        this.pythonPath = 'C:/Users/nghia/cownV1.1.1/.venv/Scripts/python.exe';
        this.quantumPath = path.join(__dirname, '../quantum_chemistry');
        this.apiScript = path.join(this.quantumPath, 'quantum_api.py');
    }

    /**
     * Execute Python quantum chemistry analysis
     * @param {string} script - Python script to run
     * @param {Array} args - Command line arguments
     * @returns {Promise<Object>} Analysis results
     */
    async executePythonScript(script, args = []) {
        return new Promise((resolve, reject) => {
            const process = spawn(this.pythonPath, [script, ...args], {
                cwd: this.quantumPath,
                stdio: ['pipe', 'pipe', 'pipe']
            });

            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            process.on('close', (code) => {
                if (code === 0) {
                    try {
                        // Extract JSON from output
                        const jsonStart = stdout.indexOf('{');
                        const jsonEnd = stdout.lastIndexOf('}') + 1;
                        if (jsonStart !== -1 && jsonEnd > jsonStart) {
                            const jsonStr = stdout.substring(jsonStart, jsonEnd);
                            const result = JSON.parse(jsonStr);
                            resolve(result);
                        } else {
                            resolve({ success: true, output: stdout });
                        }
                    } catch (error) {
                        resolve({ success: true, output: stdout, raw: true });
                    }
                } else {
                    reject(new Error(`Python script failed: ${stderr}`));
                }
            });

            process.on('error', (error) => {
                reject(error);
            });
        });
    }

    /**
     * Analyze a molecule using quantum chemistry
     * @param {Array} geometry - Molecular geometry [[atom, [x, y, z]], ...]
     * @param {string} name - Molecule name
     * @returns {Promise<Object>} Quantum analysis results
     */
    async analyzeMolecule(geometry, name = 'Unknown') {
        try {
            // Create temporary analysis script
            const analysisScript = `
import sys
import json
sys.path.append('${this.quantumPath.replace(/\\/g, '/')}')
from quantum_api import quantum_api

geometry = ${JSON.stringify(geometry)}
name = "${name}"

result = quantum_api.analyze_molecule(geometry, name)
print(json.dumps(result, indent=2))
`;

            const tempScript = path.join(this.quantumPath, 'temp_analysis.py');
            await fs.writeFile(tempScript, analysisScript);

            const result = await this.executePythonScript(tempScript);
            
            // Clean up temp file
            await fs.unlink(tempScript).catch(() => {});

            return result;
        } catch (error) {
            return {
                success: false,
                error: error.message,
                service: 'QuantumChemistryService'
            };
        }
    }

    /**
     * Get quantum chemistry system status
     * @returns {Promise<Object>} System status
     */
    async getSystemStatus() {
        try {
            const statusScript = `
import sys
import json
sys.path.append('${this.quantumPath.replace(/\\/g, '/')}')
from quantum_api import quantum_api

status = quantum_api.get_system_status()
print(json.dumps(status, indent=2))
`;

            const tempScript = path.join(this.quantumPath, 'temp_status.py');
            await fs.writeFile(tempScript, statusScript);

            const result = await this.executePythonScript(tempScript);
            
            // Clean up temp file
            await fs.unlink(tempScript).catch(() => {});

            return result;
        } catch (error) {
            return {
                success: false,
                error: error.message,
                service: 'QuantumChemistryService'
            };
        }
    }

    /**
     * Analyze common molecules for demo
     * @returns {Promise<Object>} Common molecules analysis
     */
    async analyzeCommonMolecules() {
        try {
            const commonScript = `
import sys
import json
sys.path.append('${this.quantumPath.replace(/\\/g, '/')}')
from quantum_api import quantum_api

results = quantum_api.analyze_common_molecules()
print(json.dumps(results, indent=2))
`;

            const tempScript = path.join(this.quantumPath, 'temp_common.py');
            await fs.writeFile(tempScript, commonScript);

            const result = await this.executePythonScript(tempScript);
            
            // Clean up temp file
            await fs.unlink(tempScript).catch(() => {});

            return result;
        } catch (error) {
            return {
                success: false,
                error: error.message,
                service: 'QuantumChemistryService'
            };
        }
    }

    /**
     * Run quantum chemistry demo
     * @returns {Promise<Object>} Demo results
     */
    async runDemo() {
        try {
            const demoScript = path.join(this.quantumPath, 'demo_simple_molecules.py');
            const result = await this.executePythonScript(demoScript);
            
            return {
                success: true,
                demo_completed: true,
                output: result.output || result
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                service: 'QuantumChemistryService'
            };
        }
    }

    /**
     * Validate molecular geometry format
     * @param {Array} geometry - Molecular geometry to validate
     * @returns {boolean} Whether geometry is valid
     */
    validateGeometry(geometry) {
        if (!Array.isArray(geometry)) return false;
        
        return geometry.every(entry => {
            return Array.isArray(entry) && 
                   entry.length === 2 && 
                   typeof entry[0] === 'string' && 
                   Array.isArray(entry[1]) && 
                   entry[1].length === 3 &&
                   entry[1].every(coord => typeof coord === 'number');
        });
    }

    /**
     * Get predefined molecules for common use cases
     * @returns {Object} Predefined molecular geometries
     */
    getPredefinedMolecules() {
        return {
            hydrogen: {
                name: 'Hydrogen',
                formula: 'H2',
                geometry: [['H', [0.0, 0.0, 0.0]], ['H', [0.74, 0.0, 0.0]]],
                description: 'Simplest molecule - perfect for quantum simulation'
            },
            water: {
                name: 'Water',
                formula: 'H2O',
                geometry: [
                    ['O', [0.0, 0.0, 0.117]],
                    ['H', [0.0, 0.757, -0.467]],
                    ['H', [0.0, -0.757, -0.467]]
                ],
                description: 'Essential for life - H2O molecular structure'
            },
            methane: {
                name: 'Methane',
                formula: 'CH4',
                geometry: [
                    ['C', [0.0, 0.0, 0.0]],
                    ['H', [0.629, 0.629, 0.629]],
                    ['H', [-0.629, -0.629, 0.629]],
                    ['H', [0.629, -0.629, -0.629]],
                    ['H', [-0.629, 0.629, -0.629]]
                ],
                description: 'Simplest hydrocarbon - CH4 structure'
            },
            glycine: {
                name: 'Glycine',
                formula: 'C2H5NO2',
                geometry: [
                    ['C', [0.0, 0.0, 0.0]],
                    ['N', [1.46, 0.0, 0.0]],
                    ['C', [-0.74, 1.24, 0.0]],
                    ['O', [-1.96, 1.24, 0.0]],
                    ['O', [0.0, 2.43, 0.0]],
                    ['H', [1.85, -0.89, 0.0]],
                    ['H', [1.85, 0.89, 0.0]],
                    ['H', [-0.37, -1.02, 0.0]],
                    ['H', [-0.37, 0.51, -0.89]],
                    ['H', [0.37, 3.16, 0.0]]
                ],
                description: 'Smallest amino acid - building block of proteins'
            }
        };
    }
}

module.exports = QuantumChemistryService;
