"""
Comandos de gestión de slices
"""
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
import time
import json
from typing import Dict, List
from ..config import Config
from ..api_client import PUCPAPIClient, APIException

console = Console()

@click.group()
def slice():
    """🔄 Gestión de slices"""
    pass

@slice.command("list")
@click.option('--status', help='Filtrar por estado (active, error, stopped, etc.)')
@click.option('--infrastructure', help='Filtrar por infraestructura (linux, openstack)')
@click.option('--json', 'output_json', is_flag=True, help='Salida en formato JSON')
def list_slices(status, infrastructure, output_json):
    """Lista todos los slices"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        slices = client.list_slices()
        
        # Aplicar filtros
        if status:
            slices = [s for s in slices if s.get('status') == status]
        if infrastructure:
            slices = [s for s in slices if s.get('infrastructure') == infrastructure]
        
        if output_json:
            console.print(json.dumps(slices, indent=2))
            return
        
        if not slices:
            console.print("📋 [yellow]No slices found[/yellow]")
            if status or infrastructure:
                console.print(f"   Filters: status={status}, infrastructure={infrastructure}")
            return
        
        # Crear tabla
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Status", width=12)
        table.add_column("Infrastructure", style="blue", width=12)
        table.add_column("Nodes", style="green", width=8, justify="center")
        table.add_column("Networks", style="yellow", width=8, justify="center")
        table.add_column("Created", style="dim", width=15)
        table.add_column("Actions", width=20)
        
        for slice_data in slices:
            # Status con color
            status_text = slice_data.get('status', 'unknown')
            if status_text == 'active':
                status_display = "[green]✅ active[/green]"
            elif status_text == 'error':
                status_display = "[red]❌ error[/red]"
            elif status_text == 'stopped':
                status_display = "[yellow]⏸️ stopped[/yellow]"
            elif status_text in ['deploying', 'validating']:
                status_display = "[blue]🔄 deploy.[/blue]"
            else:
                status_display = f"[dim]{status_text}[/dim]"
            
            # Emoji para infraestructura
            infra = slice_data.get('infrastructure', 'unknown')
            if infra == 'linux':
                infra_display = "🐧 linux"
            elif infra == 'openstack':
                infra_display = "☁️ openstack"
            else:
                infra_display = infra
            
            # Acciones según estado
            actions = []
            if status_text == 'active':
                actions = ["[dim]view|stop|restart[/dim]"]
            elif status_text == 'stopped':
                actions = ["[dim]view|start|delete[/dim]"]
            elif status_text == 'error':
                actions = ["[dim]view|retry|delete[/dim]"]
            elif status_text == 'draft':
                actions = ["[dim]deploy|edit|delete[/dim]"]
            else:
                actions = ["[dim]view[/dim]"]
            
            # Obtener fecha de creación formateada
            created = slice_data.get('created_at', '')
            if created:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    created_display = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    created_display = created[:16]
            else:
                created_display = 'N/A'
            
            table.add_row(
                slice_data.get('name', 'N/A'),
                status_display,
                infra_display,
                str(slice_data.get('node_count', 0)),
                str(slice_data.get('network_count', 0)),
                created_display,
                "".join(actions)
            )
        
        console.print(f"\n📋 [bold]PUCP Slices ({len(slices)} found)[/bold]\n")
        console.print(table)
        console.print()
        
        # Stats summary
        stats = {}
        for slice_data in slices:
            status = slice_data.get('status', 'unknown')
            stats[status] = stats.get(status, 0) + 1
        
        stats_text = " | ".join([f"{k}: {v}" for k, v in stats.items()])
        console.print(f"📊 [dim]{stats_text}[/dim]")
        console.print(f"💡 Use 'pucp slice show <name>' for details")
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@slice.command("show")
@click.argument('slice_name')
@click.option('--json', 'output_json', is_flag=True, help='Salida en formato JSON')
def show_slice(slice_name, output_json):
    """Muestra detalles de un slice"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        # Buscar slice por nombre o ID
        slices = client.list_slices()
        slice_data = None
        
        for s in slices:
            if s.get('name') == slice_name or s.get('id') == slice_name:
                slice_data = s
                break
        
        if not slice_data:
            console.print(f"❌ [red]Slice '{slice_name}' not found[/red]")
            return
        
        # Obtener detalles completos
        slice_details = client.get_slice(slice_data['id'])
        
        if output_json:
            console.print(json.dumps(slice_details, indent=2))
            return
        
        # Mostrar información detallada
        console.print(f"\n🔍 [bold]Slice Details: {slice_details.get('name')}[/bold]\n")
        
        # Panel de información básica
        info_text = f"""[cyan]ID:[/cyan] {slice_details.get('id', 'N/A')}
[cyan]Name:[/cyan] {slice_details.get('name', 'N/A')}
[cyan]Description:[/cyan] {slice_details.get('description', 'N/A')}
[cyan]Infrastructure:[/cyan] {slice_details.get('infrastructure', 'N/A')}
[cyan]Status:[/cyan] {slice_details.get('status', 'N/A')}
[cyan]Created:[/cyan] {slice_details.get('created_at', 'N/A')}"""
        
        console.print(Panel(info_text, title="📋 Basic Info", border_style="blue"))
        
        # Tabla de nodos
        nodes = slice_details.get('nodes', [])
        if nodes:
            nodes_table = Table(show_header=True, header_style="bold green")
            nodes_table.add_column("Node", style="cyan")
            nodes_table.add_column("Image", style="blue")
            nodes_table.add_column("Flavor", style="yellow")
            nodes_table.add_column("Status", style="green")
            nodes_table.add_column("IP Address", style="magenta")
            nodes_table.add_column("Server", style="dim")
            
            for node in nodes:
                nodes_table.add_row(
                    node.get('name', 'N/A'),
                    node.get('image', 'N/A'),
                    node.get('flavor', 'N/A'),
                    node.get('status', 'N/A'),
                    node.get('ip_address', 'N/A'),
                    node.get('assigned_host', 'N/A')
                )
            
            console.print(nodes_table)
        
        # Tabla de redes
        networks = slice_details.get('networks', [])
        if networks:
            console.print()
            networks_table = Table(show_header=True, header_style="bold yellow")
            networks_table.add_column("Network", style="cyan")
            networks_table.add_column("CIDR", style="blue")
            networks_table.add_column("VLAN", style="green")
            networks_table.add_column("Type", style="magenta")
            networks_table.add_column("Internet", style="red")
            
            for network in networks:
                networks_table.add_row(
                    network.get('name', 'N/A'),
                    network.get('cidr', 'N/A'),
                    str(network.get('vlan_id', 'N/A')),
                    network.get('network_type', 'data'),
                    "✅" if network.get('internet_access') else "❌"
                )
            
            console.print(networks_table)
        
        console.print()
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@slice.command("deploy")
@click.argument('slice_name')
@click.option('--watch', is_flag=True, help='Monitorear progreso del deployment')
def deploy_slice(slice_name, watch):
    """Despliega un slice"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        # Buscar slice
        slices = client.list_slices()
        slice_data = None
        
        for s in slices:
            if s.get('name') == slice_name or s.get('id') == slice_name:
                slice_data = s
                break
        
        if not slice_data:
            console.print(f"❌ [red]Slice '{slice_name}' not found[/red]")
            return
        
        slice_id = slice_data['id']
        
        # Verificar estado
        if slice_data.get('status') not in ['draft', 'error', 'stopped']:
            console.print(f"❌ [red]Cannot deploy slice in status: {slice_data.get('status')}[/red]")
            return
        
        console.print(f"🚀 [bold]Deploying slice '{slice_name}'...[/bold]")
        
        if watch:
            # Deployment con progreso
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Starting deployment...", total=None)
                
                # Iniciar deployment
                response = client._request('POST', client.config.slice_service, f'/slices/{slice_id}/deploy')
                
                progress.update(task, description="Deployment initiated...")
                time.sleep(2)
                
                # Monitorear progreso
                for i in range(30):  # Max 5 minutos
                    time.sleep(10)
                    
                    # Obtener estado actual
                    current_slice = client.get_slice(slice_id)
                    status = current_slice.get('status')
                    
                    if status == 'active':
                        progress.update(task, description="✅ Deployment completed!")
                        break
                    elif status == 'error':
                        progress.update(task, description="❌ Deployment failed!")
                        break
                    elif status == 'deploying':
                        progress.update(task, description=f"🔄 Deploying... ({i*10}s)")
                    else:
                        progress.update(task, description=f"Status: {status}")
        else:
            # Deployment simple
            response = client._request('POST', client.config.slice_service, f'/slices/{slice_id}/deploy')
        
        # Mostrar resultado
        if 'error' in response:
            console.print(f"❌ [red]Deployment failed: {response['error']}[/red]")
        else:
            console.print(f"✅ [green]Deployment request sent successfully![/green]")
            console.print(f"💡 Use 'pucp slice show {slice_name}' to check status")
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@slice.command("delete")
@click.argument('slice_name')
@click.option('--force', is_flag=True, help='Forzar eliminación sin confirmación')
def delete_slice(slice_name, force):
    """Elimina un slice"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        # Buscar slice
        slices = client.list_slices()
        slice_data = None
        
        for s in slices:
            if s.get('name') == slice_name or s.get('id') == slice_name:
                slice_data = s
                break
        
        if not slice_data:
            console.print(f"❌ [red]Slice '{slice_name}' not found[/red]")
            return
        
        slice_id = slice_data['id']
        
        # Confirmación
        if not force:
            console.print(f"⚠️  [yellow]About to delete slice '{slice_name}'[/yellow]")
            console.print(f"   Status: {slice_data.get('status')}")
            console.print(f"   Infrastructure: {slice_data.get('infrastructure')}")
            console.print(f"   Nodes: {slice_data.get('node_count', 0)}")
            
            if not Confirm.ask("🗑️  Are you sure you want to delete this slice?"):
                console.print("❌ Deletion cancelled")
                return
        
        console.print(f"🗑️  [bold]Deleting slice '{slice_name}'...[/bold]")
        
        response = client._request('DELETE', client.config.slice_service, f'/slices/{slice_id}')
        
        console.print(f"✅ [green]Slice '{slice_name}' deleted successfully![/green]")
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")

