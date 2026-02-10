import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import aboutVideo2 from "/about_video2.mp4";
import { Mail, Lock, Eye, EyeOff, LogIn, UserPlus } from "lucide-react";
import toast, { Toaster } from "react-hot-toast";
import "./auth.css";
import { login, register } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";

export default function AuthComponent() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const { setUser } = useAuth();

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); // ✅ This prevents default form submission
    e.stopPropagation(); // ✅ Stop event bubbling
    
    setLoading(true);

    // Validation for registration
    if (!isLogin && formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match!");
      setLoading(false);
      return;
    }

    if (!isLogin && formData.password.length < 6) {
      toast.error("Password must be at least 6 characters!");
      setLoading(false);
      return;
    }

    try {
      const data = isLogin
        ? await login(formData.email, formData.password)
        : await register(formData.email, formData.password);

      setUser(data);
      toast.success(isLogin ? "Login successful!" : "Account created!");
      
      // Reset form
      setFormData({
        email: "",
        password: "",
        confirmPassword: "",
      });

      // Redirect after successful login
      setTimeout(() => {
        navigate("/dashboard");
      }, 500);
      
    } catch (err) {
      toast.error(err.message || "Something went wrong!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="authform">
      <Toaster position="top-center" />
      <div className="form">
        <div className="left">
          <video
            className="auth-video"
            src={aboutVideo2}
            autoPlay
            playsInline
            muted
            loop
          />
        </div>

        <div className="right">
          <div className="togglebt">
            <button
              type="button" // ✅ Add type="button" to prevent form submission
              className={`loginbt ${isLogin ? "active" : ""}`}
              onClick={() => {
                setIsLogin(true);
                setFormData({
                  email: "",
                  password: "",
                  confirmPassword: "",
                });
              }}
            >
              <LogIn />
              Login
            </button>
            <button
              type="button" // ✅ Add type="button" to prevent form submission
              className={`registerbt ${!isLogin ? "active" : ""}`}
              onClick={() => {
                setIsLogin(false);
                setFormData({
                  email: "",
                  password: "",
                  confirmPassword: "",
                });
              }}
            >
              <UserPlus />
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="input-form">
            <div className="intro">
              <h1 className="intro-title">
                {isLogin ? "Welcome Back!" : "Create Account"}
              </h1>
              <p className="intro-desc">
                {isLogin
                  ? "Enter your credentials to access your account"
                  : "Join the E.V.E. community today"}
              </p>
            </div>

            <div className="fields">
              <div className="field-wrapper">
                <Mail />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Email Address"
                  required
                  autoComplete="email"
                />
              </div>

              <div className="field-wrapper">
                <Lock />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Password"
                  required
                  minLength={6}
                  autoComplete={isLogin ? "current-password" : "new-password"}
                />
                <button
                  type="button" // ✅ Prevents form submission
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label="Toggle password visibility"
                >
                  {showPassword ? <EyeOff /> : <Eye />}
                </button>
              </div>

              {!isLogin && (
                <div className="field-wrapper">
                  <Lock />
                  <input
                    type={showConfirmPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    placeholder="Confirm Password"
                    required={!isLogin}
                    minLength={6}
                    autoComplete="new-password"
                  />
                  <button
                    type="button" // ✅ Prevents form submission
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    aria-label="Toggle confirm password visibility"
                  >
                    {showConfirmPassword ? <EyeOff /> : <Eye />}
                  </button>
                </div>
              )}

              <button 
                type="submit" 
                className="submit-btn" 
                disabled={loading}
              >
                {loading ? (
                  <span className="spinner" />
                ) : (
                  <>
                    {isLogin ? <LogIn /> : <UserPlus />}
                    {isLogin ? "Sign In" : "Create Account"}
                  </>
                )}
              </button>
            </div>

            {isLogin && (
              <div className="forgot-password">
                <a 
                  href="#forgot" 
                  onClick={(e) => e.preventDefault()} // ✅ Prevent navigation
                >
                  Forgot Password?
                </a>
              </div>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}