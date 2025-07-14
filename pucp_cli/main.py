#!/usr/bin/env python3hola
import click
from rich.console import Console
from rich.table import Table
import requests

# Importar comandos
from .commands.auth import auth
from .commands.slice import slice
from .commands.resource import resource


console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🎓 PUCP Cloud Orchestrator CLI
    
    Gestiona slices, recursos y redes del cluster PUCP.
    """
    pass

# Agregar grupo de comandos
cli.add_command(auth)
cli.add_command(slice)
cli.add_command(resource)


@cli.command()
def logo():
    """Muestra el logo de PUCP"""
    logo_text = """
[bold red]
 ███████╗ ██╗   ██╗  ██████╗ ██████╗ 
 ██╔══██║ ██║   ██║ ██╔════╝ ██╔══██╗
 ███████║ ██║   ██║ ██║      ██████╔╝
 ██╔════╝ ██║   ██║ ██║      ██╔═══╝ 
 ██║      ╚██████╔╝ ╚██████╗ ██║     
 ╚═╝       ╚═════╝   ╚═════╝ ╚═╝     
[/bold red]
[bold yellow]Cloud Orchestrator CLI v1.0.0[/bold yellow]
"""
    console.print(logo_text)

@cli.command()
def status():
    """Verifica estado de servicios"""
    services = {
        'Auth Service': 'http://localhost:5001/health',
        'Slice Service': 'http://localhost:5002/health', 
        'Network Service': 'http://localhost:5004/health',
        'Image Service': 'http://localhost:5005/health',
        'Template Service': 'http://localhost:5003/health'
    }
    
    console.print("\n[bold]🔍 Checking PUCP Services...[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", width=20)
    table.add_column("URL", style="blue", width=30)
    table.add_column("Status", width=15)
    table.add_column("Response", width=20)
    
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                status = "[green]✅ Online[/green]"
                resp_text = "OK"
            else:
                status = f"[yellow]⚠️ HTTP {response.status_code}[/yellow]"
                resp_text = f"Error {response.status_code}"
        except requests.exceptions.ConnectionError:
            status = "[red]❌ Offline[/red]"
            resp_text = "Connection refused"
        except requests.exceptions.Timeout:
            status = "[red]❌ Timeout[/red]"
            resp_text = "Timeout (5s)"
        except Exception as e:
            status = "[red]❌ Error[/red]"
            resp_text = str(e)[:20]
        
        table.add_row(name, url, status, resp_text)
    
    console.print(table)
    console.print()

if __name__ == "__main__":
    cli()