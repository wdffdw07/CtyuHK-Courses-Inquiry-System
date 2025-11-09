<#
Render.ps1 - Convenience script to generate both dependency and roots-only graphs in one run.

Usage examples:
  # Default: dependency profile, bundle version (next vNNN)
  powershell -ExecutionPolicy Bypass -File .\scripts\render.ps1

  # Specify profile explicitly (dependency | roots)
  powershell -ExecutionPolicy Bypass -File .\scripts\render.ps1 -Profile dependency
  powershell -ExecutionPolicy Bypass -File .\scripts\render.ps1 -Profile roots

  # Use explicit config file instead of profile
  powershell -ExecutionPolicy Bypass -File .\scripts\render.ps1 -Config config/visualize_dependency.toml

Parameters precedence:
  -Config overrides -Profile. If neither provided, defaults to -Profile dependency.

The script detects and uses the Windows Python 3.13 interpreter path. If you prefer a venv, edit $pythonExe below.
#>
param(
    [string]$Profile = "dependency",
    [string]$Config = "",
    [switch]$Verbose
)

# Resolve Python interpreter (edit this if you switch environments)
$pythonExe = "C:/Users/ASUS/AppData/Local/Programs/Python/Python313/python.exe"
if (!(Test-Path $pythonExe)) {
    Write-Host "[ERROR] Python interpreter not found: $pythonExe" -ForegroundColor Red
    exit 1
}

# Determine command arguments
$cmdArgs = @()
if ($Config) {
    $cmdArgs += "--config"; $cmdArgs += $Config
} else {
    $cmdArgs += "visualize"; $cmdArgs += "--profile"; $cmdArgs += $Profile
}

# Always include subcommand if --config used (order matters for argparse)
if ($Config) {
    $cmdArgs += "visualize"
    # When using explicit config, profile is ignored
} else {
    # Already added visualize above
}

# Add bundle-version to ensure two images produced
$cmdArgs += "--bundle-version"
# Add verbose if requested
if ($Verbose) { $cmdArgs += "--verbose" }

Write-Host "[render] Running visualize with arguments: $($cmdArgs -join ' ')" -ForegroundColor Cyan

# If show-config is desired before rendering (optional debug)
if ($Verbose) {
    if ($Config) {
        Write-Host "[render] Effective merged config (show-config)" -ForegroundColor Yellow
        & $pythonExe orchestrator.py --config $Config show-config --profile $Profile
    } else {
        Write-Host "[render] Effective merged config (show-config via profile)" -ForegroundColor Yellow
        & $pythonExe orchestrator.py show-config --profile $Profile
    }
}

# Execute visualize
& $pythonExe orchestrator.py $cmdArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "[render] visualize command failed (exit=$LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[render] Done." -ForegroundColor Green
