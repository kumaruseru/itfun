/*
COWN User Model - MongoDB Schema cho User collection
Sử dụng Mongoose để define user schema với quantum security fields
*/

const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const UserSchema = new Schema({
    // Basic user information
    username: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        minlength: 3,
        maxlength: 30,
        match: /^[a-zA-Z0-9_]+$/,
        index: true
    },
    
    email: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        lowercase: true,
        match: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        index: true
    },
    
    password: {
        type: String,
        required: true,
        minlength: 6
    },
    
    fullName: {
        type: String,
        required: true,
        trim: true,
        maxlength: 100
    },
    
    phone: {
        type: String,
        trim: true,
        match: /^[\+]?[1-9][\d]{0,15}$/
    },
    
    // Profile information
    bio: {
        type: String,
        maxlength: 500,
        default: ''
    },
    
    avatar: {
        type: String,
        default: null
    },
    
    coverPhoto: {
        type: String,
        default: null
    },
    
    location: {
        type: String,
        maxlength: 100,
        default: ''
    },
    
    dateOfBirth: {
        type: Date,
        default: null
    },
    
    gender: {
        type: String,
        enum: ['male', 'female', 'other', 'prefer_not_to_say'],
        default: 'prefer_not_to_say'
    },
    
    // Account status
    isActive: {
        type: Boolean,
        default: true,
        index: true
    },
    
    isVerified: {
        type: Boolean,
        default: false
    },
    
    verificationCode: {
        type: String,
        default: null
    },
    
    verificationCodeExpires: {
        type: Date,
        default: null
    },
    
    // Security and authentication
    passwordResetToken: {
        type: String,
        default: null
    },
    
    passwordResetExpires: {
        type: Date,
        default: null
    },
    
    passwordChangedAt: {
        type: Date,
        default: null
    },
    
    twoFactorSecret: {
        type: String,
        default: null
    },
    
    twoFactorEnabled: {
        type: Boolean,
        default: false
    },
    
    // Quantum Security Fields
    quantumSessionId: {
        type: String,
        default: null,
        index: true
    },
    
    quantumKeys: [{
        keyId: String,
        keyType: {
            type: String,
            enum: ['encryption', 'signature', 'authentication']
        },
        createdAt: {
            type: Date,
            default: Date.now
        },
        expiresAt: Date,
        isActive: {
            type: Boolean,
            default: true
        }
    }],
    
    quantumSignatures: [{
        signatureId: String,
        eventType: String,
        createdAt: {
            type: Date,
            default: Date.now
        },
        verificationStatus: {
            type: String,
            enum: ['verified', 'pending', 'failed'],
            default: 'pending'
        }
    }],
    
    quantumSecurityLevel: {
        type: Number,
        min: 0,
        max: 1,
        default: 0.8
    },
    
    // Privacy settings
    privacySettings: {
        profileVisibility: {
            type: String,
            enum: ['public', 'friends', 'private'],
            default: 'public'
        },
        showEmail: {
            type: Boolean,
            default: false
        },
        showPhone: {
            type: Boolean,
            default: false
        },
        allowFriendRequests: {
            type: Boolean,
            default: true
        },
        allowMessages: {
            type: String,
            enum: ['everyone', 'friends', 'none'],
            default: 'friends'
        },
        showOnlineStatus: {
            type: Boolean,
            default: true
        },
        quantumEncryptedMessages: {
            type: Boolean,
            default: true
        }
    },
    
    // Social features
    friends: [{
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'User'
        },
        status: {
            type: String,
            enum: ['accepted', 'pending', 'blocked'],
            default: 'accepted'
        },
        addedAt: {
            type: Date,
            default: Date.now
        },
        quantumChannelId: String  // For quantum-secured friend communications
    }],
    
    friendRequests: [{
        from: {
            type: Schema.Types.ObjectId,
            ref: 'User'
        },
        to: {
            type: Schema.Types.ObjectId,
            ref: 'User'
        },
        message: String,
        sentAt: {
            type: Date,
            default: Date.now
        },
        status: {
            type: String,
            enum: ['pending', 'accepted', 'declined'],
            default: 'pending'
        }
    }],
    
    blockedUsers: [{
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'User'
        },
        blockedAt: {
            type: Date,
            default: Date.now
        },
        reason: String
    }],
    
    // Activity tracking
    lastLogin: {
        type: Date,
        default: null
    },
    
    lastSeen: {
        type: Date,
        default: null
    },
    
    isOnline: {
        type: Boolean,
        default: false,
        index: true
    },
    
    loginHistory: [{
        ip: String,
        userAgent: String,
        location: String,
        loginAt: {
            type: Date,
            default: Date.now
        },
        quantumVerified: {
            type: Boolean,
            default: false
        }
    }],
    
    // Notifications
    notificationSettings: {
        email: {
            type: Boolean,
            default: true
        },
        push: {
            type: Boolean,
            default: true
        },
        sms: {
            type: Boolean,
            default: false
        },
        friendRequests: {
            type: Boolean,
            default: true
        },
        messages: {
            type: Boolean,
            default: true
        },
        posts: {
            type: Boolean,
            default: true
        },
        quantumAlerts: {
            type: Boolean,
            default: true
        }
    },
    
    // Deactivation
    deactivatedAt: {
        type: Date,
        default: null
    },
    
    deactivationReason: String,
    
    deactivationSignature: String,  // Quantum signature for deactivation
    
    // Timestamps
    createdAt: {
        type: Date,
        default: Date.now,
        index: true
    },
    
    updatedAt: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps: true,
    collection: 'users'
});

