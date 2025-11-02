# SPSKladno-Project

Jednoduchý RPG projekt (Flask + PyQt6 + Pygame).

**Cíl**: Aby kdokoli mohl repo stáhnout a spustit bez problémů.

## Požadavky
- `Python 3.11` (doporučeno)
- Windows, macOS nebo Linux

## Rychlý Start (Windows)
- Otevři PowerShell v kořeni projektu.
- Vytvoř a aktivuj virtuální prostředí, nainstaluj závislosti:
  - `python -m venv venv`
  - `.\n+venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`
- Spusť aplikaci:
  - `python launcher.py`

Pokud PowerShell blokuje aktivaci skriptu (není digitálně podepsán), povol lokální skripty:
- `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Rychlý Start (macOS / Linux)
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python launcher.py`

## Setup skripty (volitelné)
- Windows: `PowerShell -ExecutionPolicy Bypass -File .\setup.ps1`
- macOS/Linux: `chmod +x setup.sh && ./setup.sh`

## Co je v repu důležité
- `requirements.txt` — všechny závislosti (včetně `pygame`).
- `launcher.py` — spustí Flask server a herního klienta.
- `app.py`, `templates/`, `data/`, `sounds/`, `icons/` — backend, UI a assety.
- `instance/rpg_game.db` — lokální SQLite databáze (generuje se automaticky, můžeš ji smazat když chceš čistý start).

## Necommituj (už je ignorováno v .gitignore)
- `venv/`, `__pycache__/`, dočasné soubory.
- Pokud máš staré prostředí `rpg_env/`, smaž ho lokálně; nevkládej ho do repozitáře.

## Typické problémy a řešení
- Aktivace venv na Windows je blokovaná:
  - Spusť: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - Nebo aktivuj s bypass: `PowerShell -ExecutionPolicy Bypass -File .\venv\Scripts\Activate.ps1`
- Chybí balíček (např. `pygame`):
  - Ujisti se, že jsi aktivoval `venv` a spusť `pip install -r requirements.txt`.

## Vývoj
- Po změně závislostí aktualizuj `requirements.txt` (např. `pip freeze > requirements.txt`).
- Nespouštěj aplikaci mimo venv — jinak budeš chybět závislosti.

## Licence
Projekt pro maturitu. Používej dle školních pravidel.
