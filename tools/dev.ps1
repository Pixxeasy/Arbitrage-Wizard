# ArbitrageWizard Development Script (PowerShell)

Write-Host "🚀 Starting ArbitrageWizard development environment..." -ForegroundColor Green

# Function to handle cleanup
$jobs = @()

try {
    Write-Host "📦 Starting shared packages in watch mode..." -ForegroundColor Yellow
    
    # Start shared-types in background
    $sharedTypes = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\packages\shared-types'; npm run dev" -PassThru
    $jobs += $sharedTypes
    
    # Start shared-utils in background  
    $sharedUtils = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\packages\shared-utils'; npm run dev" -PassThru
    $jobs += $sharedUtils

    Write-Host "🖥️  Starting frontend development server..." -ForegroundColor Yellow
    $frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\apps\frontend'; npm run dev" -PassThru
    $jobs += $frontend

    Write-Host "🐍 Starting backend development server..." -ForegroundColor Yellow  
    $backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\apps\backend-api'; python -m uvicorn app.main:app --reload --port 8000" -PassThru
    $jobs += $backend

    Write-Host ""
    Write-Host "✅ All services started!" -ForegroundColor Green
    Write-Host "📱 Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "🔧 Backend: http://localhost:8000" -ForegroundColor Cyan  
    Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop all services or close individual PowerShell windows" -ForegroundColor Yellow

    # Wait for user interrupt
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    catch [System.Management.Automation.PipelineStoppedException] {
        Write-Host "🛑 Shutting down services..." -ForegroundColor Red
    }
}
finally {
    # Cleanup: Kill all started processes
    foreach ($job in $jobs) {
        if (!$job.HasExited) {
            try {
                $job.Kill()
                Write-Host "Stopped process $($job.Id)" -ForegroundColor Gray
            }
            catch {
                # Process might have already exited
            }
        }
    }
}