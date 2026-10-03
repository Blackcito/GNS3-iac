import yaml
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException


#
# 1. Cargar el inventario YAML
def cargar_inventario(ruta_archivo):
    """Lee el archivo YAML y retorna un diccionario de Python"""
    try:
        with open(ruta_archivo, "r") as archivo:
            return yaml.safe_load(archivo)
    except FileNotFoundError:
        print(f" Error: No se encontró el archivo {ruta_archivo}")
        exit(1)
    except yaml.YAMLError:
        print("Archivo mal formateado")
        exit(1)


def obtener_equipos(inventario):
    return {
        **inventario.get("switches_distribucion", {}),
        **inventario.get("switches_acceso", {}),
        **inventario.get("routers", {}),
    }


def test_conexion(nombre_equipo, datos, username, password):
    print(f" Intentando conectar a {nombre_equipo.upper()} ({datos['ip_mgmt']})")

    # Diccionario con los parámetros que Netmiko requiere
    dispositivo = {
        "device_type": datos["device_type"],
        "host": datos["ip_mgmt"],
        "username": username,
        "password": password,
        "fast_cli": True,  # Optimización para Arista
    }

    try:
        # 4. Establecer conexión
        conexion = ConnectHandler(**dispositivo)

        # 5. Ejecutar un comando de lectura (show)
        prompt = conexion.find_prompt()
        version_output = conexion.send_command(
            "show version | include Software image version"
        )

        print(f"   Conectado exitosamente! Prompt: {prompt}")
        print(f"   {version_output.strip()}")

        # 6. Cerrar sesión
        conexion.disconnect()

    except NetmikoAuthenticationException:
        print(f"   Fallo de autenticación en {nombre_equipo}. Revisa usuario/clave.")
    except NetmikoTimeoutException:
        print(
            f"   Timeout: El equipo {nombre_equipo} no responde en la IP {datos['ip_mgmt']}."
        )
    except Exception as e:
        print(f"   Error desconocido en {nombre_equipo}: {str(e)}")

    print("-" * 50)


def main():
    inventario = cargar_inventario("inventario.yaml")
    username = inventario["global_vars"]["username"]
    password = inventario["global_vars"]["password"]
    equipos = obtener_equipos(inventario)

    for nombre, datos in equipos.items():
        test_conexion(nombre, datos, username, password)


if __name__ == "__main__":
    main()
