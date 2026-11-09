# FOIMOD-5410 isolated local migration tests, Windows PowerShell 5.1+.
# Never connects to FOI Mod clusters or remote databases.
$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
$pg = "foimod5410-db"
$network = "foimod5410-net"

# Generate an ephemeral password for the isolated test database.
$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
try {
    $rng.GetBytes($bytes)
} finally {
    $rng.Dispose()
}
$dbPassword = [BitConverter]::ToString($bytes).Replace("-", "").ToLowerInvariant()

if (!(Test-Path (Join-Path $repo "request-management-api/migrations/tests/test_foimod_5410_migration.py"))) {
    throw "Test script missing. Extract package into $repo first."
}

docker info --format '{{.ServerVersion}}' | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop is not running" }

# Never reuse an existing container: it might not be our disposable fixture.
$old = docker container ls -a --filter "name=^/$pg$" --format '{{.Names}}'
if ($old) { throw "Container $pg already exists. Inspect it before rerunning." }

$net = docker network ls --filter "name=^$network$" --format '{{.Name}}'
if (-not $net) {
    docker network create $network | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker network creation failed" }
}

Write-Host "Starting isolated PostgreSQL (no host ports published)"
docker run --name $pg --network $network `
    -e POSTGRES_USER=foimod5410 `
    -e "POSTGRES_PASSWORD=$dbPassword" `
    -e POSTGRES_DB=foimod5410_local `
    -d postgres:16-alpine | Out-Null
if ($LASTEXITCODE -ne 0) { throw "Failed to start temporary PostgreSQL" }

$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    cmd.exe /d /c "docker exec $pg pg_isready -h 127.0.0.1 -U foimod5410 -d foimod5410_local 1>nul 2>nul"
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ready) { throw "PostgreSQL did not become ready" }

Write-Host "Running Alembic revision upgrade/downgrade and safety tests"
docker run --rm --network $network `
    -v "${repo}:/work:ro" -w /work `
    -e "FOIMOD_5410_TEST_URL=postgresql+psycopg2://foimod5410:${dbPassword}@${pg}:5432/foimod5410_local" `
    python:3.12-slim sh -c `
    'python -m pip install -q -r request-management-api/migrations/tests/requirements-foimod-5410-test.txt && python -m unittest discover -s request-management-api/migrations/tests -p "test_foimod_5410_migration.py" -v'
if ($LASTEXITCODE -ne 0) { throw "FOIMOD-5410 local tests FAILED" }

Write-Host "Tests passed. To remove the disposable DB:"
Write-Host "  docker rm -f $pg"
Write-Host "  docker network rm $network"
