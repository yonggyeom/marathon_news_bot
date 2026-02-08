# PowerShell script to create Windows Task Scheduler tasks
# Run this script as Administrator

$taskName = "MarathonNewsBot"
$scriptPath = "$PSScriptRoot\run.bat"
$workingDir = $PSScriptRoot

Write-Host "Creating Windows Task Scheduler tasks for Marathon News Bot..." -ForegroundColor Green
Write-Host "Task Name: $taskName"
Write-Host "Script: $scriptPath"
Write-Host "Working Directory: $workingDir"
Write-Host ""

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$taskName' already exists. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create action
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Create triggers (8 AM and 6 PM)
$trigger1 = New-ScheduledTaskTrigger -Daily -At "08:00AM"
$trigger2 = New-ScheduledTaskTrigger -Daily -At "06:00PM"

# Combine triggers
$triggers = @($trigger1, $trigger2)

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Create principal (run whether user is logged on or not)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $triggers `
        -Settings $settings `
        -Principal $principal `
        -Description "Marathon News Bot - Runs at 8 AM and 6 PM daily to check for new marathon events and sync to Notion"
    
    Write-Host ""
    Write-Host "✓ Task created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Schedule:" -ForegroundColor Cyan
    Write-Host "  - Daily at 8:00 AM"
    Write-Host "  - Daily at 6:00 PM"
    Write-Host ""
    Write-Host "To view the task:" -ForegroundColor Cyan
    Write-Host "  Open Task Scheduler and look for '$taskName'"
    Write-Host ""
    Write-Host "To run manually:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'"
    Write-Host ""
    Write-Host "To remove the task:" -ForegroundColor Cyan
    Write-Host "  Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false"
    
} catch {
    Write-Host ""
    Write-Host "✗ Failed to create task: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please make sure to run this script as Administrator" -ForegroundColor Yellow
}
