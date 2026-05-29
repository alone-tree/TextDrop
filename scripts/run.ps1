# Copyright (C) 2026  alone-tree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw "uv was not found. Install uv first: https://docs.astral.sh/uv/"
}

if (-not $env:UV_LINK_MODE) {
  $env:UV_LINK_MODE = "copy"
}

uv run python -m textdrop
