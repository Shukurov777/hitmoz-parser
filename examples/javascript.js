// Works in browser and Node 18+ (CORS is enabled)
const API = "https://bakha.me/hitmoz";

const res = await fetch(`${API}/search?q=${encodeURIComponent("Jony")}&limit=5`);
const { songs } = await res.json();
for (const s of songs) console.log(`${s.rank}. ${s.artist} — ${s.title} [${s.duration}] ${s.download}`);
