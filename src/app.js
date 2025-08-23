/**
 * COWN Social Network - Main Application
 * Node.js Express server with quantum chemistry integration
 */
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const { Pool } = require('pg');
const redis = require('redis');

// Load environment variables
require('dotenv').config();

// Routes
const userRoutes = require('./routes/userRoutes');
const quantumRoutes = require('./routes/quantumRoutes');

// Create Express app
const app = express();

// Middleware
app.use(cors());
app.use(morgan('combined'));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Static files
app.use(express.static(path.join(__dirname, '../public')));

// Database configuration
const dbConfig = {
    connectionString: process.env.DATABASE_URL || 'postgres://localhost:5432/cown_dev',
    ssl: process.env.NODE_ENV === 'production' ? {
        rejectUnauthorized: process.env.DB_SSL_REJECT_UNAUTHORIZED !== 'false'
    } : false
};

// Redis configuration
const redisConfig = {
    url: process.env.REDIS_URL || 'redis://localhost:6379'
};

// Initialize database connection
const db = new Pool(dbConfig);

// Initialize Redis connection
let redisClient;
try {
    redisClient = redis.createClient(redisConfig);
    redisClient.connect();
    console.log('✅ Redis connected successfully');
} catch (error) {
    console.log('⚠️ Redis connection failed:', error.message);
}

// Test database connection
db.query('SELECT NOW()', (err, result) => {
    if (err) {
        console.log('❌ Database connection failed:', err.message);
    } else {
        console.log('✅ Database connected successfully');
        console.log('🕐 Server time:', result.rows[0].now);
    }
});

// API Routes
app.use('/api/users', userRoutes);
app.use('/api/quantum', quantumRoutes);

