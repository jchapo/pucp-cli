"""
Comandos de gestión de recursos
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich.columns import Columns
from rich.bar import Bar
import time
from ..config import Config
from ..api_client import PUCPAPIClient, APIException

console = Console()

@click.group()
def resource():
    """📊 Gestión de recursos"""
    pass

@resource.command("servers")
@click.option('--infrastructure', help='Filtrar por infraestructura')
def list_servers(infrastructure):
    """Lista servidores y su estado"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        # Obtener recursos
        params = {}
        if infrastructure:
            params['infrastructure'] = infrastructure
        
        url = f"{config.slice_service}/resources"
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        response = client.session.get(url, timeout=30)
        if response.status_code != 200:
            raise APIException(f"HTTP {response.status_code}")
        
        data = response.json()
        servers = data.get('servers', [])
        
        if not servers:
            console.print("📋 [yellow]No servers found[/yellow]")
            return
        
        # Crear tabla
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Server", style="cyan", width=15)
        table.add_column("Infrastructure", style="blue", width=12)
        table.add_column("Zone", style="green", width=15)
        table.add_column("CPU Usage", width=20)
        table.add_column("RAM Usage", width=20)
        table.add_column("Status", width=10)
        
        for server in servers:
            # CPU bar
            cpu_used = server.get('used_vcpus', 0)
            cpu_total = server.get('total_vcpus', 1)
            cpu_percent = (cpu_used / cpu_total) * 100 if cpu_total > 0 else 0
            cpu_bar = f"[cyan]{'█' * int(cpu_percent/5)}[/cyan]{'░' * (20-int(cpu_percent/5))} {cpu_used}/{cpu_total}"
            
            # RAM bar
            ram_used = server.get('used_ram', 0)
            ram_total = server.get('total_ram', 1)
            ram_percent = (ram_used / ram_total) * 100 if ram_total > 0 else 0
            ram_gb_used = ram_used / 1024
            ram_gb_total = ram_total / 1024
            ram_bar = f"[yellow]{'█' * int(ram_percent/5)}[/yellow]{'░' * (20-int(ram_percent/5))} {ram_gb_used:.1f}/{ram_gb_total:.1f}GB"
            
            # Status
            status = server.get('status', 'unknown')
            if status == 'active':
                status_display = "[green]🟢 UP[/green]"
            else:
                status_display = "[red]🔴 DOWN[/red]"
            
            # Infraestructura con emoji
            infra = server.get('infrastructure', 'unknown')
            if infra == 'linux':
                infra_display = "🐧 linux"
            elif infra == 'openstack':
                infra_display = "☁️ openstack"
            else:
                infra_display = infra
            
            table.add_row(
                server.get('hostname', 'N/A'),
                infra_display,
                server.get('zone_name', 'N/A'),
                cpu_bar,
                ram_bar,
                status_display
            )
        
        console.print(f"\n📊 [bold]PUCP Servers ({len(servers)} found)[/bold]\n")
        console.print(table)
        console.print()
        
        # Estadísticas globales
        stats = data.get('statistics', {})
        if stats:
            console.print("🔢 [bold]Resource Statistics[/bold]")
            for infra, stat in stats.items():
                cpu_util = stat.get('cpu_utilization', 0)
                ram_util = stat.get('ram_utilization', 0)
                console.print(f"  {infra}: CPU {cpu_util:.1f}% | RAM {ram_util:.1f}% | {stat.get('active_servers', 0)}/{stat.get('total_servers', 0)} servers")
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@resource.command("dashboard")
@click.option('--refresh', default=5, help='Intervalo de refresco en segundos')
def dashboard(refresh):
    """Dashboard interactivo de recursos"""
    
    console.print("📊 [bold]PUCP Resource Dashboard[/bold]")
    console.print("Press Ctrl+C to exit\n")
    
    try:
        while True:
            with console.screen():
                config = Config()
                client = PUCPAPIClient(config)
                
                try:
                    # Obtener datos
                    response = client.session.get(f"{config.slice_service}/resources", timeout=10)
                    data = response.json()
                    
                    servers = data.get('servers', [])
                    stats = data.get('statistics', {})
                    
                    # Header
                    console.print("📊 [bold blue]PUCP Cloud Orchestrator - Resource Dashboard[/bold blue]")
                    console.print(f"🔄 Auto-refresh: {refresh}s | {time.strftime('%H:%M:%S')}\n")
                    
                    # Statistics cards
                    cards = []
                    for infra, stat in stats.items():
                        cpu_util = stat.get('cpu_utilization', 0)
                        ram_util = stat.get('ram_utilization', 0)
                        active = stat.get('active_servers', 0)
                        total = stat.get('total_servers', 0)
                        
                        status_emoji = "🟢" if active == total else "🟡" if active > 0 else "🔴"
                        
                        card_content = f"""[bold]{infra.title()}[/bold]
{status_emoji} {active}/{total} servers
🔧 CPU: {cpu_util:.1f}%
🧠 RAM: {ram_util:.1f}%"""
                        
                        cards.append(Panel(card_content, border_style="blue"))
                    
                    if cards:
                        console.print(Columns(cards))
                        console.print()
                    
                    # Server table
                    if servers:
                        table = Table(show_header=True, header_style="bold magenta", title="Server Status")
                        table.add_column("Server", style="cyan")
                        table.add_column("Infra", style="blue")
                        table.add_column("CPU", width=15)
                        table.add_column("RAM", width=15)
                        table.add_column("VMs", style="green")
                        table.add_column("Status")
                        
                        for server in servers[:10]:  # Mostrar solo primeros 10
                            cpu_used = server.get('used_vcpus', 0)
                            cpu_total = server.get('total_vcpus', 1)
                            cpu_percent = (cpu_used / cpu_total) * 100 if cpu_total > 0 else 0
                            
                            ram_used = server.get('used_ram', 0) / 1024
                            ram_total = server.get('total_ram', 1) / 1024
                            ram_percent = (ram_used * 1024 / server.get('total_ram', 1)) * 100 if server.get('total_ram', 1) > 0 else 0
                            
                            status = "🟢" if server.get('status') == 'active' else "🔴"
                            
                            table.add_row(
                                server.get('hostname', 'N/A'),
                                "🐧" if server.get('infrastructure') == 'linux' else "☁️",
                                f"{cpu_percent:.0f}% ({cpu_used}/{cpu_total})",
                                f"{ram_percent:.0f}% ({ram_used:.1f}G)",
                                str(server.get('active_vms', 0)),
                                status
                            )
                        
                        console.print(table)
                    
                    console.print(f"\n[dim]Press Ctrl+C to exit | Refreshing every {refresh}s[/dim]")
                    
                except Exception as e:
                    console.print(f"❌ [red]Error fetching data: {e}[/red]")
                
                time.sleep(refresh)
                
    except KeyboardInterrupt:
        console.print("\n👋 Dashboard closed")

@resource.command("flavors")
def list_flavors():
    """Lista flavors disponibles para VMs"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        response = client.session.get(f"{config.slice_service}/resources", timeout=10)
        data = response.json()
        
        flavors = data.get('vm_flavors', {})
        
        if not flavors:
            console.print("📋 [yellow]No flavors found[/yellow]")
            return
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Flavor", style="cyan", width=10)
        table.add_column("vCPUs", style="green", width=8, justify="center")
        table.add_column("RAM (MB)", style="yellow", width=10, justify="center")
        table.add_column("Disk (GB)", style="blue", width=10, justify="center")
        table.add_column("Description", style="dim")
        
        for name, specs in flavors.items():
            table.add_row(
                name,
                str(specs.get('vcpus', 'N/A')),
                str(specs.get('ram', 'N/A')),
                str(specs.get('disk', 'N/A')),
                f"Small instance" if name == 'small' else f"{name.title()} instance"
            )
        
        console.print(f"\n⚙️  [bold]Available VM Flavors[/bold]\n")
        console.print(table)
        console.print()
        
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")