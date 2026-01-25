import React, { useEffect } from "react";
import "./problemst.css";
import { useRef, useState } from "react";

export default function ProblemSt() {
  const featRef = useRef(null);
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
    if (featRef.current) observer.observe(featRef.current);
    return () => observer.disconnect();
  });
  return (
    <div
      id="problem-statement"
      ref={featRef}
      className={`feature ${visible ? "visible" : ""}`}
    >
      <div className="punchline">
        <div>
          <img src="./bg.jpg" alt="" className="hero-image" />

          <h1 className="punchline-main">
            AI execution <br />
            today is <br />
            inefficient and <br />
            one-dimensional
          </h1>
          <h3 className="punchline-sub">
            Most organizations rely on single general-purpose models for every
            type of task. This forces manual model switching, wastes compute,
            and limits performance. When the controller fails, the entire
            workflow stops creating bottlenecks that make real-world deployments
            impractical.
          </h3>
        </div>
      </div>
      <div className="main-features">
        <div className="col1">
          <div className="task">
            <h2>Task-Aware Model Selection</h2>
          </div>

          <div className="hybrid">
            <h2>Hybrid AI Execution</h2>
          </div>
        </div>
        <div className="col2">
          <div className="fault">
            <h2>Fault Tolerance</h2>
          </div>
        </div>
      </div>
    </div>
  );
}
