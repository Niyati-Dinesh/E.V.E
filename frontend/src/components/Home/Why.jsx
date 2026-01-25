import "./why.css";
import React from "react";
import { useRef, useState, useEffect } from "react";
export default function Why() {
  const whyRef = useRef(null);
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
    if (whyRef.current) observer.observe(whyRef.current);
    return () => observer.disconnect();
  });
  return (
    <div id="why" ref={whyRef} className={`whys ${visible ? "visible" : ""}`}>
      <div className="reasons">

        <div className="col1">
          <div className="one">
            <h1>01</h1>
            <h3>Models are picked per task, not manually.</h3>
          </div>
          <div className="two">
            <h1>02</h1>
            <h3>Fault-tolerant pipelines designed for real workloads.</h3>
          </div>
        </div>

        <div className="col2">
          <video
            src="three ai agents.mp4"
            autoPlay
            loop
            muted
            playsInline
            className="three-agents"
          ></video>
        </div>

         <div className="col3">
          <div className="why-choose">
            <h2>Why choose <br/> EVE ?</h2>
          </div>
          <div className="three">
            <h1>03</h1>
            <h3>More output, lower inference cost.</h3>
          </div>
          <div className="four">
            <h1>04</h1>
            <h3>Latency, accuracy, throughput are all visible.</h3>
          </div>
        </div>

      </div>
    </div>
  );
}
