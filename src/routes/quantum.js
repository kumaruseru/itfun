/*
COWN Quantum Routes
API routes cho hệ thống lượng tử
*/

const express = require('express');
const router = express.Router();
const quantumController = require('../controllers/quantumController');
const { verifyToken } = require('../middleware/auth');

// Health check endpoint (không cần auth)
router.get('/health', quantumController.healthCheck);

// QKD session management (cần auth)
router.post('/qkd/session', verifyToken, quantumController.startQKDSession);
router.delete('/qkd/session/:session_id', verifyToken, quantumController.terminateSession);
router.get('/qkd/statistics', verifyToken, quantumController.getQKDStatistics);

// Quantum encryption endpoints (cần auth)
router.post('/encryption/encrypt', verifyToken, quantumController.encryptMessage);
router.post('/encryption/decrypt', verifyToken, quantumController.decryptMessage);
router.get('/encryption/statistics', verifyToken, quantumController.getEncryptionStatistics);

// Security analysis (cần auth)
router.get('/security/analyze', verifyToken, quantumController.analyzeSecuritys);

// Middleware để log quantum operations
router.use((req, res, next) => {
    console.log(`[QUANTUM] ${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

module.exports = router;
