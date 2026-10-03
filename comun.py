"""
comun.py — Funciones compartidas entre los scripts de despliegue (02, 03, 04, 05).
Principio DRY: cada función vive en UN solo lugar.
"""

import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


def cargar_inventario(ruta_archivo="inventario.yaml"):
    """Lee el YAML y devuelve un diccionario de Python."""
    try:
        with open(ruta_archivo, "r") as archivo:
            return yaml.safe_load(archivo)
    except FileNotFoundError:
        print(f"Error: no existe {ruta_archivo}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error de sintaxis YAML:\n{e}")
        exit(1)


def enviar_config(nombre_equipo, datos, username, password, comandos):
    """Conecta por SSH (OOB), hace enable, aplica config y guarda."""
    dispositivo = {
        "device_type": datos["device_type"],
        "host": datos["ip_mgmt"],
        "username": username,
        "password": password,
        "secret": password,  # <-- NECESARIO PARA EL COMANDO ENABLE
        "fast_cli": True,
        "session_log": f"debug_{nombre_equipo}.log",
    }
    print(f"→ {nombre_equipo} ({datos['ip_mgmt']})")
    try:
        conexion = ConnectHandler(**dispositivo)
        conexion.enable()
        conexion.send_config_set(comandos)
        conexion.save_config()
        conexion.disconnect()
        print("  ✓ OK: configuración aplicada y guardada")
    except NetmikoAuthenticationException:
        print(f"  ✗ Fallo de autenticación en {nombre_equipo}")
    except NetmikoTimeoutException:
        print(f"  ✗ Timeout: {nombre_equipo} no responde en {datos['ip_mgmt']}")
    except Exception as e:
        print(f"  ✗ Error en {nombre_equipo}: {e}")
    print("-" * 50)


def construir_hostname(datos_equipo):
    """Devuelve el comando de hostname."""
    return [f"hostname {datos_equipo['hostname']}"]


def construir_vlans(inventario):
    """Crea todas las VLANs del bloque global 'vlans'."""
    comandos = []
    for vlan_id, info in inventario["vlans"].items():
        comandos.append(f"vlan {vlan_id}")
        comandos.append(f"name {info['name']}")
        comandos.append("exit")
    return comandos


def construir_enlaces_ruteados(datos_equipo):
    """Enlaces L3 (ruteados) — LACP si tiene 'members', o enlace simple."""
    comandos = []
    for enlace in datos_equipo["enlaces_ruteados"]:
        if "members" in enlace:
            po_num = enlace["interface"].replace("Port-Channel", "")
            for miembro in enlace["members"]:
                comandos.append(f"interface {miembro}")
                comandos.append(f"channel-group {po_num} mode active")
                comandos.append("exit")
        comandos.append(f"interface {enlace['interface']}")
        if "descripcion" in enlace:
            comandos.append(f"description {enlace['descripcion']}")
        comandos.append("no switchport")  # volverlo puerto ruteado (L3)
        comandos.append(f"ip address {enlace['ip']}")
        comandos.append("no shutdown")
        comandos.append("exit")
    return comandos


def construir_trunks(datos_switch):
    """Trunks L2 (LACP si tiene 'members', o enlace simple)."""
    comandos = []
    for trunk in datos_switch["trunks"]:
        if "members" in trunk:
            po_num = trunk["interface"].replace("Port-Channel", "")
            for miembro in trunk["members"]:
                comandos.append(f"interface {miembro}")
                comandos.append(f"channel-group {po_num} mode active")
                comandos.append("exit")
        comandos.append(f"interface {trunk['interface']}")
        if "descripcion" in trunk:
            comandos.append(f"description {trunk['descripcion']}")
        comandos.append("switchport mode trunk")
        comandos.append(f"switchport trunk allowed vlan {trunk['vlans']}")
        comandos.append("no shutdown")
        comandos.append("exit")
    return comandos
