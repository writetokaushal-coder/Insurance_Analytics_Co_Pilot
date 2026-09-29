$ErrorActionPreference = "Stop"

$exclude = @(
    "insurance-ai-copilot.*file:",
    "pywin32==",
    "pywinpty==",
    "win32-setctime==",
    "pyreadline3=="
)

pip freeze |
    Where-Object {
        $line = $_
        -not ($exclude | Where-Object { $line -match $_ })
    } |
    Set-Content requirements.lock.txt

Write-Host "Saved requirements.lock.txt"
Write-Host "Review the lock file for any other Windows-only package before Linux Docker build."
