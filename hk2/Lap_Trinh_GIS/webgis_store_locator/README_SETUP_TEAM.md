# Team Setup (Shared Structure, Local DB)

This project is set up so each teammate uses:
- the same code + migrations + fixture in Git
- a separate local PostgreSQL database

## One-command setup

From project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1
```

## Useful options

- Recreate virtual environment:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -RecreateVenv
```

- Reset local DB data and reload fixture:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -FlushData
```

- Setup and run server immediately:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_team.ps1 -RunServer -Port 8000
```

## Required local config

Each teammate must create/update `.env` to point to their own local DB credentials.
Do not share real DB passwords in Git.
