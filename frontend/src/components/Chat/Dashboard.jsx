import "./dashboard.css";

export default function Dashboard() {
  return (
    <div id="chat-interface">
      <img src="bg.jpg" className="dash-bg"/>
    <div className="video-and cards">
      <div>
        <video
        src="/agent.mp4"
        autoPlay
        loop
        muted
        playsInline
        className="dashboard-video"
      />
      </div>
      <div className="fn-cards">
        <div className="arc-ui">
          <div className="ui-card left">Analyse</div>
          <div className="ui-card center">Documentation</div>
          <div className="ui-card right">Coding</div>
        </div>
      </div>
      
      </div>
    </div>
  );
}