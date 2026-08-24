# generate_shots.ps1
# Sequentially generate 6 storyboard clips for "The Flower Shop at the Alley".
# Reads English prompts from script.md, calls Volcengine Ark Seedance 2.0
# text-to-video API, polls each task, and downloads the video.
# API key is read from $env:USERPROFILE\.ark-key and NEVER printed.
# NOTE: this file is pure ASCII. Chinese literals are built at runtime from
# Unicode code points so PowerShell 5.1 parses it regardless of file encoding.
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$scriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$mdPath      = Join-Path $scriptDir "script.md"
$clipsDir    = Join-Path $scriptDir "clips"
$keyPath     = Join-Path $env:USERPROFILE ".ark-key"
$baseUrl     = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
$model       = "doubao-seedance-2-0-mini-260615"
$pollSeconds = 20

# Chinese strings built at runtime (keep file ASCII)
$headingPattern = "^###\s+$([char]0x5206)$([char]0x955C)"                                  # 分镜
$promptCell     = "$([char]0x82F1)$([char]0x6587)$([char]0x63D0)$([char]0x793A)$([char]0x8BCD)"  # 英文提示词

# --- 1. Read API key (never printed) ---
if (-not (Test-Path $keyPath)) { throw "API key file not found: $keyPath" }
$apiKey = (Get-Content -Path $keyPath -Raw).Trim()
if ([string]::IsNullOrWhiteSpace($apiKey)) { throw "API key is empty" }

# --- 2. Extract the 6 English prompts from script.md ---
$lines = Get-Content -Path $mdPath -Encoding UTF8
$prompts = @()
$inShot = $false
foreach ($line in $lines) {
    if ($line -match $headingPattern) { $inShot = $true; continue }
    if ($inShot -and $line -match '^\|') {
        $cells = $line.Trim('|') -split '\|' | ForEach-Object { $_.Trim() }
        if ($cells.Count -ge 2 -and $cells[0] -eq $promptCell) {
            $prompts += $cells[1]
            $inShot = $false
        }
    }
}
if ($prompts.Count -ne 6) { throw "Expected 6 English prompts from script.md, got $($prompts.Count)" }
Write-Host "Parsed $($prompts.Count) prompts from script.md"

# --- 3. Prepare clips directory ---
New-Item -ItemType Directory -Force -Path $clipsDir | Out-Null

$headers = @{ Authorization = "Bearer $apiKey"; "Content-Type" = "application/json" }

# --- helpers ---
function Get-VideoUrl {
    param($task)
    $content = $task.content
    if ($content -is [System.Array]) {
        if ($content.Count -gt 0) { return $content[0].video_url }
    } elseif ($null -ne $content) {
        if ($content.video_url) { return $content.video_url }
    }
    if ($task.video_url) { return $task.video_url }
    return $null
}

# --- 4. Process 6 shots sequentially (no parallelism) ---
for ($i = 0; $i -lt 6; $i++) {
    $n = $i + 1
    $outFile = Join-Path $clipsDir ("shot{0}.mp4" -f $n)

    # resume support: skip shots already downloaded
    if ((Test-Path $outFile) -and ((Get-Item $outFile).Length -gt 0)) {
        Write-Host "[shot$n] clip already exists, skipping ($((Get-Item $outFile).Length) bytes)"
        continue
    }

    $prompt = $prompts[$i]
    Write-Host "[shot$n] creating task ..."

    $bodyObj = @{
        model          = $model
        content        = @(@{ type = "text"; text = $prompt })
        resolution     = "720p"
        ratio          = "16:9"
        duration       = 6
        generate_audio = $true
        watermark      = $false
    }
    $bodyJson = $bodyObj | ConvertTo-Json -Depth 5

    # create task with small retry loop
    $task = $null
    for ($try = 1; $try -le 3; $try++) {
        try {
            $task = Invoke-RestMethod -Method Post -Uri $baseUrl -Headers $headers -ContentType "application/json" -Body $bodyJson
            break
        } catch {
            if ($try -eq 3) { throw "Failed to create task for shot$n : $_" }
            Write-Host "[shot$n] create retry $try ..."
            Start-Sleep -Seconds 5
        }
    }

    $taskId = $task.id
    if (-not $taskId) { throw "No task id in create response: $($task | ConvertTo-Json -Depth 5 -Compress)" }
    Write-Host "[shot$n] task id: $taskId, polling every ${pollSeconds}s ..."

    # poll until succeeded / failed / cancelled (allow up to 45 min per shot)
    $deadline = (Get-Date).AddMinutes(45)
    $status = ""
    $videoUrl = $null
    while ((Get-Date) -lt $deadline) {
        Start-Sleep -Seconds $pollSeconds
        $q = Invoke-RestMethod -Method Get -Uri "$baseUrl/$taskId" -Headers $headers
        $status = $q.status
        Write-Host "[shot$n] status: $status"
        if ($status -eq "succeeded") {
            $videoUrl = Get-VideoUrl $q
            if (-not $videoUrl) { throw "Task succeeded but no video_url found for shot$n" }
            break
        }
        if ($status -eq "failed") { throw "Task failed for shot$n" }
        if ($status -eq "cancelled") { throw "Task cancelled for shot$n" }
    }
    if (-not $videoUrl) { throw "Polling timeout for shot$n, last status: $status" }

    # download (try without auth header first, then with)
    Write-Host "[shot$n] downloading video ..."
    try {
        Invoke-WebRequest -Uri $videoUrl -OutFile $outFile
    } catch {
        Invoke-WebRequest -Uri $videoUrl -Headers $headers -OutFile $outFile
    }
    $size = (Get-Item $outFile).Length
    if ($size -eq 0) { throw "Downloaded file is empty for shot$n" }
    Write-Host "[shot$n] done: $outFile ($size bytes)"
}

Write-Host "All 6 shots processed."
