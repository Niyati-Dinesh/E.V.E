import React from "react";
import { Link } from "react-router-dom";
import "./home.css";
import { useRef, useState, useEffect } from "react";
export default function Home() {
  const titleRef = useRef(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0,
        rootMargin: "0px 0px -100px 0px",
      },
    );
    if (titleRef.current) observer.observe(titleRef.current);
    return () => observer.disconnect();
  });
  return (
    <section
      id="home"
      ref={titleRef}
      className={`title ${visible ? "visible" : ""}`}
    >
      <video
        src="/home.mp4"
        autoPlay
        loop
        muted
        playsInline
        className="hero-video"
      />

      <div className="hero-content">
        <h1 className="hero-title">
          Efficient,
          <br />
          adaptive,
          <br />
          and <span className="seamless">seamless</span>
          <br />
          execution
        </h1>

        <p className="hero-sub">Revolutionizing AI orchestration</p>

        <Link to="/login" className="hero-cta">
          Join us
        </Link>
      </div>
    </section>
  );
}
