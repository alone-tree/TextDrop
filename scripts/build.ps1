# Copyright (C) 2026  alone-tree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