// Indexes for performance
UserSchema.index({ username: 1 });
UserSchema.index({ email: 1 });
UserSchema.index({ isActive: 1, isOnline: 1 });
UserSchema.index({ quantumSessionId: 1 });
UserSchema.index({ createdAt: -1 });
UserSchema.index({ lastLogin: -1 });

// Text search index
UserSchema.index({ 
    username: 'text', 
    fullName: 'text', 
    bio: 'text' 
}, {
    weights: {
        username: 10,
        fullName: 5,
        bio: 1
    },
    name: 'user_search_index'
});

// Compound indexes
UserSchema.index({ isActive: 1, isVerified: 1 });
UserSchema.index({ 'friends.userId': 1, 'friends.status': 1 });

// Virtual fields
UserSchema.virtual('friendsCount').get(function() {
    return this.friends ? this.friends.filter(f => f.status === 'accepted').length : 0;
});

UserSchema.virtual('isDeactivated').get(function() {
    return this.deactivatedAt !== null;
});

UserSchema.virtual('quantumSecurityStatus').get(function() {
    const now = new Date();
    const activeKeys = this.quantumKeys ? this.quantumKeys.filter(k => 
        k.isActive && (!k.expiresAt || k.expiresAt > now)
    ).length : 0;
    
    return {
        sessionActive: !!this.quantumSessionId,
        activeKeys,
        securityLevel: this.quantumSecurityLevel,
        signaturesCount: this.quantumSignatures ? this.quantumSignatures.length : 0
    };
});

// Instance methods
UserSchema.methods.toJSON = function() {
    const user = this.toObject();
    
    // Remove sensitive fields
    delete user.password;
    delete user.passwordResetToken;
    delete user.verificationCode;
    delete user.twoFactorSecret;
    delete user.quantumKeys;  // Don't expose quantum keys in JSON
    delete user.__v;
    
    return user;
};

UserSchema.methods.toPublicProfile = function() {
    return {
        id: this._id,
        username: this.username,
        fullName: this.fullName,
        bio: this.bio,
        avatar: this.avatar,
        location: this.location,
        isOnline: this.isOnline,
        lastSeen: this.lastSeen,
        createdAt: this.createdAt,
        friendsCount: this.friendsCount
    };
};

