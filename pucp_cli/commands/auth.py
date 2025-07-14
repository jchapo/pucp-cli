"""
Comandos de autenticación
"""
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from ..config import Config
from ..api_client import PUCPAPIClient, APIException

console = Console()

@click.group()
def auth():
    """🔐 Gestión de autenticación"""
    pass

@auth.command()
@click.option('--username', '-u', help='Nombre de usuario')
@click.option('--password', '-p', help='Contraseña')
def login(username, password):
    """Iniciar sesión en PUCP Cloud Orchestrator"""
    
    config = Config()
    client = PUCPAPIClient(config)
    
    # Solicitar credenciales si no se proporcionaron
    if not username:
        username = Prompt.ask("👤 Username")
    
    if not password:
        password = Prompt.ask("🔒 Password", password=True)
    
    try:
        console.print("🔄 Logging in...")
        
        # Hacer login
        response = client.login(username, password)
        token = response.get('token')
        user_info = response.get('user', {})
        
        if not token:
            console.print("❌ [red]Login failed: No token received[/red]")
            return
        
        # Guardar token
        config.save_token(token)
        
        # Mostrar éxito
        console.print("✅ [green]Login successful![/green]")
        
        # Mostrar info del usuario
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("👤 User:", user_info.get('username', username))
        table.add_row("🎭 Role:", user_info.get('role', 'unknown'))
        table.add_row("📧 Email:", user_info.get('email', 'N/A'))
        table.add_row("🎫 Token:", f"{token[:20]}..." if len(token) > 20 else token)
        
        console.print(table)
        console.print(f"\n💡 Token saved to: [dim]{config.token_file}[/dim]")
        
    except APIException as e:
        console.print(f"❌ [red]Login failed: {e}[/red]")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")

@auth.command()
def status():
    """Verificar estado de autenticación"""
    
    config = Config()
    token = config.get_token()
    
    if not token:
        console.print("❌ [red]Not authenticated[/red]")
        console.print("💡 Run 'pucp auth login' to authenticate")
        return
    
    try:
        client = PUCPAPIClient(config)
        response = client.validate_token()
        
        user_info = response.get('user', {})
        
        console.print("✅ [green]Authenticated[/green]")
        
        table = Table(show_header=False, box=None)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("👤 User:", user_info.get('username', 'unknown'))
        table.add_row("🎭 Role:", user_info.get('role', 'unknown'))
        table.add_row("🎫 Token:", f"{token[:20]}..." if len(token) > 20 else token)
        table.add_row("📂 Config:", str(config.config_dir))
        
        console.print(table)
        
    except APIException as e:
        console.print(f"❌ [red]Token validation failed: {e}[/red]")
        console.print("💡 Run 'pucp auth login' to re-authenticate")
    except Exception as e:
        console.print(f"❌ [red]Error checking status: {e}[/red]")

@auth.command()
def logout():
    """Cerrar sesión"""
    
    config = Config()
    
    if not config.get_token():
        console.print("ℹ️  [yellow]Already logged out[/yellow]")
        return
    
    try:
        config.remove_token()
        console.print("✅ [green]Logged out successfully[/green]")
        console.print("🔒 Token removed from local storage")
        
    except Exception as e:
        console.print(f"❌ [red]Error during logout: {e}[/red]")

@auth.command("config")  # ← Especificar nombre directamente
def config_cmd(endpoint):
    """Configurar endpoints de servicios"""
    
    config = Config()
    
    if endpoint:
        # Actualizar endpoint base
        config.auth_service = f"{endpoint.rstrip('/')}/auth"
        config.slice_service = f"{endpoint.rstrip('/')}/slice"
        config.template_service = f"{endpoint.rstrip('/')}/template"
        config.network_service = f"{endpoint.rstrip('/')}/network"
        config.image_service = f"{endpoint.rstrip('/')}/image"
        
        config.save_config()
        console.print(f"✅ [green]Configuration updated[/green]")
        console.print(f"🌐 Base endpoint: {endpoint}")
    else:
        # Mostrar configuración actual
        console.print("📋 [bold]Current Configuration[/bold]")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Service", style="cyan")
        table.add_column("URL", style="blue")
        
        table.add_row("Auth Service", config.auth_service)
        table.add_row("Slice Service", config.slice_service)
        table.add_row("Template Service", config.template_service)
        table.add_row("Network Service", config.network_service)
        table.add_row("Image Service", config.image_service)
        
        console.print(table)
        console.print(f"\n📂 Config file: [dim]{config.config_file}[/dim]")