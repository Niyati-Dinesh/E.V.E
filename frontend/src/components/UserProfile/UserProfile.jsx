// components/UserProfile/UserProfile.jsx
import React, { useState, useRef, useEffect } from "react";
import {
  X, Camera, AtSign, FileText,
  Save, Check, Loader2, Mail,
} from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import "./userprofile.css";

// Prefix relative avatar URLs with the backend base so they load from
// FastAPI (port 8000) rather than the Vite dev server (port 5173).
const BACKEND = "http://localhost:8000";
function resolveUrl(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  return `${BACKEND}${url}`;
}

export default function UserProfile({ onClose }) {
  const { profile, saveProfile, saveAvatar } = useAuth();

  const [form, setForm] = useState({
    full_name: profile?.full_name || "",
    bio:       profile?.bio       || "",
  });

  const [saving,        setSaving]        = useState(false);
  const [saved,         setSaved]         = useState(false);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [previewUrl,    setPreviewUrl]    = useState(resolveUrl(profile?.pfp_url));
  const [error,         setError]         = useState("");
  const fileRef = useRef(null);

  // Sync form + avatar if profile loads late (AuthContext fetch completes)
  useEffect(() => {
    if (profile) {
      setForm({
        full_name: profile.full_name || "",
        bio:       profile.bio       || "",
      });
      setPreviewUrl(resolveUrl(profile.pfp_url));
    }
  }, [profile]);

  // Restore focus when modal closes
  useEffect(() => {
    const prev = document.activeElement;
    return () => prev?.focus();
  }, []);

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) return setError("Please select an image file.");
    if (file.size > 2 * 1024 * 1024) return setError("Image must be under 2 MB.");
    setError("");

    // Show local preview immediately while upload is in-flight
    const reader = new FileReader();
    reader.onload = (ev) => setPreviewUrl(ev.target.result);
    reader.readAsDataURL(file);

    setAvatarLoading(true);
    try {
      const result = await saveAvatar(file);
      // Once backend responds, switch preview to the persisted URL
      if (result?.pfp_url) setPreviewUrl(resolveUrl(result.pfp_url));
    } catch (err) {
      setError(err.message || "Avatar upload failed");
    } finally {
      setAvatarLoading(false);
      // Clear input so same file can be re-selected if needed
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await saveProfile(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setError(err.message || "Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  const initials = form.full_name
    ? form.full_name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : (profile?.email?.[0] || "U").toUpperCase();

  return (
    <div className="profile-overlay" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="profile-modal" role="dialog" aria-modal="true" aria-label="Edit profile">

        {/* ── Header ─────────────────────────────────────────────────────── */}
        <div className="profile-header">
          <span className="profile-header-label">Profile</span>
          <button className="profile-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* ── Avatar ─────────────────────────────────────────────────────── */}
        <div className="profile-avatar-section">
          <div className="profile-avatar-wrap">
            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Profile"
                className="profile-avatar-img"
                onError={() => setPreviewUrl(null)}
              />
            ) : (
              <div className="profile-avatar-initials">{initials}</div>
            )}
            {avatarLoading && (
              <div className="profile-avatar-overlay">
                <Loader2 size={20} className="spin" />
              </div>
            )}
            <button
              className="profile-avatar-btn"
              onClick={() => fileRef.current?.click()}
              title="Change photo"
              type="button"
            >
              <Camera size={14} />
            </button>
          </div>
          <input
            ref={fileRef}
            type="file"
            accept="image/*"
            style={{ display: "none" }}
            onChange={handleAvatarChange}
          />
          <div className="profile-avatar-meta">
            <div className="profile-display-name">
              {form.full_name || "Your Username"}
            </div>
            <div className="profile-email-pill">
              <Mail size={11} />
              {profile?.email}
            </div>
          </div>
        </div>

        {/* ── Divider ────────────────────────────────────────────────────── */}
        <div className="profile-divider" />

        {/* ── Form ───────────────────────────────────────────────────────── */}
        <form className="profile-form" onSubmit={handleSave}>

          <div className="profile-field">
            <label className="profile-label">Username</label>
            <div className="profile-input-wrap">
              <AtSign size={15} />
              <input
                name="full_name"
                value={form.full_name}
                onChange={handleChange}
                placeholder="Your username"
                maxLength={100}
                autoComplete="username"
              />
            </div>
          </div>

          <div className="profile-field">
            <label className="profile-label">Bio</label>
            <div className="profile-input-wrap profile-textarea-wrap">
              <FileText size={15} style={{ marginTop: "3px", flexShrink: 0 }} />
              <textarea
                name="bio"
                value={form.bio}
                onChange={handleChange}
                placeholder="A short bio about yourself"
                maxLength={300}
                rows={3}
              />
            </div>
            <span className="profile-char-count">{form.bio.length}/300</span>
          </div>

          {error && <p className="profile-error">{error}</p>}

          <button
            type="submit"
            className={`profile-save-btn ${saved ? "saved" : ""}`}
            disabled={saving}
          >
            {saving ? (
              <><Loader2 size={15} className="spin" /> Saving…</>
            ) : saved ? (
              <><Check size={15} /> Saved</>
            ) : (
              <><Save size={15} /> Save Changes</>
            )}
          </button>
        </form>

      </div>
    </div>
  );
}