UserSchema.methods.addFriend = function(friendId, quantumChannelId = null) {
    if (this.friends.some(f => f.userId.toString() === friendId.toString())) {
        throw new Error('User is already a friend');
    }
    
    this.friends.push({
        userId: friendId,
        status: 'accepted',
        addedAt: new Date(),
        quantumChannelId
    });
    
    return this.save();
};

UserSchema.methods.removeFriend = function(friendId) {
    this.friends = this.friends.filter(f => 
        f.userId.toString() !== friendId.toString()
    );
    
    return this.save();
};

UserSchema.methods.blockUser = function(userIdToBlock, reason = '') {
    // Remove from friends if exists
    this.removeFriend(userIdToBlock);
    
    // Add to blocked list
    if (!this.blockedUsers.some(b => b.userId.toString() === userIdToBlock.toString())) {
        this.blockedUsers.push({
            userId: userIdToBlock,
            blockedAt: new Date(),
            reason
        });
    }
    
    return this.save();
};

UserSchema.methods.unblockUser = function(userIdToUnblock) {
    this.blockedUsers = this.blockedUsers.filter(b => 
        b.userId.toString() !== userIdToUnblock.toString()
    );
    
    return this.save();
};

UserSchema.methods.addQuantumKey = function(keyId, keyType, expiresAt) {
    this.quantumKeys.push({
        keyId,
        keyType,
        createdAt: new Date(),
        expiresAt,
        isActive: true
    });
    
    return this.save();
};

UserSchema.methods.addQuantumSignature = function(signatureId, eventType) {
    this.quantumSignatures.push({
        signatureId,
        eventType,
        createdAt: new Date(),
        verificationStatus: 'pending'
    });
    
    return this.save();
};

UserSchema.methods.updateOnlineStatus = function(isOnline) {
    this.isOnline = isOnline;
    this.lastSeen = new Date();
    
    return this.save();
};

UserSchema.methods.addLoginRecord = function(ip, userAgent, location, quantumVerified = false) {
    this.loginHistory.push({
        ip,
        userAgent,
        location,
        loginAt: new Date(),
        quantumVerified
    });
    
    // Keep only last 50 login records
    if (this.loginHistory.length > 50) {
        this.loginHistory = this.loginHistory.slice(-50);
    }
    
    this.lastLogin = new Date();
    
    return this.save();
};

// Static methods
UserSchema.statics.findByEmailOrUsername = function(email, username) {
    return this.findOne({
        $or: [
            { email: email.toLowerCase() },
            { username: username }
        ],
        isActive: true
    });
};

UserSchema.statics.searchUsers = function(query, excludeUserId, page = 1, limit = 20) {
    const skip = (page - 1) * limit;
    
    return this.find({
        $text: { $search: query },
        _id: { $ne: excludeUserId },
        isActive: true
    })
    .select('username fullName bio avatar isOnline lastSeen')
    .sort({ score: { $meta: 'textScore' } })
    .skip(skip)
    .limit(limit);
};

UserSchema.statics.findActiveUsers = function(lastActiveHours = 24) {
    const cutoffTime = new Date(Date.now() - (lastActiveHours * 60 * 60 * 1000));
    
    return this.find({
        isActive: true,
        $or: [
            { isOnline: true },
            { lastSeen: { $gte: cutoffTime } }
        ]
    });
};

UserSchema.statics.findUsersWithQuantumSecurity = function() {
    return this.find({
        isActive: true,
        quantumSessionId: { $ne: null }
    });
};

// Pre-save middleware
UserSchema.pre('save', function(next) {
    this.updatedAt = new Date();
    next();
});

// Post-save middleware
UserSchema.post('save', function(doc) {
    console.log(`User ${doc.username} saved successfully`);
});

// Create model
const User = mongoose.model('User', UserSchema);

module.exports = { User, UserSchema };
