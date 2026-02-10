import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./routes/ProtectedRoute";
import GuestRoute from "./routes/GuestRoute";

import Navbar from "./components/Navigation/Navbar";
import Footer from "./components/Footer/Footer";
import Main from "./components/Home/Main";
import About from "./components/About/About";
import AuthComponent from "./components/Auth/AuthComponent";
import Dashboard from "./components/Chat/Dashboard";
import ScrollToTop from "./components/ScrollToTop";

export default function App() {
  return (
    <div className="app">
      <AuthProvider>
        <ScrollToTop />
        <Navbar />
        <main className="app-main">
          <Routes>
            {/* root redirect */}
            <Route path="/" element={<Navigate to="/home" replace />} />

            <Route path="/home" element={<Main />} />
            <Route path="/about" element={<About />} />

            {/* Guest-only */}
            <Route
              path="/login"
              element={
                <GuestRoute>
                  <AuthComponent />
                </GuestRoute>
              }
            />

            {/* Protected */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* catch-all */}
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </main>
        <Footer />
      </AuthProvider>
    </div>
  );
}
