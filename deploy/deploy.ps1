# Uploads the website to the server and installs it. Run from the repo folder on Windows:
#   powershell -ExecutionPolicy Bypass -File .\deploy\deploy.ps1
# Run it again after every change to publish the new version.
param(
    [string]$Server = "ubuntu@37.32.36.77",
    [string]$Key = "$env:USERPROFILE\.ssh\zebel-arvan-key"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Preparing upload folder on the server"
ssh -i $Key $Server "rm -rf ~/hormozraya-upload && mkdir -p ~/hormozraya-upload"

Write-Host "==> Uploading the website"
scp -i $Key -r "$root\public" "$root\deploy\nginx-arvan.conf" "$root\deploy\server-install.sh" "${Server}:~/hormozraya-upload/"

Write-Host "==> Installing on the server"
ssh -t -i $Key $Server "bash ~/hormozraya-upload/server-install.sh"
