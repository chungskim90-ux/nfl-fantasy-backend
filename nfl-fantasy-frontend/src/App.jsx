import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import NewsFeed from "./pages/NewsFeed";
import TopPerformers from "./pages/TopPerformers";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: "1rem", fontFamily: "system-ui, sans-serif" }}>
        <h1>NFL Fantasy Dashboard</h1>

        <nav style={{ marginBottom: "1rem", display: "flex", gap: "1rem" }}>
          <Link to="/">News Feed</Link>
          <Link to="/top-performers">Top Performers</Link>
        </nav>

        <Routes>
          <Route path="/" element={<NewsFeed />} />
          <Route path="/top-performers" element={<TopPerformers />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
