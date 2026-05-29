# Copyright (C) 2026  alone-tree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$venv = Join-Path $root ".venv"
$python = Join-Path $venv "Scripts\python.exe"

Set-Location $root

if (-not (Test-Path $python)) {
  python -m venv $venv
}

& $python -m pip install -e .
& $python -m textdrop
