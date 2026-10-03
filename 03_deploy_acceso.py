"""
03_deploy_acceso.py — Fase 3: configura los switches de acceso (L2).
Reutiliza las funciones compartidas de comun.py.
"""
from comun import (
    cargar_inventario,
    enviar_config,
    construir_hostname,
    construir_vlans,
    construir_trunks,
)


def construir_puertos_acceso(datos_switch):
    """Puertos de acceso donde van los PCs (un puerto = una VLAN)."""
    comandos = []
    for grupo in datos_switch["puertos_acceso"]:
        # 'interfaces' es una LISTA: varios puertos en la misma VLAN
        for interface in grupo["interfaces"]:
            comandos.append(f"interface {interface}")
            comandos.append("switchport mode access")
            comandos.append(f"switchport access vlan {grupo['vlan']}")
            comandos.append("no shutdown")
            comandos.append("exit")
    return comandos


def main():
    inventario = cargar_inventario("inventario.yaml")
    username = inventario["global_vars"]["username"]
    password = inventario["global_vars"]["password"]

    for nombre, datos in inventario["switches_acceso"].items():
        comandos = []
        comandos += construir_hostname(datos)
        comandos += construir_vlans(inventario)
        comandos.append("spanning-tree mode rapid-pvst")  # coincide con la distribución
        comandos += construir_trunks(datos)
        comandos += construir_puertos_acceso(datos)
        enviar_config(nombre, datos, username, password, comandos)


if __name__ == "__main__":
    main()
