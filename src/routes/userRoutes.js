/**
 * COWN User Routes
 * RESTful API endpoints for user management
 */
const express = require('express');
const UserController = require('../controllers/UserController');

const router = express.Router();
const userController = new UserController();

// Bind methods to maintain 'this' context
const bindMethods = (controller) => {
    Object.getOwnPropertyNames(Object.getPrototypeOf(controller))
        .filter(name => name !== 'constructor' && typeof controller[name] === 'function')
        .forEach(method => {
            controller[method] = controller[method].bind(controller);
        });
};

bindMethods(userController);

/**
 * @route POST /api/users/register
 * @desc Register a new user
 * @access Public
 */
router.post('/register', userController.register);

/**
 * @route POST /api/users/login
 * @desc Login user
 * @access Public
 */
router.post('/login', userController.login);

/**
 * @route GET /api/users/profile/:id
 * @desc Get user profile
 * @access Private
 */
router.get('/profile/:id', userController.getProfile);

/**
 * @route PUT /api/users/profile/:id
 * @desc Update user profile
 * @access Private
 */
router.put('/profile/:id', userController.updateProfile);

/**
 * @route POST /api/users/logout
 * @desc Logout user
 * @access Private
 */
router.post('/logout', userController.logout);

/**
 * @route GET /api/users/help
 * @desc Get API documentation
 * @access Public
 */
router.get('/help', (req, res) => {
    res.json({
        success: true,
        title: 'COWN User Management API',
        description: 'User authentication and profile management with quantum security',
        endpoints: {
            'POST /api/users/register': 'Register new user account',
            'POST /api/users/login': 'Login with quantum authentication',
            'GET /api/users/profile/:id': 'Get user profile information',
            'PUT /api/users/profile/:id': 'Update user profile',
            'POST /api/users/logout': 'Logout and clear quantum session'
        },
        features: [
            'Quantum-secured authentication',
            'Encrypted user sessions',
            'Profile management',
            'Cloud storage integration'
        ],
        timestamp: new Date().toISOString()
    });
});

module.exports = router;
