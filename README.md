# PUCP CLI

![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![CLI](https://img.shields.io/badge/interface-CLI-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)

<img width="924" height="575" alt="Screenshot from 2025-09-07 01-17-33" src="https://github.com/user-attachments/assets/20712de5-a135-4304-8686-7ec86b861aab" />


**PUCP CLI** es una herramienta de línea de comandos diseñada para interactuar con el **Orquestador Cloud v3** desde el terminal. Permite gestionar recursos de cómputo, slices, imágenes, redes y plantillas de manera eficiente y automatizada.

## ✨ Características principales

- 🚀 **Gestión de slices** - Crear, listar, actualizar y eliminar entornos lógicos
- 🖼️ **Administración de imágenes** - Subir, descargar y gestionar imágenes de VM
- 🌐 **Configuración de redes** - Administrar topologías de red virtuales
- 📋 **Gestión de plantillas** - Desplegar y administrar plantillas predefinidas
- 🔐 **Autenticación integrada** - Sistema de login seguro con tokens JWT
- ⚙️ **Multi-backend** - Soporte para Linux clusters y OpenStack
- 📊 **Informes detallados** - Outputs en JSON, YAML o tabla
- 🔧 **Configuración flexible** - Perfiles y configuraciones personalizables

## 📋 Tabla de contenidos

- [Instalación](#-instalación)
- [Configuración inicial](#-configuración-inicial)
- [Uso básico](#-uso-básico)
- [Comandos disponibles](#-comandos-disponibles)
- [Ejemplos prácticos](#-ejemplos-prácticos)
- [Configuración avanzada](#-configuración-avanzada)
- [Troubleshooting](#-troubleshooting)
- [Contribución](#-contribución)

## 🚀 Instalación

### Requisitos del sistema

- **Python**: 3.10 o superior
- **pip**: Última versión
- **Acceso de red**: Al Orquestador Cloud v3
- **Sistema operativo**: Linux, macOS, Windows

### Método 1: Instalación desde repositorio

```bash
# Clonar el repositorio
git clone https://github.com/jchapo/pucp-cli.git
cd pucp-cli

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar CLI
pip install -e .
```

### Método 2: Instalación con pip (cuando esté disponible)

```bash
# Instalación directa
pip install pucp-cli

# Verificar instalación
pucp --version
```

### Verificar instalación

```bash
# Comprobar que el comando está disponible
pucp --help

# Verificar conectividad con el orquestador
pucp health check
```

## ⚙️ Configuración inicial

### Configurar endpoint del orquestador

```bash
# Configurar URL del API Gateway
pucp config set api-url https://your-orchestrator.example.com:8000

# Configurar timeout por defecto
pucp config set timeout 30

# Ver configuración actual
pucp config list
```

### Autenticación

```bash
# Iniciar sesión
pucp auth login --username admin --password your-password

# Verificar estado de autenticación
pucp auth status

# Renovar token
pucp auth refresh

# Cerrar sesión
pucp auth logout
```

## 🖥️ Uso básico

### Sintaxis general

```bash
pucp [OPCIONES_GLOBALES] <comando> [SUBCOMANDO] [OPCIONES] [ARGUMENTOS]
```

### Opciones globales

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--help, -h` | Mostrar ayuda | `pucp --help` |
| `--version` | Mostrar versión | `pucp --version` |
| `--verbose, -v` | Modo verboso | `pucp -v slice list` |
| `--format` | Formato de salida | `pucp --format json slice list` |
| `--config` | Archivo de configuración | `pucp --config ~/.pucp/config.yaml` |

### Formatos de salida

- **table** (por defecto): Tabla formateada para terminal
- **json**: Salida en formato JSON
- **yaml**: Salida en formato YAML
- **csv**: Valores separados por comas

## 📚 Comandos disponibles

### 🔐 Autenticación (`auth`)

```bash
# Gestionar autenticación
pucp auth login                    # Iniciar sesión
pucp auth logout                   # Cerrar sesión
pucp auth status                   # Ver estado
pucp auth refresh                  # Renovar token
```

### 🍰 Gestión de slices (`slice`)

```bash
# Operaciones con slices
pucp slice list                    # Listar todos los slices
pucp slice create --name my-slice  # Crear slice
pucp slice show <slice-id>         # Mostrar detalles
pucp slice delete <slice-id>       # Eliminar slice
pucp slice start <slice-id>        # Iniciar slice
pucp slice stop <slice-id>         # Detener slice
```

### 🖼️ Gestión de imágenes (`image`)

```bash
# Administrar imágenes
pucp image list                    # Listar imágenes
pucp image upload --file image.qcow2 --name ubuntu-22.04
pucp image download <image-id> --output ./image.qcow2
pucp image delete <image-id>       # Eliminar imagen
pucp image show <image-id>         # Ver detalles
```

### 🌐 Gestión de redes (`network`)

```bash
# Configurar redes
pucp network list                  # Listar redes
pucp network create --name net1 --cidr 192.168.1.0/24
pucp network show <network-id>     # Ver detalles
pucp network delete <network-id>   # Eliminar red
```

### 📋 Gestión de plantillas (`template`)

```bash
# Trabajar con plantillas
pucp template list                 # Listar plantillas
pucp template show <template-id>   # Ver plantilla
pucp template deploy <template-id> --slice <slice-id>
pucp template create --file template.yaml
```

### 🏥 Monitoreo y salud (`health`)

```bash
# Verificar estado del sistema
pucp health check                  # Estado general
pucp health services               # Estado de servicios
pucp health resources              # Uso de recursos
```

## 💡 Ejemplos prácticos

### Escenario 1: Crear y desplegar una topología web básica

```bash
# 1. Autenticarse
pucp auth login --username admin

# 2. Crear un nuevo slice
pucp slice create --name "web-app" --description "Aplicación web de prueba"

# 3. Listar plantillas disponibles
pucp template list --type web

# 4. Desplegar plantilla web básica
pucp template deploy web-basic --slice web-app --params '{"instances": 2}'

# 5. Verificar estado del slice
pucp slice show web-app --status

# 6. Ver logs de despliegue
pucp slice logs web-app --follow
```

### Escenario 2: Gestión de imágenes personalizadas

```bash
# 1. Subir imagen personalizada
pucp image upload \
  --file ./ubuntu-custom.qcow2 \
  --name "ubuntu-22.04-custom" \
  --description "Ubuntu con configuraciones PUCP"

# 2. Verificar la subida
pucp image list --filter "ubuntu-22.04-custom"

# 3. Usar la imagen en un slice
pucp slice create \
  --name "test-custom" \
  --image "ubuntu-22.04-custom" \
  --flavor "medium"
```

### Escenario 3: Configuración de red compleja

```bash
# 1. Crear red principal
pucp network create \
  --name "production-net" \
  --cidr "10.0.0.0/16" \
  --gateway "10.0.0.1"

# 2. Crear subred para aplicaciones
pucp network create \
  --name "app-subnet" \
  --cidr "10.0.1.0/24" \
  --parent "production-net"

# 3. Crear slice conectado a la red
pucp slice create \
  --name "app-server" \
  --network "app-subnet" \
  --ip "10.0.1.10"
```

## 🔧 Configuración avanzada

### Archivo de configuración

El CLI busca configuración en las siguientes ubicaciones:

1. `./pucp-cli.yaml` (directorio actual)
2. `~/.pucp/config.yaml` (directorio home)
3. `/etc/pucp-cli/config.yaml` (sistema)

### Ejemplo de configuración (`~/.pucp/config.yaml`)

```yaml
# Configuración del API Gateway
api:
  url: "https://orchestrator.pucp.edu.pe:8000"
  timeout: 30
  verify_ssl: true

# Credenciales por defecto
auth:
  username: "admin"
  save_token: true
  token_file: "~/.pucp/token"

# Configuración de salida
output:
  format: "table"
  color: true
  paging: true

# Perfiles de configuración
profiles:
  development:
    api:
      url: "http://localhost:8000"
      verify_ssl: false
  
  production:
    api:
      url: "https://prod-orchestrator.pucp.edu.pe:8000"
      timeout: 60

# Configuración de logging
logging:
  level: "INFO"
  file: "~/.pucp/pucp-cli.log"
  rotate: true
```

### Uso de perfiles

```bash
# Usar perfil específico
pucp --profile development slice list

# Cambiar perfil por defecto
pucp config set profile production

# Listar perfiles disponibles
pucp config profiles
```

### Variables de entorno

El CLI también respeta las siguientes variables de entorno:

```bash
export PUCP_API_URL="https://your-orchestrator.example.com:8000"
export PUCP_USERNAME="your-username"
export PUCP_PASSWORD="your-password"
export PUCP_FORMAT="json"
export PUCP_PROFILE="development"
```

## 🔍 Troubleshooting

### Problemas comunes y soluciones

#### Error de conexión

```bash
Error: Connection refused to https://orchestrator.example.com:8000

# Solución: Verificar conectividad
ping orchestrator.example.com
curl -k https://orchestrator.example.com:8000/health

# Verificar configuración
pucp config get api-url
```

#### Token expirado

```bash
Error: Authentication token has expired

# Solución: Renovar token
pucp auth refresh

# O iniciar sesión nuevamente
pucp auth login
```

#### Comando no encontrado

```bash
pucp: command not found

# Solución: Verificar instalación
pip list | grep pucp-cli

# Reinstalar si es necesario
pip install --force-reinstall pucp-cli
```

#### Problemas de SSL

```bash
Error: SSL certificate verification failed

# Solución temporal: Deshabilitar verificación SSL
pucp config set verify-ssl false

# Solución permanente: Agregar certificado al trust store
pucp config set ca-bundle /path/to/ca-bundle.crt
```

### Modo debug

```bash
# Habilitar logging detallado
pucp --verbose --debug slice create --name test

# Ver logs del CLI
tail -f ~/.pucp/pucp-cli.log

# Verificar configuración cargada
pucp config debug
```

### Comandos de diagnóstico

```bash
# Verificar conectividad completa
pucp health check --verbose

# Probar autenticación
pucp auth test

# Verificar configuración
pucp config validate

# Información del sistema
pucp info system
```

## 🧪 Testing

### Ejecutar tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Ejecutar suite completa
pytest

# Tests con cobertura
pytest --cov=pucp_cli --cov-report=html

# Tests específicos
pytest tests/test_auth.py -v
```

### Tests de integración

```bash
# Requiere un orquestador funcionando
pytest tests/integration/ --api-url http://localhost:8000
```

## 🤝 Contribución

¡Las contribuciones son bienvenidas! 

### Proceso de contribución

1. 🍴 **Fork** el repositorio
2. 🔀 **Crea una rama**: `git checkout -b feature/nueva-funcionalidad`
3. ✅ **Ejecuta los tests**: `pytest`
4. 📝 **Commit tus cambios**: `git commit -m 'Add: nueva funcionalidad'`
5. 📤 **Push**: `git push origin feature/nueva-funcionalidad`
6. 🔄 **Abre un Pull Request**

### Estándares de código

```bash
# Formatear código
black pucp_cli/
isort pucp_cli/

# Linting
flake8 pucp_cli/
pylint pucp_cli/

# Type checking
mypy pucp_cli/
```

### Estructura para nuevos comandos

```python
# pucp_cli/commands/nuevo_comando.py
import click
from pucp_cli.core import api_client
from pucp_cli.utils import output, auth

@click.group()
def nuevo_comando():
    """Descripción del nuevo comando."""
    pass

@nuevo_comando.command()
@click.option('--param', help='Parámetro de ejemplo')
@auth.require_auth
def subcomando(param):
    """Descripción del subcomando."""
    try:
        result = api_client.get(f'/nuevo-endpoint?param={param}')
        output.display(result, format='table')
    except Exception as e:
        output.error(f'Error: {e}')
        raise click.ClickException('Operación fallida')
```

## 📄 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces relacionados

- 🏠 **Orquestador Cloud v3**: [GitHub Repository](https://github.com/jchapo/Orquestador_Cloud_v3)
- 📖 **Documentación de API**: [API_DOCUMENTATION.md](https://github.com/jchapo/Orquestador_Cloud_v3/blob/main/API_DOCUMENTATION.md)
- 🎓 **PUCP**: [Pontificia Universidad Católica del Perú](https://www.pucp.edu.pe)

## 📞 Soporte y contacto

- 🐛 **Issues**: [GitHub Issues](https://github.com/jchapo/pucp-cli/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/jchapo/pucp-cli/discussions)
- 📧 **Email**: jchapo@pucp.edu.pe

## 🏆 Reconocimientos

- Desarrollado por el equipo de la **Pontificia Universidad Católica del Perú**
- Basado en la arquitectura de **Orquestador Cloud v3**
- Inspirado en las mejores prácticas de CLI tools como `kubectl`, `aws-cli` y `gcloud`

---

<div align="center">

**¿Te resultó útil? ¡Dale una ⭐ al repositorio!**

[Documentación](https://github.com/jchapo/pucp-cli/wiki) • [Contribuir](#-contribución) • [Reportar Bug](https://github.com/jchapo/pucp-cli/issues)

</div>
