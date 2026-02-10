import "./navbar.css";
import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { TextAlignJustify, X, User, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import { logout } from "../../api/auth";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const active = location.pathname;
  const userMenuRef = useRef(null);

  const { user, loading, setUser } = useAuth();

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setUserMenuOpen(false);
      }
    };

    if (userMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [userMenuOpen]);

  // Close menus when route changes
  useEffect(() => {
    setUserMenuOpen(false);
    setMenuOpen(false);
  }, [location.pathname]);

  // Prevent body scroll when menu is open (mobile)
  useEffect(() => {
    if (menuOpen && window.innerWidth <= 768) {
      document.body.classList.add("menu-open");
    } else {
      document.body.classList.remove("menu-open");
    }

    return () => {
      document.body.classList.remove("menu-open");
    };
  }, [menuOpen]);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      setUserMenuOpen(false);
      setMenuOpen(false);
      navigate("/home");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const toggleMenu = () => {
    setMenuOpen((prev) => !prev);
    setUserMenuOpen(false); // Close user menu when toggling main menu
  };

  // Render auth-dependent content with smooth transition
  const renderAuthSection = () => {
    if (loading) {
      // Show minimal loading skeleton
      return (
        <div 
          className="nav-link-skeleton"
          style={{
            width: '100px',
            height: '20px',
            background: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            opacity: 0.6
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
            onClick={() => setUserMenuOpen((prev) => !prev)}
          >
            <User />
            <span>{user.email}</span>
          </button>

          {userMenuOpen && (
            <div className="user-menu">
              <button type="button" onClick={handleLogout}>
                <LogOut />
                Logout
              </button>
            </div>
          )}
        </div>
      </>
    );
  };

  return (
    <div id="navbar" className={menuOpen ? "expanded" : ""}>
      <div className="brand">
        {/* Logo */}
        <div className="brand-name">
          <h1>E.v.e</h1>
        </div>

        {/* Links */}
        <div className={`brand-links ${menuOpen ? "open" : ""}`}>
          <Link
            to="/home"
            className={`nav-link ${active === "/home" ? "active" : ""}`}
            onClick={() => setMenuOpen(false)}
          >
            Home
          </Link>

          <Link
            to="/about"
            className={`nav-link ${active === "/about" ? "active" : ""}`}
            onClick={() => setMenuOpen(false)}
          >
            About
          </Link>

          {renderAuthSection()}
        </div>

        {/* Mobile Toggle - with icon transition */}
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
  );
}