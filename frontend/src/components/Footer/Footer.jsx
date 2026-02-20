import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Mail, Home, Building2, PhoneCall } from "lucide-react";
import "./footer.css";

export default function Footer() {
  const navigate = useNavigate();

  const handleHome = (e) => {
    e.preventDefault();
    navigate("/");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <footer className="footer">
      <div className="footer-inner">

        {/* ── Brand ── */}
        <div className="footer-brand">
          <img src="/logo-transparent.png" alt="EVE" className="footer-logo" />
          <span className="footer-fullform">Execution Versatility Engine</span>
        </div>

        {/* ── Nav icons ── */}
        <nav className="footer-nav" aria-label="Footer navigation">
          <a href="/" onClick={handleHome} title="Home" className="footer-nav-link">
            <Home size={16} />
            <span>Home</span>
          </a>
          <a
            href="https://naicoits.com/"
            target="_blank"
            rel="noopener noreferrer"
            title="Company"
            className="footer-nav-link"
          >
            <Building2 size={16} />
            <span>Company</span>
          </a>
          <a
            href="https://naicoits.com/#contactUs"
            target="_blank"
            rel="noopener noreferrer"
            title="Contact"
            className="footer-nav-link"
          >
            <PhoneCall size={16} />
            <span>Contact</span>
          </a>
        </nav>

        {/* ── Divider ── */}
        <div className="footer-rule" />

        {/* ── Bottom strip ── */}
        <div className="footer-bottom">
          <a href="mailto:ignite.techteam33@gmail.com" className="footer-email">
            <Mail size={14} />
            <span>ignite.techteam33@gmail.com</span>
          </a>

          <div className="footer-legal">
            <Link to="/terms" className="footer-legal-link">Terms &amp; Conditions</Link>
            <span className="footer-dot">·</span>
            <a href="#" className="footer-legal-link">Privacy Policy</a>
            <span className="footer-dot">·</span>
            <span className="footer-copy">© {new Date().getFullYear()} EVE</span>
          </div>
        </div>

      </div>
    </footer>
  );
}