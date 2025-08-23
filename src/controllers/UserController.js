/*
COWN Backend Controllers
User Controller - Xử lý tất cả user-related operations
*/

const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { User } = require('../models/User');
const { validationResult } = require('express-validator');
const { UserService } = require('../services/UserService');
const { AuthService } = require('../services/AuthService');
const { QuantumSecurityService } = require('../services/QuantumSecurityService');

class UserController {
    constructor() {
        this.userService = new UserService();
        this.authService = new AuthService();
        this.quantumService = new QuantumSecurityService();
    }

    /**
     * Register new user với quantum security
     * POST /api/users/register
     */
    async register(req, res) {
        try {
            // Validate input
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    success: false,
                    message: 'Validation errors',
                    errors: errors.array()
                });
            }

            const { username, email, password, fullName, phone } = req.body;

            // Check if user exists
            const existingUser = await this.userService.findByEmailOrUsername(email, username);
            if (existingUser) {
                return res.status(409).json({
                    success: false,
                    message: 'User already exists with this email or username'
                });
            }

            // Hash password
            const saltRounds = 12;
            const hashedPassword = await bcrypt.hash(password, saltRounds);

            // Create quantum security session
            const quantumSession = await this.quantumService.createUserQuantumSession(username);

            // Create user
            const userData = {
                username,
                email,
                password: hashedPassword,
                fullName,
                phone,
                quantumSessionId: quantumSession.session_id,
                isActive: true,
                createdAt: new Date(),
                lastLogin: null
            };

            const newUser = await this.userService.createUser(userData);

            // Generate JWT token with quantum signature
            const tokenData = {
                userId: newUser.id,
                username: newUser.username,
                quantumSessionId: quantumSession.session_id
            };

            const token = await this.authService.generateQuantumSecureToken(tokenData);

            // Return user data (without password)
            const { password: _, ...userResponse } = newUser;

            res.status(201).json({
                success: true,
                message: 'User registered successfully',
                data: {
                    user: userResponse,
                    token,
                    quantumSecurity: {
                        sessionId: quantumSession.session_id,
                        securityLevel: quantumSession.security_level
                    }
                }
            });

        } catch (error) {
            console.error('User registration error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error during registration'
            });
        }
    }

    /**
     * User login với quantum authentication
     * POST /api/users/login
     */
    async login(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    success: false,
                    message: 'Validation errors',
                    errors: errors.array()
                });
            }

            const { emailOrUsername, password } = req.body;

            // Find user
            const user = await this.userService.findByEmailOrUsername(emailOrUsername, emailOrUsername);
            if (!user) {
                return res.status(401).json({
                    success: false,
                    message: 'Invalid credentials'
                });
            }

            // Check password
            const isPasswordValid = await bcrypt.compare(password, user.password);
            if (!isPasswordValid) {
                return res.status(401).json({
                    success: false,
                    message: 'Invalid credentials'
                });
            }

            // Check if user is active
            if (!user.isActive) {
                return res.status(403).json({
                    success: false,
                    message: 'Account is deactivated'
                });
            }

            // Validate quantum session
            let quantumSession = await this.quantumService.getQuantumSession(user.quantumSessionId);
            if (!quantumSession || quantumSession.isExpired()) {
                // Create new quantum session
                quantumSession = await this.quantumService.createUserQuantumSession(user.username);
                await this.userService.updateUser(user.id, { 
                    quantumSessionId: quantumSession.session_id 
                });
            }

            // Generate quantum-secure token
            const tokenData = {
                userId: user.id,
                username: user.username,
                quantumSessionId: quantumSession.session_id
            };

            const token = await this.authService.generateQuantumSecureToken(tokenData);

            // Update last login
            await this.userService.updateUser(user.id, { 
                lastLogin: new Date() 
            });

            // Return user data
            const { password: _, ...userResponse } = user;

            res.json({
                success: true,
                message: 'Login successful',
                data: {
                    user: userResponse,
                    token,
                    quantumSecurity: {
                        sessionId: quantumSession.session_id,
                        securityLevel: quantumSession.security_level,
                        expiresAt: quantumSession.expires_at
                    }
                }
            });

        } catch (error) {
            console.error('User login error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error during login'
            });
        }
    }

    /**
     * Get user profile
     * GET /api/users/profile
     */
    async getProfile(req, res) {
        try {
            const userId = req.user.userId;

            const user = await this.userService.findById(userId);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            // Get quantum security status
            const quantumStatus = await this.quantumService.getSecurityStatus(user.username);

            const { password: _, ...userResponse } = user;

            res.json({
                success: true,
                data: {
                    user: userResponse,
                    quantumSecurity: quantumStatus
                }
            });

        } catch (error) {
            console.error('Get profile error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Update user profile
     * PUT /api/users/profile
     */
    async updateProfile(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    success: false,
                    message: 'Validation errors',
                    errors: errors.array()
                });
            }

            const userId = req.user.userId;
            const { fullName, phone, bio, avatar, location } = req.body;

            // Update user data
            const updateData = {
                fullName,
                phone,
                bio,
                avatar,
                location,
                updatedAt: new Date()
            };

            // Remove undefined fields
            Object.keys(updateData).forEach(key => 
                updateData[key] === undefined && delete updateData[key]
            );

            const updatedUser = await this.userService.updateUser(userId, updateData);

            const { password: _, ...userResponse } = updatedUser;

            res.json({
                success: true,
                message: 'Profile updated successfully',
                data: {
                    user: userResponse
                }
            });

        } catch (error) {
            console.error('Update profile error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Change password với quantum verification
     * PUT /api/users/change-password
     */
    async changePassword(req, res) {
        try {
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({
                    success: false,
                    message: 'Validation errors',
                    errors: errors.array()
                });
            }

            const userId = req.user.userId;
            const { currentPassword, newPassword } = req.body;

            // Get user
            const user = await this.userService.findById(userId);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            // Verify current password
            const isCurrentPasswordValid = await bcrypt.compare(currentPassword, user.password);
            if (!isCurrentPasswordValid) {
                return res.status(401).json({
                    success: false,
                    message: 'Current password is incorrect'
                });
            }

            // Hash new password
            const saltRounds = 12;
            const hashedNewPassword = await bcrypt.hash(newPassword, saltRounds);

            // Create quantum signature for password change
            const changeEvent = {
                userId: user.id,
                action: 'password_change',
                timestamp: new Date(),
                metadata: {
                    ip: req.ip,
                    userAgent: req.get('User-Agent')
                }
            };

            const quantumSignature = await this.quantumService.signEvent(
                JSON.stringify(changeEvent), 
                user.username
            );

            // Update password
            await this.userService.updateUser(userId, {
                password: hashedNewPassword,
                passwordChangedAt: new Date(),
                quantumSignatures: user.quantumSignatures 
                    ? [...user.quantumSignatures, quantumSignature.signature_id]
                    : [quantumSignature.signature_id]
            });

            res.json({
                success: true,
                message: 'Password changed successfully',
                data: {
                    quantumVerification: {
                        signatureId: quantumSignature.signature_id,
                        securityLevel: quantumSignature.security_level
                    }
                }
            });

        } catch (error) {
            console.error('Change password error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Search users
     * GET /api/users/search
     */
    async searchUsers(req, res) {
        try {
            const { q, page = 1, limit = 20 } = req.query;
            const currentUserId = req.user.userId;

            if (!q || q.trim().length < 2) {
                return res.status(400).json({
                    success: false,
                    message: 'Search query must be at least 2 characters'
                });
            }

            const searchResults = await this.userService.searchUsers(
                q.trim(), 
                currentUserId, 
                parseInt(page), 
                parseInt(limit)
            );

            res.json({
                success: true,
                data: searchResults
            });

        } catch (error) {
            console.error('Search users error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Get user by username
     * GET /api/users/:username
     */
    async getUserByUsername(req, res) {
        try {
            const { username } = req.params;
            const currentUserId = req.user.userId;

            const user = await this.userService.findByUsername(username);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            // Check privacy settings
            const canViewProfile = await this.userService.canViewProfile(currentUserId, user.id);
            if (!canViewProfile) {
                return res.status(403).json({
                    success: false,
                    message: 'Profile is private'
                });
            }

            // Return limited profile data
            const profileData = {
                id: user.id,
                username: user.username,
                fullName: user.fullName,
                bio: user.bio,
                avatar: user.avatar,
                location: user.location,
                createdAt: user.createdAt,
                isOnline: user.isOnline,
                lastSeen: user.lastSeen
            };

            res.json({
                success: true,
                data: {
                    user: profileData
                }
            });

        } catch (error) {
            console.error('Get user by username error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Deactivate account
     * DELETE /api/users/account
     */
    async deactivateAccount(req, res) {
        try {
            const userId = req.user.userId;
            const { password } = req.body;

            // Verify password
            const user = await this.userService.findById(userId);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            const isPasswordValid = await bcrypt.compare(password, user.password);
            if (!isPasswordValid) {
                return res.status(401).json({
                    success: false,
                    message: 'Password is incorrect'
                });
            }

            // Create quantum signature for account deactivation
            const deactivationEvent = {
                userId: user.id,
                action: 'account_deactivation',
                timestamp: new Date(),
                metadata: {
                    ip: req.ip,
                    userAgent: req.get('User-Agent')
                }
            };

            const quantumSignature = await this.quantumService.signEvent(
                JSON.stringify(deactivationEvent), 
                user.username
            );

            // Deactivate account
            await this.userService.updateUser(userId, {
                isActive: false,
                deactivatedAt: new Date(),
                deactivationSignature: quantumSignature.signature_id
            });

            // Cleanup quantum session
            await this.quantumService.cleanupUserSession(user.quantumSessionId);

            res.json({
                success: true,
                message: 'Account deactivated successfully',
                data: {
                    quantumVerification: {
                        signatureId: quantumSignature.signature_id
                    }
                }
            });

        } catch (error) {
            console.error('Deactivate account error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }

    /**
     * Get quantum security dashboard
     * GET /api/users/quantum-security
     */
    async getQuantumSecurity(req, res) {
        try {
            const userId = req.user.userId;

            const user = await this.userService.findById(userId);
            if (!user) {
                return res.status(404).json({
                    success: false,
                    message: 'User not found'
                });
            }

            // Get comprehensive quantum security status
            const quantumStatus = await this.quantumService.getSecurityStatus(user.username);
            const threats = await this.quantumService.detectThreats(user.quantumSessionId);
            const metrics = await this.quantumService.getPerformanceMetrics(user.username);

            res.json({
                success: true,
                data: {
                    securityStatus: quantumStatus,
                    threatDetection: threats,
                    performanceMetrics: metrics,
                    recommendations: await this.quantumService.getSecurityRecommendations(user.username)
                }
            });

        } catch (error) {
            console.error('Get quantum security error:', error);
            res.status(500).json({
                success: false,
                message: 'Internal server error'
            });
        }
    }
}

module.exports = { UserController };
