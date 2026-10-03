"""
05_deploy_router.py — Configura el router de borde (R1).
hostname + IPs de enlaces internos + WAN (DHCP hacia Cloud1).
"""

from comun import (
    cargar_inventario,
    enviar_config,
    construir_hostname,
    construir_enlaces_ruteados,
)


def construir_wan(datos_router):
    """WAN: interfaz hacia Cloud1 con IP por DHCP y reglas NAT."""
    comandos = ["ip routing"]  # Habilita el ruteo global en el equipo
    wan = datos_router.get("wan", {})
    if wan:
        # Configuración de la interfaz física WAN
        comandos.append(f"interface {wan['interface']}")
        comandos.append("no switchport")
        comandos.append("ip address dhcp")
        comandos.append("no shutdown")
        comandos.append("exit")

        # Crear ACL para permitir que las subredes internas salgan a Internet
        comandos.append("ip access-list standard NAT-ACL")
        comandos.append("permit 10.1.0.0/16")
        comandos.append("exit")

        # Aplicar NAT Overload (PAT) a la interfaz WAN
        comandos.append(
            f"ip nat source dynamic access-list NAT-ACL interface {wan['interface']} overload"
        )

    return comandos


def main():
    inventario = cargar_inventario("inventario.yaml")
    username = inventario["global_vars"]["username"]
    password = inventario["global_vars"]["password"]

    for nombre, datos in inventario["routers"].items():
        comandos = []
        comandos += construir_hostname(datos)
        comandos += construir_enlaces_ruteados(datos)
        comandos += construir_wan(datos)
        enviar_config(nombre, datos, username, password, comandos)


if __name__ == "__main__":
    main()
