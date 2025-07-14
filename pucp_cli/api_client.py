# pucp_cli/api_client.py
"""
Cliente unificado para APIs del PUCP Cloud Orchestrator
"""

import requests
from typing import Optional, Dict, List
from rich.console import Console
from .config import Config

console = Console()

class APIException(Exception):
    """Excepción para errores de API"""
    pass

class PUCPAPIClient:
    """Cliente principal para todas las APIs"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        
        # Headers comunes
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PUCP-CLI/1.0.0'
        })
        
        # Agregar token si existe
        token = config.get_token()
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
            #self.session.headers['Authorization'] = f'Bearer {config.token}'
    
    def _request(self, method: str, service_url: str, endpoint: str, **kwargs) -> Dict:
        """Método base para hacer requests"""
        url = f"{service_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            
            if response.status_code == 401:
                raise APIException("Authentication required. Run 'pucp auth login'")
            elif response.status_code == 403:
                raise APIException("Insufficient permissions")
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    raise APIException(error_data.get('error', f'HTTP {response.status_code}'))
                except:
                    raise APIException(f'HTTP {response.status_code}: {response.text}')
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise APIException(f"Cannot connect to {service_url}")
        except requests.exceptions.Timeout:
            raise APIException(f"Request timeout to {service_url}")
    
     # === AUTH METHODS ===
    def login(self, username: str, password: str) -> Dict:
        """Login usuario"""
        return self._request('POST', self.config.auth_service, '/login', 
                           json={'username': username, 'password': password})
    
    def validate_token(self) -> Dict:
        """Valida token actual"""
        return self._request('POST', self.config.auth_service, '/validate')
    
    def set_token(self, token: str):
        """Establece token para requests"""
        self.session.headers['Authorization'] = f'Bearer {token}'
    
    # === SLICE METHODS ===
    def list_slices(self) -> list:
        """Lista todos los slices"""
        return self._request('GET', self.config.slice_service, '/slices')
    
    def get_slice(self, slice_id: str) -> Dict:
        """Obtiene detalles de un slice"""
        return self._request('GET', self.config.slice_service, f'/slices/{slice_id}')
    
    def create_slice(self, slice_data: Dict) -> Dict:
        """Crea nuevo slice"""
        return self._request('POST', self.config.slice_service, '/slices', json=slice_data)
    
    def deploy_slice(self, slice_id: str) -> Dict:
        """Despliega un slice"""
        return self._request('POST', self.config.slice_service, f'/slices/{slice_id}/deploy')
    
    def delete_slice(self, slice_id: str) -> Dict:
        """Elimina un slice"""
        return self._request('DELETE', self.config.slice_service, f'/slices/{slice_id}')
        
    # === SLICE SERVICE ===
    def slice_list(self) -> List[Dict]:
        """Lista todos los slices"""
        return self._request('GET', self.config.slice_service, '/slices')
    
    def slice_get(self, slice_id: str) -> Dict:
        """Obtiene detalles de un slice"""
        return self._request('GET', self.config.slice_service, f'/slices/{slice_id}')
    
    def slice_create(self, slice_data: Dict) -> Dict:
        """Crea nuevo slice"""
        return self._request('POST', self.config.slice_service, '/slices', 
                           json=slice_data)
    
    def slice_deploy(self, slice_id: str) -> Dict:
        """Despliega un slice"""
        return self._request('POST', self.config.slice_service, f'/slices/{slice_id}/deploy')
    
    def slice_delete(self, slice_id: str) -> Dict:
        """Elimina un slice"""
        return self._request('DELETE', self.config.slice_service, f'/slices/{slice_id}')
    
    # === RESOURCE SERVICE ===
    def resource_servers(self, infrastructure: str = None) -> List[Dict]:
        """Lista servidores"""
        params = {'infrastructure': infrastructure} if infrastructure else {}
        return self._request('GET', self.config.slice_service, '/resources', 
                           params=params)
    
    # === NETWORK SERVICE ===
    def network_vlans(self, infrastructure: str = None) -> List[Dict]:
        """Lista VLANs"""
        params = {'infrastructure': infrastructure} if infrastructure else {}
        return self._request('GET', self.config.network_service, '/api/vlans', 
                           params=params)
    
    # === HEALTH CHECKS ===
    def health_check_all(self) -> Dict:
        """Verifica estado de todos los servicios"""
        services = {
            'auth': self.config.auth_service,
            'slice': self.config.slice_service,
            'network': self.config.network_service,
            'image': self.config.image_service,
        }
        
        status = {}
        for name, url in services.items():
            try:
                self._request('GET', url, '/health')
                status[name] = '🟢 Online'
            except:
                status[name] = '🔴 Offline'
        
        return status