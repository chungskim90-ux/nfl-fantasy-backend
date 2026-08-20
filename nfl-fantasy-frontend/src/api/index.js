export const API = {
  getTeamNews: (team) =>
    fetch(`http://localhost:8000/team/${team}`).then(r => r.json()),

  getItems: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return fetch(`http://localhost:8000/items?${query}`).then(r => r.json());
  },

  ingest: () =>
    fetch(`http://localhost:8000/ingest`, { method: "POST" }).then(r => r.json()),

  debugFeeds: () =>
    fetch(`http://localhost:8000/debug-feeds`).then(r => r.json()),
};
