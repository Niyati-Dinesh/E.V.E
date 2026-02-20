// components/Navbar/Navbar.jsx
import "./navbar.css";
import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { TextAlignJustify, X, User, LogOut, Settings } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { logout } from "../../api/auth";
import UserProfile from "../UserProfile/UserProfile";

export default function Navbar() {
  const [menuOpen,       setMenuOpen]       = useState(false);
  const [userMenuOpen,   setUserMenuOpen]   = useState(false);
  const [profileOpen,    setProfileOpen]    = useState(false);
  const location  = useLocation();
  const navigate  = useNavigate();
  const active    = location.pathname;
  const userMenuRef = useRef(null);

  const { user, profile, loading, setUser } = useAuth();

  /* ── close user menu on outside click ──────────────────────────── */
  useEffect(() => {
    const handler = (e) => {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target))
        setUserMenuOpen(false);
    };
    if (userMenuOpen) document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [userMenuOpen]);

  /* ── close menus on route change ───────────────────────────────── */
  useEffect(() => {
    setUserMenuOpen(false);
    setMenuOpen(false);
  }, [location.pathname]);

  /* ── prevent body scroll on mobile menu ────────────────────────── */
  useEffect(() => {
    if (menuOpen && window.innerWidth <= 768)
      document.body.classList.add("menu-open");
    else
      document.body.classList.remove("menu-open");
    return () => document.body.classList.remove("menu-open");
  }, [menuOpen]);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      setUserMenuOpen(false);
      setMenuOpen(false);
      navigate("/home");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const openProfile = () => {
    setUserMenuOpen(false);
    setMenuOpen(false);
    setProfileOpen(true);
  };

  const toggleMenu = () => {
    setMenuOpen((p) => !p);
    setUserMenuOpen(false);
  };

  /* ── Avatar helper ──────────────────────────────────────────────── */
  const AvatarBadge = ({ size = 28 }) => {
    if (profile?.pfp_url) {
      return (
        <img
          src={profile.pfp_url}
          alt="avatar"
          className="nav-avatar-img"
          style={{ width: size, height: size, borderRadius: 8, objectFit: "cover" }}
        />
      );
    }
    const initials = profile?.full_name
      ? profile.full_name.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
      : (user?.email?.[0] || "U").toUpperCase();
    return (
      <span
        className="nav-avatar-initials"
        style={{ width: size, height: size, fontSize: size * 0.38 }}
        aria-hidden="true"
      >
        {initials}
      </span>
    );
  };

  /* ── Display name / email ───────────────────────────────────────── */
  const displayName = profile?.full_name || user?.email || "";
  const shortName   = displayName.length > 20
    ? displayName.slice(0, 18) + "…"
    : displayName;

  /* ── Auth section ───────────────────────────────────────────────── */
  const renderAuthSection = () => {
    if (loading) {
      return (
        <div
          className="nav-link-skeleton"
          style={{
            width: 100,
            height: 20,
            background: "rgba(255,255,255,0.1)",
            borderRadius: 4,
            opacity: 0.6,
          }}
        />
      );
    }

    if (!user) {
      return (
        <Link
          to="/login"
          className={`nav-link ${active === "/login" ? "active" : ""}`}
          onClick={() => setMenuOpen(false)}
        >
          Get Started
        </Link>
      );
    }

    return (
      <>
        <Link
          to="/dashboard"
          className={`nav-link ${active === "/dashboard" ? "active" : ""}`}
          onClick={() => setMenuOpen(false)}
        >
          Dashboard
        </Link>

        <div className="user-dropdown" ref={userMenuRef}>
          <button
            type="button"
            onClick={() => setUserMenuOpen((p) => !p)}
            aria-haspopup="true"
            aria-expanded={userMenuOpen}
          >
            <AvatarBadge size={26} />
            <span>{shortName}</span>
          </button>

          {userMenuOpen && (
            <div className="user-menu">
              <button type="button" onClick={openProfile} className="user-menu-profile">
                <Settings size={15} />
                Edit Profile
              </button>
              <div className="user-menu-separator" />
              <button type="button" onClick={handleLogout} className="user-menu-logout">
                <LogOut size={15} />
                Logout
              </button>
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <>
      <div id="navbar" className={menuOpen ? "expanded" : ""}>
        <div className="brand">
          <div className="brand-name"><h1>E.v.e</h1></div>

          <div className={`brand-links ${menuOpen ? "open" : ""}`}>
            <Link
              to="/home"
              className={`nav-link ${active === "/home" ? "active" : ""}`}
              onClick={() => setMenuOpen(false)}
            >Home</Link>

            <Link
              to="/about"
              className={`nav-link ${active === "/about" ? "active" : ""}`}
              onClick={() => setMenuOpen(false)}
            >About</Link>

            {renderAuthSection()}
          </div>

          <button
            type="button"
            className="navbar-toggler"
            onClick={toggleMenu}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
          >
            {menuOpen ? <X /> : <TextAlignJustify />}
          </button>
        </div>
      </div>

      {/* Profile overlay — rendered at top level so it's above navbar */}
      {profileOpen && <UserProfile onClose={() => setProfileOpen(false)} />}
    </>
  );
}