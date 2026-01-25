import React, { useEffect } from "react";
import "./power.css";
import { useRef, useState } from "react";

export default function Power() {
  const powerRef = useRef(null);
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
    if (powerRef.current) observer.observe(powerRef.current);
    return () => observer.disconnect();
  });
  return (
    <div
      id="power"
      ref={powerRef}
      className={`powers ${visible ? "visible" : ""}`}
    >
      <div className="main-power">
        <h1>
          Orchestrating The
          <br />
          <span className="future">Future</span> of AI
        </h1>
      </div>
      <div className="what-powers">
        <div className="col1">
          <div className="pow1">
            <div>
              <h1>
                Build Specialized
                <br /> AI Workflows
              </h1>
            </div>
            <div>
              <h3>
                The Master Controller analyzes each task and selects the optimal
                AI worker based on complexity, quality expectations, and system
                constraints, no manual intervention required.
              </h3>
              <video
                src="./agent.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="agent-video"
              ></video>
            </div>
          </div>
          <div className="pow2">
            <div>
              {" "}
              <h1>Efficiency & Performance</h1>
            </div>
            <div>
              <h3>
                Generalist workers handle lightweight tasks, while specialist
                nodes take over high-value workloads, balancing speed, accuracy,
                and resource cost across the execution pipeline.
              </h3>
            </div>
          </div>
        </div>
        <div className="col2">
          <div className="pow3">
            <div>
              <img src="./bg-logo.png" className="bglogo"></img>
              <h1>Enterprise Reliability</h1>
            </div>
            <div>
              <h3>
                E.V.E maintains continuity even if a master node fails, ensuring
                workflows never stop due to a single point of failure, a key
                requirement in real-world deployments.
              </h3>
            </div>
          </div>
          <div className="pow4">
            <div>
              <h1>Optimization Layer</h1>
            </div>
            <div>
              <h3>
                Worker execution history, latency, and quality metrics are
                recorded for transparent benchmarking and explainable
                decision-making across the system.
              </h3>
              <video
                src="./revenue.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="revenue-video"
              ></video>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
