"""
Configuración del CLI
"""
import os
import json
from pathlib import Path
from typing import Optional

class Config:
    """Gestión de configuración del CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".pucp-cli"
        self.config_file = self.config_dir / "config.json"
        self.token_file = self.config_dir / "token"
        
        # URLs por defecto
        self.auth_service = "http://localhost:5001"
        self.slice_service = "http://localhost:5002"
        self.template_service = "http://localhost:5003"
        self.network_service = "http://localhost:5004"
        self.image_service = "http://localhost:5005"
        
        # Cargar configuración existente
        self.load_config()
    
    def load_config(self):
        """Carga configuración desde archivo"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
            except Exception:
                pass  # Usar valores por defecto si hay error
    
    def save_config(self):
        """Guarda configuración actual"""
        self.config_dir.mkdir(exist_ok=True)
        
        data = {
            'auth_service': self.auth_service,
            'slice_service': self.slice_service,
            'template_service': self.template_service,
            'network_service': self.network_service,
            'image_service': self.image_service,
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_token(self) -> Optional[str]:
        """Obtiene token guardado"""
        if self.token_file.exists():
            try:
                return self.token_file.read_text().strip()
            except Exception:
                return None
        return None
    
    def save_token(self, token: str):
        """Guarda token"""
        self.config_dir.mkdir(exist_ok=True)
        self.token_file.write_text(token)
        # Permisos restrictivos para el token
        os.chmod(self.token_file, 0o600)
    
    def remove_token(self):
        """Elimina token guardado"""
        if self.token_file.exists():
            self.token_file.unlink()