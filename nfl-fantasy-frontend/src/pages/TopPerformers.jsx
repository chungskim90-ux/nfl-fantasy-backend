import { useEffect, useState } from "react";

export default function TopPerformers() {
  const [leagueId, setLeagueId] = useState("");
  const [week, setWeek] = useState(1);
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    if (!leagueId) return;

    setLoading(true);
    const res = await fetch(
      `/api/top-performers?league_id=${leagueId}&week=${week}`
    );
    const data = await res.json();
    setPlayers(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, [leagueId, week]);

  return (
    <div style={{ padding: "1rem" }}>
      <h1>Weekly Top Performers</h1>

      <div style={{ marginBottom: "1rem" }}>
        <input
          placeholder="Sleeper League ID"
          value={leagueId}
          onChange={(e) => setLeagueId(e.target.value)}
        />

        <input
          type="number"
          min={1}
          max={18}
          value={week}
          onChange={(e) => setWeek(Number(e.target.value))}
          style={{ marginLeft: "1rem" }}
        />
      </div>

      {loading ? (
        <p>Loading…</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Player</th>
              <th>Team</th>
              <th>Pos</th>
              <th>Points</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p) => (
              <tr key={p.player_id}>
                <td>{p.name}</td>
                <td>{p.team}</td>
                <td>{p.position}</td>
                <td>{p.points.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
