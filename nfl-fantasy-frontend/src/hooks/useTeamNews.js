import { useEffect, useState } from "react";

export function useTeamNews(team) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    if (!team) return;
    fetch(`http://localhost:8000/team/${team}`)
      .then(res => res.json())
      .then(setItems);
  }, [team]);

  return items;
}