@slice.command("create")
@click.option('--name', prompt='Slice name', help='Nombre del slice')
@click.option('--infrastructure', type=click.Choice(['linux', 'openstack']), prompt='Infrastructure', help='Infraestructura')
@click.option('--interactive', is_flag=True, help='Modo interactivo')
def create_slice(name, infrastructure, interactive):
    """Crea un nuevo slice"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    try:
        if interactive:
            console.print("🎯 [bold]Interactive Slice Creation[/bold]")
            console.print("This wizard will guide you through creating a new slice\n")
            
            # Datos básicos
            name = Prompt.ask("📝 Slice name", default=name)
            description = Prompt.ask("📄 Description (optional)", default="")
            
            # Infraestructura
            if not infrastructure:
                infrastructure = Prompt.ask("🏗️  Infrastructure", choices=['linux', 'openstack'], default='linux')
            
            # Template básico
            template_choice = Prompt.ask(
                "📐 Topology template", 
                choices=['linear', 'mesh', 'custom'], 
                default='linear'
            )
            
            if template_choice == 'custom':
                console.print("❌ [red]Custom templates not implemented yet[/red]")
                return
            
            # Número de nodos
            node_count = int(Prompt.ask("🖥️  Number of nodes", default="3"))
            
            # Crear configuración básica
            slice_config = {
                'name': name,
                'description': description,
                'infrastructure': infrastructure,
                'nodes': [],
                'networks': [
                    {
                        'name': 'mgmt-net',
                        'cidr': '192.168.201.0/24',
                        'network_type': 'management'
                    },
                    {
                        'name': 'data-net', 
                        'cidr': '10.60.1.0/24',
                        'network_type': 'data'
                    }
                ]
            }
            
            # Crear nodos
            for i in range(node_count):
                node = {
                    'name': f'{template_choice}-node-{i+1}',
                    'image': 'ubuntu-20.04',
                    'flavor': 'small'
                }
                slice_config['nodes'].append(node)
            
        else:
            # Modo no interactivo - configuración mínima
            slice_config = {
                'name': name,
                'description': f'Slice created via CLI for {infrastructure}',
                'infrastructure': infrastructure,
                'nodes': [
                    {
                        'name': f'{name}-node-1',
                        'image': 'ubuntu-20.04',
                        'flavor': 'small'
                    }
                ],
                'networks': [
                    {
                        'name': 'data-net',
                        'cidr': '10.60.1.0/24',
                        'network_type': 'data'
                    }
                ]
            }
        
        console.print(f"\n🏗️  [bold]Creating slice '{name}'...[/bold]")
        
        response = client._request('POST', client.config.slice_service, '/slices', json=slice_config)
        
        console.print(f"✅ [green]Slice '{name}' created successfully![/green]")
        console.print(f"🆔 Slice ID: {response.get('id')}")
        console.print(f"💡 Use 'pucp slice deploy {name}' to deploy it")
        
    except APIException as e:
        console.print(f"❌ [red]API Error: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")