$ErrorActionPreference = "Stop"

python -m PyInstaller `
  --name TextDrop `
  --onefile `
  --windowed `
  --clean `
  --paths src `
  src\textdrop\app.py

