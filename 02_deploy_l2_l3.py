"""
02_deploy_l2_l3.py — Fase 2: configura los switches de distribución (L3).
Reutiliza las funciones compartidas de comun.py.
"""

from comun import (
    cargar_inventario,
    enviar_config,
    construir_hostname,
    construir_vlans,
    construir_enlaces_ruteados,
    construir_trunks,
)


def construir_svis(datos_switch):
    """SVIs + VRRP (gateways de las VLANs)."""
    comandos = ["ip routing"]
    for svi in datos_switch["svis"]:
        comandos.append(f"interface Vlan{svi['vlan']}")
        comandos.append(f"ip address {svi['ip']}")
        comandos.append(f"vrrp {svi['vrrp_group']} priority {svi['priority']}")
        comandos.append(f"vrrp {svi['vrrp_group']} ipv4 {svi['vrrp_ip']}")
        comandos.append(f"vrrp {svi['vrrp_group']} preempt")
        comandos.append("no shutdown")
        comandos.append("exit")
    return comandos


def construir_stp(datos_switch, vlans):
    """Rapid-PVST+ con prioridad según el rol (root primary/secondary)."""
    comandos = ["spanning-tree mode rapid-pvst"]
    prioridad = "4096" if datos_switch["stp_role"] == "root_primary" else "8192"
    for vlan_id in vlans:
        comandos.append(f"spanning-tree vlan {vlan_id} priority {prioridad}")
    return comandos


def main():
    inventario = cargar_inventario("inventario.yaml")
    username = inventario["global_vars"]["username"]
    password = inventario["global_vars"]["password"]

    for nombre, datos in inventario["switches_distribucion"].items():
        comandos = []
        comandos += construir_hostname(datos)
        comandos += construir_vlans(inventario)
        comandos += construir_enlaces_ruteados(datos)
        comandos += construir_trunks(datos)
        comandos += construir_svis(datos)
        comandos += construir_stp(datos, inventario["vlans"])
        enviar_config(nombre, datos, username, password, comandos)


if __name__ == "__main__":
    main()
