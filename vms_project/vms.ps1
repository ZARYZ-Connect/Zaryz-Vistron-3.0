param (
    [Parameter(Mandatory=$false, Position=0)]
    [string]$Action,

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

# Configuration
$ContainerName = "vistron_saas"
$ComposeFile = "../docker-compose.yml"

function Show-Help {
    Write-Host "`n🚀 Vistron Docker Terminal Management" -ForegroundColor Cyan
    Write-Host "--------------------------------------"
    Write-Host "Usage: ./vms.ps1 <action> [args]`n"
    Write-Host "Actions:"
    Write-Host "  up              - Build and start all services"
    Write-Host "  down            - Stop and remove containers"
    Write-Host "  restart         - Restart all services"
    Write-Host "  logs            - View real-time container logs"
    Write-Host "  shell           - Open a bash terminal inside the app container"
    Write-Host "  manage [cmd]    - Run a Django manage.py command"
    Write-Host "  migrate         - Shortcut to run database migrations"
    Write-Host "  superuser       - Shortcut to create a Django superuser"
    Write-Host "  ps              - List running containers"
    Write-Host "  help            - Show this help message"
    Write-Host ""
}

if (-not $Action) {
    Show-Help
    return
}

switch ($Action) {
    "up" {
        docker-compose -f $ComposeFile up --build -d
    }
    "down" {
        docker-compose -f $ComposeFile down
    }
    "restart" {
        docker-compose -f $ComposeFile restart
    }
    "logs" {
        docker-compose -f $ComposeFile logs -f --tail 100
    }
    "shell" {
        docker exec -it $ContainerName /bin/bash
    }
    "manage" {
        docker exec -it $ContainerName python manage.py $RemainingArgs
    }
    "migrate" {
        docker exec -it $ContainerName python manage.py migrate
    }
    "superuser" {
        docker exec -it $ContainerName python manage.py createsuperuser
    }
    "ps" {
        docker-compose -f $ComposeFile ps
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help
    }
}
