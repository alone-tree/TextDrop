$ErrorActionPreference = "Stop"

$releaseName = "TextDrop-v0.1-windows"
$releaseDir = Join-Path "dist" $releaseName
$zipPath = Join-Path "dist" "$releaseName.zip"

if (Test-Path $releaseDir) {
  Remove-Item -Recurse -Force $releaseDir
}

if (Test-Path $zipPath) {
  Remove-Item -Force $zipPath
}

python -m PyInstaller `
  --name TextDrop `
  --onedir `
  --windowed `
  --clean `
  --icon assets\app_icon.ico `
  --add-data "assets;assets" `
  --distpath $releaseDir `
  --workpath build `
  --paths src `
  src\textdrop\app.py

Compress-Archive -Path (Join-Path $releaseDir "TextDrop") -DestinationPath $zipPath -Force

Write-Host "Build output: $(Join-Path $releaseDir 'TextDrop')"
Write-Host "Zip output: $zipPath"
