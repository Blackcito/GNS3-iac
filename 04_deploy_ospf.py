"""
04_deploy_ospf.py — Fase 4: enrutamiento dinámico OSPF.
Configura OSPF en el router de borde (R1) y los switches de distribución.
"""
from comun import (
    cargar_inventario,
    enviar_config,
)


def construir_ospf(datos_equipo, area):
    """Configura OSPF: router-id, enlaces activos y SVIs (passive)."""
    comandos = []

    # 1) Proceso OSPF + router-id
    comandos.append("router ospf 1")
    comandos.append(f"router-id {datos_equipo['router_id']}")

    # 2) SVIs como passive (solo los switches de distribución tienen 'svis')
    if "svis" in datos_equipo:
        for svi in datos_equipo["svis"]:
            comandos.append(f"passive-interface Vlan{svi['vlan']}")
    comandos.append("exit")

    # 3) Enlaces ruteados: activos (forman vecinos OSPF)
    for enlace in datos_equipo["enlaces_ruteados"]:
        comandos.append(f"interface {enlace['interface']}")
        comandos.append(f"ip ospf area {area}")
        comandos.append("exit")

    # 4) SVIs: advertir las subredes de usuarios (ya marcadas como passive)
    if "svis" in datos_equipo:
        for svi in datos_equipo["svis"]:
            comandos.append(f"interface Vlan{svi['vlan']}")
            comandos.append(f"ip ospf area {area}")
            comandos.append("exit")

    return comandos


def main():
    inventario = cargar_inventario("inventario.yaml")
    username = inventario["global_vars"]["username"]
    password = inventario["global_vars"]["password"]
    area = inventario["ospf"]["area"]

    # Combinar routers + distribución (ambos corren OSPF)
    equipos_l3 = {
        **inventario.get("routers", {}),
        **inventario.get("switches_distribucion", {}),
    }

    for nombre, datos in equipos_l3.items():
        comandos = construir_ospf(datos, area)
        enviar_config(nombre, datos, username, password, comandos)


if __name__ == "__main__":
    main()
