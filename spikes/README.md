# spikes/ (THROWAWAY)

Everything in this folder is throwaway verification code written during the design session.
It is not engine code, it is not tested, and nothing in the engine should import it.

Each subfolder holds scripts for one research area. Each script writes its raw output to
`<area>/out/YYYYMMDD-HHMM_<name>.<ext>` so the design docs can cite exactly what ran and what came back.

Shared environment: `spikes/.venv` (created with uv, Python 3.13). It is gitignored.
