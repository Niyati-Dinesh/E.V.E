// context/AuthContext.jsx
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { getMe, logout } from "../api/auth";
import { getProfile, updateProfile, uploadAvatar } from "../api/profile";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = useCallback(async () => {
    try {
      const data = await getProfile();
      setProfile(data);
    } catch (_) {
      setProfile(null);
    }
  }, []);

  useEffect(() => {
    getMe()
      .then((u) => {
        setUser(u);
        return getProfile();
      })
      .then(setProfile)
      .catch(() => {
        setUser(null);
        setProfile(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const signOut = async () => {
    await logout();
    setUser(null);
    setProfile(null);
  };

  // Save text fields — returns updated profile and keeps context in sync
  const saveProfile = useCallback(async (data) => {
    const updated = await updateProfile(data);
    setProfile(updated);
    return updated;
  }, []);

  // Upload avatar — returns the full API response (including pfp_url)
  // so callers (UserProfile.jsx) can update their local preview immediately.
  const saveAvatar = useCallback(async (file) => {
    const result = await uploadAvatar(file);
    // Merge new pfp_url into context profile
    setProfile((prev) => ({ ...prev, pfp_url: result.pfp_url }));
    // Return the full result so the component can resolveUrl itself
    return result;
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        profile,
        setProfile,
        loading,
        signOut,
        fetchProfile,
        saveProfile,
        saveAvatar,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);