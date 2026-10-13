# THROWAWAY SPIKE: not engine code. Purpose: watch the s09 poller's JSONL (local file only, no network) and print one line per notable change (lineup confirmed, starters visible, game status change, injury change); exit at a UTC deadline.
import json, time, sys, datetime, glob
from pathlib import Path

OUT = Path(__file__).parent / "out"
deadline = datetime.datetime.fromisoformat(sys.argv[1])  # e.g. 2026-10-13T23:20:00+00:00
path = sorted(OUT.glob("*_pretip_poller.jsonl"))[-1]
seen = 0
state = {}
while datetime.datetime.now(datetime.timezone.utc) < deadline:
    lines = path.read_text(encoding="utf-8").splitlines()
    for l in lines[seen:]:
        d = json.loads(l); s = d.get("summary"); k = d["kind"]; t = d["t_utc"][11:19]
        if k == "rotowire_lineups" and isinstance(s, dict):
            st = {tuple(g["teams"]): tuple(x["status"] for x in g["sides"]) for g in s["games"] if g["teams"]}
            if st != state.get(k):
                print(f"{t} rotowire {st}", flush=True); state[k] = st
        elif k == "espn_summary" and isinstance(s, dict):
            v = (s.get("status"), len(s.get("box_starters") or []), len(s.get("roster_starters") or []))
            if v != state.get(k):
                print(f"{t} espn_summary status={v[0]} box_starters={v[1]} roster_starters={v[2]}", flush=True); state[k] = v
        elif k == "nba_scoreboardv3" and isinstance(s, dict):
            v = (s.get("gameStatus"), s.get("text"))
            if v != state.get(k):
                print(f"{t} nba_scoreboard {v}", flush=True); state[k] = v
        elif k == "nba_boxscore" and isinstance(s, dict):
            v = (s.get("n_players"), s.get("n_with_position(starters)"))
            if v != state.get(k):
                print(f"{t} nba_boxscore players={v[0]} starters={v[1]}", flush=True); state[k] = v
        elif k == "espn_injuries" and isinstance(s, dict) and s.get("changes") and len(s["changes"]) < 10:
            print(f"{t} espn_injuries changes={s['changes'][:4]}", flush=True)
        elif k in ("end",) or d.get("stopped_host"):
            print(f"{t} {k} {d}", flush=True)
    seen = len(lines)
    time.sleep(20)
print("deadline reached", flush=True)
