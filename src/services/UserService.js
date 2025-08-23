/*
COWN User Service
Business logic layer cho user operations với quantum security integration
*/

const { User } = require('../models/User');
const { QuantumSecurityService } = require('./QuantumSecurityService');

class UserService {
    constructor() {
        this.quantumService = new QuantumSecurityService();
    }

    /**
     * Create new user
     * @param {Object} userData - User data object
     * @returns {Promise<Object>} Created user
     */
    async createUser(userData) {
        try {
            const user = new User(userData);
            const savedUser = await user.save();
            
            console.log(`Created new user: ${savedUser.username} with quantum session: ${savedUser.quantumSessionId}`);
            
            return savedUser.toObject();
        } catch (error) {
            if (error.code === 11000) {
                throw new Error('User with this email or username already exists');
            }
            throw error;
        }
    }

    /**
     * Find user by ID
     * @param {String} userId - User ID
     * @returns {Promise<Object|null>} User object or null
     */
    async findById(userId) {
        try {
            const user = await User.findById(userId);
            return user ? user.toObject() : null;
        } catch (error) {
            throw new Error(`Error finding user by ID: ${error.message}`);
        }
    }

    /**
     * Find user by username
     * @param {String} username - Username
     * @returns {Promise<Object|null>} User object or null
     */
    async findByUsername(username) {
        try {
            const user = await User.findOne({ 
                username: username,
                isActive: true 
            });
            return user ? user.toObject() : null;
        } catch (error) {
            throw new Error(`Error finding user by username: ${error.message}`);
        }
    }

    /**
     * Find user by email
     * @param {String} email - Email address
     * @returns {Promise<Object|null>} User object or null
     */
    async findByEmail(email) {
        try {
            const user = await User.findOne({ 
                email: email.toLowerCase(),
                isActive: true 
            });
            return user ? user.toObject() : null;
        } catch (error) {
            throw new Error(`Error finding user by email: ${error.message}`);
        }
    }

    /**
     * Find user by email or username
     * @param {String} email - Email address
     * @param {String} username - Username
     * @returns {Promise<Object|null>} User object or null
     */
    async findByEmailOrUsername(email, username) {
        try {
            const user = await User.findByEmailOrUsername(email, username);
            return user ? user.toObject() : null;
        } catch (error) {
            throw new Error(`Error finding user by email or username: ${error.message}`);
        }
    }

    /**
     * Update user
     * @param {String} userId - User ID
     * @param {Object} updateData - Data to update
     * @returns {Promise<Object>} Updated user
     */
    async updateUser(userId, updateData) {
        try {
            // Remove fields that shouldn't be updated directly
            const { _id, createdAt, ...safeUpdateData } = updateData;
            
            const user = await User.findByIdAndUpdate(
                userId,
                { 
                    ...safeUpdateData,
                    updatedAt: new Date() 
                },
                { 
                    new: true,
                    runValidators: true 
                }
            );

            if (!user) {
                throw new Error('User not found');
            }

            return user.toObject();
        } catch (error) {
            throw new Error(`Error updating user: ${error.message}`);
        }
    }

    /**
     * Search users
     * @param {String} query - Search query
     * @param {String} excludeUserId - User ID to exclude from results
     * @param {Number} page - Page number
     * @param {Number} limit - Results per page
     * @returns {Promise<Object>} Search results
     */
    async searchUsers(query, excludeUserId, page = 1, limit = 20) {
        try {
            const users = await User.searchUsers(query, excludeUserId, page, limit);
            const total = await User.countDocuments({
                $text: { $search: query },
                _id: { $ne: excludeUserId },
                isActive: true
            });

            return {
                users: users.map(user => user.toPublicProfile()),
                pagination: {
                    currentPage: page,
                    totalPages: Math.ceil(total / limit),
                    totalUsers: total,
                    hasNext: page < Math.ceil(total / limit),
                    hasPrev: page > 1
                }
            };
        } catch (error) {
            throw new Error(`Error searching users: ${error.message}`);
        }
    }

