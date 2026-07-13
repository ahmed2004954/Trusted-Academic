# run_testsprite.ps1
# Automates starting the Django local server and running TestSprite CLI tests.

# 1. Start Django Server in background on port 8055
Write-Host "Starting Django local server on port 8055..." -ForegroundColor Cyan
$DjangoProcess = Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList "manage.py runserver 127.0.0.1:8055 --noreload" -NoNewWindow -PassThru

# 2. Wait for the server to be responsive
$Url = "http://127.0.0.1:8055/"
$MaxRetries = 20
$RetryCount = 0
$ServerReady = $false

Write-Host "Waiting for server to become responsive at $Url..." -ForegroundColor Cyan
while ($RetryCount -lt $MaxRetries) {
    try {
        $Response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($Response.StatusCode -eq 200) {
            $ServerReady = $true
            break
        }
    }
    catch {
        # Server not ready yet
    }
    Start-Sleep -Seconds 1
    $RetryCount++
}

if (-not $ServerReady) {
    Write-Error "Django server failed to start or respond on port 8055. Cleaning up..."
    Stop-Process -Id $DjangoProcess.Id -Force
    exit 1
}

Write-Host "Django server is online! Running TestSprite CLI tests..." -ForegroundColor Green

# 3. Run TestSprite tests
try {
    $env:API_KEY = "sk-user-WafQaNASmdDhmDU-6e-VHng17Mo19Z19p9JP9kav0A6SRqS8qsZQk5m8QGKi4GzxfBq9sCkmWbIB8UYSEvfqHyxDDCNoqbVAwCw0GGBTBED0BTzWfsV5d9nMArP1BIByp10"
    node C:\Users\h7304\AppData\Local\npm-cache\_npx\8ddf6bea01b2519d\node_modules\@testsprite\testsprite-mcp\dist\index.js generateCodeAndExecute
}
finally {
    # 4. Clean up Django process on exit
    Write-Host "Stopping Django server..." -ForegroundColor Cyan
    Stop-Process -Id $DjangoProcess.Id -Force
}