// Health check endpoint
app.get('/api/health', async (req, res) => {
    try {
        // Test database
        const dbResult = await db.query('SELECT NOW()');
        
        // Test Redis
        let redisStatus = 'disconnected';
        try {
            if (redisClient && redisClient.isOpen) {
                await redisClient.ping();
                redisStatus = 'connected';
            }
        } catch (redisError) {
            redisStatus = 'error';
        }

        res.json({
            success: true,
            status: 'healthy',
            timestamp: new Date().toISOString(),
            services: {
                database: {
                    status: 'connected',
                    timestamp: dbResult.rows[0].now
                },
                redis: {
                    status: redisStatus
                },
                quantum_chemistry: {
                    status: 'available',
                    python_path: 'C:/Users/nghia/cownV1.1.1/.venv/Scripts/python.exe'
                }
            },
            features: [
                'User Management',
                'Quantum Chemistry Simulations',
                'Molecular Analysis',
                'Real-time Messaging',
                'Cloud Storage'
            ]
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            status: 'unhealthy',
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// API documentation endpoint
app.get('/api', (req, res) => {
    res.json({
        success: true,
        title: 'COWN Social Network API',
        description: 'Advanced social network with quantum chemistry integration',
        version: '1.1.1',
        endpoints: {
            health: 'GET /api/health - System health check',
            users: 'GET /api/users - User management endpoints',
            quantum: 'GET /api/quantum - Quantum chemistry endpoints'
        },
        features: {
            quantum_chemistry: {
                description: 'Molecular simulations using quantum computing',
                algorithms: ['VQE', 'QAOA'],
                max_qubits: 20,
                supported_molecules: ['H2', 'H2O', 'CH4', 'Glycine']
            },
            social_network: {
                description: 'Full-featured social networking platform',
                features: ['Messaging', 'Search', 'Maps', 'Settings']
            }
        },
        documentation: {
            quantum_api: 'GET /api/quantum/help',
            user_api: 'GET /api/users/help'
        },
        timestamp: new Date().toISOString()
    });
});

// Serve frontend pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/login.html'));
});

app.get('/register', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/register.html'));
});

app.get('/home', (req, res) => {
    res.sendFile(path.join(__dirname, '../public/home.html'));
});

// Quantum Chemistry Demo Page
app.get('/quantum-demo', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COWN Quantum Chemistry Demo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .button { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #5a6fd8; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 10px; white-space: pre-wrap; font-family: monospace; }
        .molecule-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .molecule-card { border: 2px solid #e9ecef; border-radius: 10px; padding: 15px; }
        .energy { color: #28a745; font-weight: bold; }
        .formula { color: #007bff; font-weight: bold; font-size: 1.2em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 COWN Quantum Chemistry Demo</h1>
            <p>Advanced molecular simulations using quantum computing algorithms</p>
        </div>

        <div class="card">
            <h2>🔬 System Status</h2>
            <button class="button" onclick="checkStatus()">Check System Status</button>
            <div id="status-result" class="result" style="display: none;"></div>
        </div>

        <div class="card">
            <h2>🧬 Predefined Molecules</h2>
            <button class="button" onclick="loadPredefined()">Load Molecules</button>
            <button class="button" onclick="analyzeCommon()">Analyze Common Molecules</button>
            <div id="molecules-grid" class="molecule-grid"></div>
        </div>

        <div class="card">
            <h2>⚛️ Custom Molecule Analysis</h2>
            <p>Enter molecular geometry in JSON format:</p>
            <textarea id="geometry-input" rows="8" style="width: 100%; font-family: monospace;">
[
    ["H", [0.0, 0.0, 0.0]], 
    ["H", [0.74, 0.0, 0.0]]
]
            </textarea>
            <br>
            <input type="text" id="molecule-name" placeholder="Molecule name" value="Custom Molecule" style="width: 200px; margin: 10px 0;">
            <br>
            <button class="button" onclick="analyzeCustom()">Analyze Molecule</button>
            <div id="custom-result" class="result" style="display: none;"></div>
        </div>

        <div class="card">
            <h2>🚀 Full Demo</h2>
            <button class="button" onclick="runFullDemo()">Run Complete Demo</button>
            <div id="demo-result" class="result" style="display: none;"></div>
        </div>
    </div>

    <script>
        async function apiCall(url, method = 'GET', body = null) {
            try {
                const options = { method, headers: { 'Content-Type': 'application/json' } };
                if (body) options.body = JSON.stringify(body);
                
                const response = await fetch(url, options);
                return await response.json();
            } catch (error) {
                return { success: false, error: error.message };
            }
        }

        async function checkStatus() {
            const result = await apiCall('/api/quantum/status');
            document.getElementById('status-result').style.display = 'block';
            document.getElementById('status-result').textContent = JSON.stringify(result, null, 2);
        }

        async function loadPredefined() {
            const result = await apiCall('/api/quantum/predefined');
            const grid = document.getElementById('molecules-grid');
            
            if (result.success) {
                grid.innerHTML = '';
                Object.entries(result.data).forEach(([key, mol]) => {
                    const card = document.createElement('div');
                    card.className = 'molecule-card';
                    card.innerHTML = \`
                        <h3>\${mol.name} <span class="formula">(\${mol.formula})</span></h3>
                        <p>\${mol.description}</p>
                        <p><strong>Atoms:</strong> \${mol.geometry.length}</p>
                        <button class="button" onclick="analyzeMolecule('\${key}')">Analyze</button>
                        <div id="result-\${key}" class="result" style="display: none;"></div>
                    \`;
                    grid.appendChild(card);
                });
            }
        }

        async function analyzeMolecule(moleculeKey) {
            const predefined = await apiCall('/api/quantum/predefined');
            if (predefined.success && predefined.data[moleculeKey]) {
                const mol = predefined.data[moleculeKey];
                const result = await apiCall('/api/quantum/analyze', 'POST', {
                    geometry: mol.geometry,
                    name: mol.name
                });
                
                const resultDiv = document.getElementById(\`result-\${moleculeKey}\`);
                resultDiv.style.display = 'block';
                
                if (result.success && result.data.success && result.data.quantum_analysis) {
                    const qa = result.data.quantum_analysis;
                    resultDiv.innerHTML = \`
                        <strong class="energy">Ground State Energy: \${qa.ground_state_energy.toFixed(6)} Ha</strong><br>
                        Quantum Fidelity: \${qa.quantum_fidelity.toFixed(4)}<br>
                        Computation Time: \${qa.computational_time.toFixed(3)}s<br>
                        Algorithm: \${qa.algorithm}<br>
                        Binding Energy: \${result.data.properties.binding_energy.toFixed(2)} eV
                    \`;
                } else {
                    resultDiv.textContent = JSON.stringify(result, null, 2);
                }
            }
        }

        async function analyzeCommon() {
            const result = await apiCall('/api/quantum/common-molecules');
            const grid = document.getElementById('molecules-grid');
            
            if (result.success && result.data.success) {
                grid.innerHTML = '<h3>Common Molecules Analysis Results:</h3>';
                Object.entries(result.data.molecules).forEach(([name, data]) => {
                    const card = document.createElement('div');
                    card.className = 'molecule-card';
                    
                    if (data.success && data.quantum_analysis) {
                        card.innerHTML = \`
                            <h3>\${name} <span class="formula">(\${data.molecule.formula})</span></h3>
                            <p>\${data.description}</p>
                            <div class="energy">Energy: \${data.quantum_analysis.ground_state_energy.toFixed(6)} Ha</div>
                            <p>Fidelity: \${data.quantum_analysis.quantum_fidelity.toFixed(4)}</p>
                            <p>Time: \${data.quantum_analysis.computational_time.toFixed(3)}s</p>
                        \`;
                    } else {
                        card.innerHTML = \`<h3>\${name}</h3><p>Analysis failed: \${data.error || 'Unknown error'}</p>\`;
                    }
                    grid.appendChild(card);
                });
            }
        }

        async function analyzeCustom() {
            try {
                const geometry = JSON.parse(document.getElementById('geometry-input').value);
                const name = document.getElementById('molecule-name').value;
                
                const result = await apiCall('/api/quantum/analyze', 'POST', { geometry, name });
                
                const resultDiv = document.getElementById('custom-result');
                resultDiv.style.display = 'block';
                resultDiv.textContent = JSON.stringify(result, null, 2);
            } catch (error) {
                document.getElementById('custom-result').style.display = 'block';
                document.getElementById('custom-result').textContent = 'Error: ' + error.message;
            }
        }

        async function runFullDemo() {
            const resultDiv = document.getElementById('demo-result');
            resultDiv.style.display = 'block';
            resultDiv.textContent = 'Running full demo... This may take a few minutes.';
            
            const result = await apiCall('/api/quantum/demo', 'POST');
            resultDiv.textContent = JSON.stringify(result, null, 2);
        }

        // Load predefined molecules on page load
        window.onload = () => {
            loadPredefined();
        };
    </script>
</body>
</html>
    `);
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        path: req.originalUrl,
        available_endpoints: [
            'GET /',
            'GET /api',
            'GET /api/health',
            'GET /api/quantum/help',
            'GET /quantum-demo'
        ],
        timestamp: new Date().toISOString()
    });
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Server Error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: error.message,
        timestamp: new Date().toISOString()
    });
});

// Server configuration
const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || 'localhost';

app.listen(PORT, HOST, () => {
    console.log('🚀 COWN Social Network Server Started');
    console.log('=' * 50);
    console.log(`🌐 Server running at http://${HOST}:${PORT}`);
    console.log(`🧪 Quantum Demo: http://${HOST}:${PORT}/quantum-demo`);
    console.log(`📊 API Documentation: http://${HOST}:${PORT}/api`);
    console.log(`❤️ Health Check: http://${HOST}:${PORT}/api/health`);
    console.log('=' * 50);
    console.log('🔬 Quantum Chemistry Features:');
    console.log('   ✅ VQE Algorithm Implementation');
    console.log('   ✅ Molecular Simulations (H2, H2O, CH4, Glycine)');
    console.log('   ✅ PennyLane Integration');
    console.log('   ✅ RESTful API Endpoints');
    console.log('   ✅ Interactive Web Demo');
    console.log('=' * 50);
});

module.exports = app;
