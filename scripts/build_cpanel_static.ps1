$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$frontend = Join-Path $root "frontend"
$backend = Join-Path $root "backend"
$templatesTarget = Join-Path $backend "templates\frontend"
$staticTarget = Join-Path $backend "static\frontend"

Push-Location $frontend
try {
  $env:VITE_PUBLIC_BASE = "/static/frontend/"
  $env:VITE_API_BASE_URL = "/api/v1"
  npm run build
} finally {
  Remove-Item Env:\VITE_PUBLIC_BASE -ErrorAction SilentlyContinue
  Remove-Item Env:\VITE_API_BASE_URL -ErrorAction SilentlyContinue
  Pop-Location
}

New-Item -ItemType Directory -Force -Path $templatesTarget | Out-Null
if (Test-Path -LiteralPath $staticTarget) {
  Remove-Item -LiteralPath $staticTarget -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $staticTarget | Out-Null

Copy-Item -LiteralPath (Join-Path $frontend "dist\index.html") -Destination (Join-Path $templatesTarget "index.html") -Force
Copy-Item -Path (Join-Path $frontend "dist\*") -Destination $staticTarget -Recurse -Force
