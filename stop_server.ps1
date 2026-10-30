# WordFeather Local Server Stopper
# Stops ONLY the WordFeather development server.
# Does NOT touch Docker Desktop, does NOT stop thorsten-kokoro-tts,
# and does NOT kill unrelated Python/Node processes.

$ErrorActionPreference = 'SilentlyContinue'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
if (-not $repoRoot) { $repoRoot = Get-Location }

$pidFile = Join-Path $repoRoot 'dev_server.pid'
$stopped = $false

# 1. Check PID file first
if (Test-Path $pidFile) {
    $rawPid = (Get-Content $pidFile -Raw).Trim()
    if ($rawPid -match '^\d+$') {
        $targetPid = [int]$rawPid
        $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue
        if ($proc) {
            # Verify command line to ensure it is dev_server
            $cimProc = Get-CimInstance Win32_Process -Filter "ProcessId = $targetPid"
            $cmdLine = $cimProc.CommandLine
            if ($cmdLine -and $cmdLine -match 'dev_server') {
                Stop-Process -Id $targetPid -Force
                Write-Host "  [OK] Stopped WordFeather dev server (PID $targetPid)." -ForegroundColor Green
                $stopped = $true
            } elseif ($proc.ProcessName -match 'python|node') {
                # If process name is python/node and listening on port 8080
                $conn = Get-NetTCPConnection -LocalPort 8080 -OwningProcess $targetPid -State Listen -ErrorAction SilentlyContinue
                if ($conn) {
                    Stop-Process -Id $targetPid -Force
                    Write-Host "  [OK] Stopped WordFeather dev server on port 8080 (PID $targetPid)." -ForegroundColor Green
                    $stopped = $true
                }
            }
        }
    }
    Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
}

# 2. Secondary check: inspect any process listening on port 8080
$connections = Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue
if ($connections) {
    $owningPids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($p in $owningPids) {
        $cimProc = Get-CimInstance Win32_Process -Filter "ProcessId = $p"
        if ($cimProc) {
            $cmd = $cimProc.CommandLine
            if ($cmd -match 'dev_server') {
                Stop-Process -Id $p -Force
                Write-Host "  [OK] Stopped server process on port 8080 (PID $p)." -ForegroundColor Green
                $stopped = $true
            }
        }
    }
}

if ($stopped) {
    Write-Host ""
    Write-Host "  [INFO] WordFeather web server was stopped." -ForegroundColor Cyan
    Write-Host "  [INFO] Docker Desktop and container 'thorsten-kokoro-tts' remain running." -ForegroundColor Cyan
} else {
    Write-Host "  [INFO] WordFeather web server is not currently running." -ForegroundColor Yellow
}