    /**
     * Check if user can view another user's profile
     * @param {String} viewerId - ID of user viewing
     * @param {String} targetUserId - ID of target user
     * @returns {Promise<Boolean>} Can view profile
     */
    async canViewProfile(viewerId, targetUserId) {
        try {
            if (viewerId === targetUserId) {
                return true;
            }

            const targetUser = await User.findById(targetUserId);
            if (!targetUser || !targetUser.isActive) {
                return false;
            }

            // Check privacy settings
            const privacySettings = targetUser.privacySettings || {};
            
            switch (privacySettings.profileVisibility) {
                case 'public':
                    return true;
                
                case 'friends':
                    // Check if viewer is a friend
                    const isFriend = targetUser.friends.some(
                        friend => friend.userId.toString() === viewerId && friend.status === 'accepted'
                    );
                    return isFriend;
                
                case 'private':
                    return false;
                
                default:
                    return true;
            }
        } catch (error) {
            throw new Error(`Error checking profile visibility: ${error.message}`);
        }
    }

    /**
     * Add friend relationship with quantum channel
     * @param {String} userId - User ID sending request
     * @param {String} friendId - User ID receiving request
     * @returns {Promise<Object>} Friend relationship result
     */
    async addFriend(userId, friendId) {
        try {
            if (userId === friendId) {
                throw new Error('Cannot add yourself as friend');
            }

            const [user, friend] = await Promise.all([
                User.findById(userId),
                User.findById(friendId)
            ]);

            if (!user || !friend) {
                throw new Error('User not found');
            }

            // Check if already friends
            const existingFriend = user.friends.find(
                f => f.userId.toString() === friendId
            );
            
            if (existingFriend) {
                throw new Error('Users are already friends');
            }

            // Create quantum communication channel
            const quantumChannel = await this.quantumService.establishQuantumChannel(
                user.username, 
                friend.username
            );

            // Add friend to both users
            await Promise.all([
                user.addFriend(friendId, quantumChannel.session_id),
                friend.addFriend(userId, quantumChannel.session_id)
            ]);

            return {
                success: true,
                quantumChannelId: quantumChannel.session_id,
                securityLevel: quantumChannel.security_level
            };
        } catch (error) {
            throw new Error(`Error adding friend: ${error.message}`);
        }
    }

    /**
     * Remove friend relationship
     * @param {String} userId - User ID
     * @param {String} friendId - Friend ID to remove
     * @returns {Promise<Boolean>} Success status
     */
    async removeFriend(userId, friendId) {
        try {
            const [user, friend] = await Promise.all([
                User.findById(userId),
                User.findById(friendId)
            ]);

            if (!user || !friend) {
                throw new Error('User not found');
            }

            // Get quantum channel ID before removal
            const userFriend = user.friends.find(
                f => f.userId.toString() === friendId
            );

            if (userFriend && userFriend.quantumChannelId) {
                // Cleanup quantum channel
                await this.quantumService.cleanupQuantumChannel(
                    userFriend.quantumChannelId
                );
            }

            // Remove friend from both users
            await Promise.all([
                user.removeFriend(friendId),
                friend.removeFriend(userId)
            ]);

            return true;
        } catch (error) {
            throw new Error(`Error removing friend: ${error.message}`);
        }
    }

    /**
     * Block user
     * @param {String} userId - User ID doing the blocking
     * @param {String} userToBlockId - User ID to block
     * @param {String} reason - Reason for blocking
     * @returns {Promise<Boolean>} Success status
     */
    async blockUser(userId, userToBlockId, reason = '') {
        try {
            const user = await User.findById(userId);
            if (!user) {
                throw new Error('User not found');
            }

            await user.blockUser(userToBlockId, reason);
            
            // Also remove from friend's friend list
            const blockedUser = await User.findById(userToBlockId);
            if (blockedUser) {
                await blockedUser.removeFriend(userId);
            }

            return true;
        } catch (error) {
            throw new Error(`Error blocking user: ${error.message}`);
        }
    }

