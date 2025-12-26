import { createContext, useContext, useState, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Load user from local storage
        try {
            const storedUser = localStorage.getItem('artha_user');
            if (storedUser) {
                setUser(JSON.parse(storedUser));
            }
        } catch (error) {
            console.error("Failed to parse user from storage", error);
            localStorage.removeItem('artha_user');
        }
        setLoading(false);
    }, []);

    // Helper to map Backend User -> Frontend User Shape
    const mapUser = (backendUser, token) => {
        return {
            ...backendUser,
            id: backendUser.phone, // Use phone as ID for now
            name: `${backendUser.firstName} ${backendUser.lastName}`,
            email: backendUser.email || '', // Backend might not send email
            avatar: `https://ui-avatars.com/api/?name=${backendUser.firstName}+${backendUser.lastName}&background=0A2540&color=fff`,
            // Map boolean to string status
            kycStatus: backendUser.kycVerified ? 'verified' : 'incomplete',
            activeRole: 'none',
            bankDetailsAdded: false, // Default
            totalLended: 0,
            totalBorrowed: 0,
            token: token // Important: Store token for API interceptor
        };
    };

    const login = async (phone, password) => {
        try {
            const data = await authService.login(phone, password);
            const mappedUser = mapUser(data.user, data.token);
            setUser(mappedUser);
            localStorage.setItem('artha_user', JSON.stringify(mappedUser));
            return mappedUser;
        } catch (error) {
            console.error("Login failed", error);
            throw error; // Propagate to UI
        }
    };

    const register = async (userData) => {
        // Step 1: Send OTP
        return await authService.register(userData);
    };

    const verifyOtp = async (phone, otp) => {
        // Step 2: Receive Token, but backend verify-otp only returns { token }
        // We probably need to fetch the user profile immediately after or construct it?
        // Wait, the backend verify-otp returns { token }. It does NOT return the user object.
        // We should hit a /profile endpoint or similar. 
        // OR: authService.login returns the user. 
        // Let's assume we can Decode the token OR we need to call login (or get-profile).
        // For now, let's try to just get the token, save it, and maybe "fake" the user object or fetch it.
        // Actually, looking at backend auth_routes.py:
        // verify_otp -> verify_registration_otp -> create_session -> returns token string.
        // It does NOT return user details.
        // We need a way to get user details. 
        // We can call /auth/me or just /auth/login with the password if we had it? No.
        // Backend main.py shows `app.include_router(auth_router)`.
        // There is usually a `/me` endpoint? 
        // Checked: `auth_dependency.py` gets user. `auth_routes.py` has login.
        // There is no `/me` in `auth_routes.py`.
        // BAD INTEGRATION: After OTP verify, we have a token but no User data.
        // FIX: We will just set the token and maybe minimal data, then require a refresh or implement /me?
        // workaround: verifyOtp returns token. We can store token. 
        // But the frontend relies on `user` object.
        // I'll implement a `fetchProfile` method or similar later.
        // For now, I'll return the token and let the UI handle redirection to Login (user has to login again)
        // OR I can use the existing data to hydrate the user state temporarily.

        const data = await authService.verifyOtp(phone, otp);
        return data; // { token }
        // The UI should probably auto-login? Or ask to login using password?
        // Let's ask user to Login after registration for safety/simplicity, as backend doesn't return User on verify.
    };

    const logout = () => {
        // specific logout logic
        try {
            if (user?.token) authService.logout(user.token);
        } catch (e) { /* ignore */ }
        setUser(null);
        localStorage.removeItem('artha_user');
    };

    // Helper to update KYC status locally
    const updateKycStatus = (status) => {
        if (user) {
            const updatedUser = { ...user, kycStatus: status };
            setUser(updatedUser);
            localStorage.setItem('artha_user', JSON.stringify(updatedUser));
        }
    }

    const setUserRole = (role) => {
        if (user) {
            const updatedUser = { ...user, activeRole: role };
            setUser(updatedUser);
            localStorage.setItem('artha_user', JSON.stringify(updatedUser));
        }
    }

    const value = {
        user,
        loading,
        login,
        register,
        verifyOtp,
        logout,
        updateKycStatus,
        setUserRole
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
