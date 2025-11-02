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
  - `.\venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt`
- Spusť aplikaci:
  - `python launcher.py`

Pokud PowerShell blokuje aktivaci skriptu (není digitálně podepsán), povol lokální skripty:
- `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Typické problémy a řešení
- Aktivace venv na Windows je blokovaná:
  - Spusť: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
  - Nebo aktivuj s bypass: `PowerShell -ExecutionPolicy Bypass -File .\venv\Scripts\Activate.ps1`
- Chybí balíček (např. `pygame`):
  - Ujisti se, že jsi aktivoval `venv` a spusť `pip install -r requirements.txt`.

## Licence
Projekt pro maturitu. Používej dle školních pravidel.