    /**
     * Get user friends with quantum security status
     * @param {String} userId - User ID
     * @param {Object} options - Pagination and filter options
     * @returns {Promise<Object>} Friends list with quantum status
     */
    async getUserFriends(userId, options = {}) {
        try {
            const { page = 1, limit = 20, status = 'accepted' } = options;
            const skip = (page - 1) * limit;

            const user = await User.findById(userId)
                .populate({
                    path: 'friends.userId',
                    select: 'username fullName avatar isOnline lastSeen',
                    match: { isActive: true }
                });

            if (!user) {
                throw new Error('User not found');
            }

            // Filter friends by status and paginate
            const friends = user.friends
                .filter(f => f.status === status && f.userId)
                .slice(skip, skip + limit);

            // Get quantum security status for each friend
            const friendsWithQuantumStatus = await Promise.all(
                friends.map(async (friend) => {
                    const quantumStatus = friend.quantumChannelId 
                        ? await this.quantumService.getChannelStatus(friend.quantumChannelId)
                        : null;

                    return {
                        user: friend.userId.toPublicProfile(),
                        friendshipDate: friend.addedAt,
                        quantumSecurity: quantumStatus
                    };
                })
            );

            const totalFriends = user.friends.filter(f => f.status === status).length;

            return {
                friends: friendsWithQuantumStatus,
                pagination: {
                    currentPage: page,
                    totalPages: Math.ceil(totalFriends / limit),
                    totalFriends,
                    hasNext: page < Math.ceil(totalFriends / limit),
                    hasPrev: page > 1
                }
            };
        } catch (error) {
            throw new Error(`Error getting user friends: ${error.message}`);
        }
    }

    /**
     * Update user online status
     * @param {String} userId - User ID
     * @param {Boolean} isOnline - Online status
     * @returns {Promise<Boolean>} Success status
     */
    async updateOnlineStatus(userId, isOnline) {
        try {
            const user = await User.findById(userId);
            if (!user) {
                throw new Error('User not found');
            }

            await user.updateOnlineStatus(isOnline);
            return true;
        } catch (error) {
            throw new Error(`Error updating online status: ${error.message}`);
        }
    }

    /**
     * Record user login with quantum verification
     * @param {String} userId - User ID
     * @param {Object} loginData - Login data (IP, user agent, etc.)
     * @returns {Promise<Boolean>} Success status
     */
    async recordLogin(userId, loginData) {
        try {
            const user = await User.findById(userId);
            if (!user) {
                throw new Error('User not found');
            }

            const { ip, userAgent, location } = loginData;
            
            // Verify quantum session if available
            let quantumVerified = false;
            if (user.quantumSessionId) {
                try {
                    const quantumStatus = await this.quantumService.verifyUserSession(
                        user.quantumSessionId
                    );
                    quantumVerified = quantumStatus.isValid;
                } catch (quantumError) {
                    console.warn(`Quantum verification failed for user ${userId}:`, quantumError);
                }
            }

            await user.addLoginRecord(ip, userAgent, location, quantumVerified);
            return true;
        } catch (error) {
            throw new Error(`Error recording login: ${error.message}`);
        }
    }

    /**
     * Get user statistics
     * @param {String} userId - User ID
     * @returns {Promise<Object>} User statistics
     */
    async getUserStats(userId) {
        try {
            const user = await User.findById(userId);
            if (!user) {
                throw new Error('User not found');
            }

            const stats = {
                friends: user.friendsCount,
                joinDate: user.createdAt,
                lastLogin: user.lastLogin,
                isOnline: user.isOnline,
                quantumSecurity: user.quantumSecurityStatus,
                profileViews: 0, // TODO: Implement profile views tracking
                posts: 0, // TODO: Get from Posts service
                messages: 0 // TODO: Get from Messages service
            };

            return stats;
        } catch (error) {
            throw new Error(`Error getting user stats: ${error.message}`);
        }
    }

    /**
     * Cleanup inactive users
     * @param {Number} inactiveDays - Days of inactivity threshold
     * @returns {Promise<Number>} Number of users cleaned up
     */
    async cleanupInactiveUsers(inactiveDays = 365) {
        try {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - inactiveDays);

            const inactiveUsers = await User.find({
                isActive: true,
                lastLogin: { $lt: cutoffDate }
            });

            let cleanedUp = 0;

            for (const user of inactiveUsers) {
                // Cleanup quantum sessions
                if (user.quantumSessionId) {
                    try {
                        await this.quantumService.cleanupUserSession(user.quantumSessionId);
                    } catch (error) {
                        console.warn(`Failed to cleanup quantum session for user ${user.id}:`, error);
                    }
                }

                // Deactivate user
                await User.findByIdAndUpdate(user._id, {
                    isActive: false,
                    deactivatedAt: new Date(),
                    deactivationReason: 'Automatic cleanup due to inactivity'
                });

                cleanedUp++;
            }

            return cleanedUp;
        } catch (error) {
            throw new Error(`Error during cleanup: ${error.message}`);
        }
    }
}

module.exports = { UserService };
