import { useState, useEffect } from "react";

const NFL_TEAMS = [
  { abbr: "ALL", name: "All Teams" },
  { abbr: "ARI", name: "Arizona Cardinals" },
  { abbr: "ATL", name: "Atlanta Falcons" },
  { abbr: "BAL", name: "Baltimore Ravens" },
  { abbr: "BUF", name: "Buffalo Bills" },
  { abbr: "CAR", name: "Carolina Panthers" },
  { abbr: "CHI", name: "Chicago Bears" },
  { abbr: "CIN", name: "Cincinnati Bengals" },
  { abbr: "CLE", name: "Cleveland Browns" },
  { abbr: "DAL", name: "Dallas Cowboys" },
  { abbr: "DEN", name: "Denver Broncos" },
  { abbr: "DET", name: "Detroit Lions" },
  { abbr: "GB", name: "Green Bay Packers" },
  { abbr: "HOU", name: "Houston Texans" },
  { abbr: "IND", name: "Indianapolis Colts" },
  { abbr: "JAX", name: "Jacksonville Jaguars" },
  { abbr: "KC", name: "Kansas City Chiefs" },
  { abbr: "LV", name: "Las Vegas Raiders" },
  { abbr: "LAC", name: "Los Angeles Chargers" },
  { abbr: "LAR", name: "Los Angeles Rams" },
  { abbr: "MIA", name: "Miami Dolphins" },
  { abbr: "MIN", name: "Minnesota Vikings" },
  { abbr: "NE", name: "New England Patriots" },
  { abbr: "NO", name: "New Orleans Saints" },
  { abbr: "NYG", name: "New York Giants" },
  { abbr: "NYJ", name: "New York Jets" },
  { abbr: "PHI", name: "Philadelphia Eagles" },
  { abbr: "PIT", name: "Pittsburgh Steelers" },
  { abbr: "SEA", name: "Seattle Seahawks" },
  { abbr: "SF", name: "San Francisco 49ers" },
  { abbr: "TB", name: "Tampa Bay Buccaneers" },
  { abbr: "TEN", name: "Tennessee Titans" },
  { abbr: "WAS", name: "Washington Commanders" },
];

const TEAM_LOGOS = {
  ARI: "https://a.espncdn.com/i/teamlogos/nfl/500/ari.png",
  ATL: "https://a.espncdn.com/i/teamlogos/nfl/500/atl.png",
  BAL: "https://a.espncdn.com/i/teamlogos/nfl/500/bal.png",
  BUF: "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
  CAR: "https://a.espncdn.com/i/teamlogos/nfl/500/car.png",
  CHI: "https://a.espncdn.com/i/teamlogos/nfl/500/chi.png",
  CIN: "https://a.espncdn.com/i/teamlogos/nfl/500/cin.png",
  CLE: "https://a.espncdn.com/i/teamlogos/nfl/500/cle.png",
  DAL: "https://a.espncdn.com/i/teamlogos/nfl/500/dal.png",
  DEN: "https://a.espncdn.com/i/teamlogos/nfl/500/den.png",
  DET: "https://a.espncdn.com/i/teamlogos/nfl/500/det.png",
  GB:  "https://a.espncdn.com/i/teamlogos/nfl/500/gb.png",
  HOU: "https://a.espncdn.com/i/teamlogos/nfl/500/hou.png",
  IND: "https://a.espncdn.com/i/teamlogos/nfl/500/ind.png",
  JAX: "https://a.espncdn.com/i/teamlogos/nfl/500/jax.png",
  KC:  "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
  LV:  "https://a.espncdn.com/i/teamlogos/nfl/500/lv.png",
  LAC: "https://a.espncdn.com/i/teamlogos/nfl/500/lac.png",
  LAR: "https://a.espncdn.com/i/teamlogos/nfl/500/lar.png",
  MIA: "https://a.espncdn.com/i/teamlogos/nfl/500/mia.png",
  MIN: "https://a.espncdn.com/i/teamlogos/nfl/500/min.png",
  NE:  "https://a.espncdn.com/i/teamlogos/nfl/500/ne.png",
  NO:  "https://a.espncdn.com/i/teamlogos/nfl/500/no.png",
  NYG: "https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png",
  NYJ: "https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png",
  PHI: "https://a.espncdn.com/i/teamlogos/nfl/500/phi.png",
  PIT: "https://a.espncdn.com/i/teamlogos/nfl/500/pit.png",
  SEA: "https://a.espncdn.com/i/teamlogos/nfl/500/sea.png",
  SF:  "https://a.espncdn.com/i/teamlogos/nfl/500/sf.png",
  TB:  "https://a.espncdn.com/i/teamlogos/nfl/500/tb.png",
  TEN: "https://a.espncdn.com/i/teamlogos/nfl/500/ten.png",
  WAS: "https://a.espncdn.com/i/teamlogos/nfl/500/was.png",
};

function App() {
  const [team, setTeam] = useState("ALL");
  const [breakingOnly, setBreakingOnly] = useState(false);
  const [items, setItems] = useState([]);

  useEffect(() => {
    const endpoint =
      team === "ALL"
        ? `http://localhost:8000/items?min_relevance=${breakingOnly ? 80 : 0}`
        : `http://localhost:8000/items?team=${team}&min_relevance=${breakingOnly ? 80 : 0}`;

    fetch(endpoint)
      .then(res => res.json())
      .then(setItems);
  }, [team, breakingOnly]);

  return (
    <div style={{ padding: "1rem", fontFamily: "system-ui, sans-serif" }}>
      <h1>NFL Fantasy News Feed</h1>

      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <label>
          <span>Select Team: </span>
          <select
            value={team}
            onChange={(e) => setTeam(e.target.value)}
            style={{ marginLeft: "0.5rem", padding: "0.25rem 0.5rem" }}
          >
            {NFL_TEAMS.map(t => (
              <option key={t.abbr} value={t.abbr}>
                {t.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          <input
            type="checkbox"
            checked={breakingOnly}
            onChange={(e) => setBreakingOnly(e.target.checked)}
            style={{ marginRight: "0.5rem" }}
          />
          Breaking News Only (≥ 80)
        </label>
      </div>

      <ul style={{ listStyle: "none", padding: 0, marginTop: "1rem" }}>
        {items.map((item) => (
          <li
            key={item.id}
            style={{
              border: "1px solid #ddd",
              borderRadius: "6px",
              padding: "0.75rem",
              marginBottom: "0.5rem",
              background: "#fafafa",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              {TEAM_LOGOS[item.team] && (
                <img
                  src={TEAM_LOGOS[item.team]}
                  alt={item.team}
                  style={{ width: "32px", height: "32px", borderRadius: "4px" }}
                />
              )}

              <div style={{ fontSize: "0.85rem", color: "#555" }}>
                {item.team} • {item.player_name || "Unknown"} • {item.source}
              </div>
            </div>

            <div style={{ marginTop: "0.25rem" }}>{item.text}</div>

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: "0.4rem",
                fontSize: "0.8rem",
              }}
            >
              {item.url && (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: "#0077cc" }}
                >
                  Source link
                </a>
              )}
              <span>Relevance: {item.fantasy_relevance}</span>
            </div>
          </li>
        ))}
      </ul>

      {items.length === 0 && (
        <div style={{ marginTop: "1rem", color: "#777" }}>
          No items found for this team.
        </div>
      )}
    </div>
  );
}

export default App;
