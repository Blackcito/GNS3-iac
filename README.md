# Arista NetDevOps: Automatización de Infraestructura como Código (IaC) en Python

## Descripción del Proyecto
Este repositorio contiene la automatización completa de una topología de red jerárquica (Core/Distribución/Acceso) basada en switches Arista vEOS y enrutamiento OSPF. A diferencia de los orquestadores declarativos (como Terraform o Ansible), este proyecto fue desarrollado nativamente en **Python con Netmiko**.

El diseño arquitectónico separa por completo la lógica imperativa de ejecución de los datos de la red (inventario YAML), permitiendo escalar la topología sin modificar el código fuente.

##  Arquitectura y Tecnologías
*   **Gestión de Datos (SSOT):** Archivo YAML (`inventario.yaml`) estructurado como Fuente Única de Verdad para VLANs, direccionamiento IP, roles STP y parámetros VRRP.
*   **Orquestación Iterativa:** Scripts modulares en Python 3 implementando el principio DRY (Don't Repeat Yourself) para el despliegue de configuraciones vía SSH.
*   **Alta Disponibilidad (HA):** Configuración dinámica de Rapid-PVST+ (Root Primary/Secondary) para prevención de bucles L2, y VRRP (Master/Backup) con preempción para redundancia de Gateways.
*   **Agregación de Enlaces:** Despliegue automatizado de EtherChannels (LACP 802.3ad) en enlaces troncales y ruteados.
*   **Enrutamiento y Perímetro:** Configuración automatizada de OSPF Multi-área para la propagación de rutas y NAT Overload (PAT) dinámico en el router de borde para salida a Internet.
*   **Entorno de Pruebas:** Topología virtualizada en GNS3 sobre KVM/QEMU (Linux), utilizando una red Out-of-Band (OOB) para la gestión.

## Estructura del Repositorio
*   `inventario.yaml`: Base de datos centralizada con la topología, credenciales y parámetros de red.
*   `comun.py`: Módulo core con funciones reutilizables de conexión, escalada de privilegios y generación de comandos base.
*   `01_conexion_base.py`: Auditoría inicial para validar conectividad SSH y credenciales contra todos los nodos.
*   `02_deploy_l2_l3.py`: Despliegue de la Capa de Distribución (Creación de SVIs, inyección de VRRP, STP y LACP).
*   `03_deploy_acceso.py`: Despliegue de la Capa de Acceso (Asignación de puertos de acceso y Trunks LACP).
*   `04_deploy_ospf.py`: Despliegue del enrutamiento dinámico (OSPF) en el perímetro y distribución.
*   `05_deploy_router.py`: Configuración del router perimetral (R1), incluyendo ruteo global y reglas NAT/PAT.

## Cómo Ejecutar

1.  Asegurar la conectividad hacia la red Out-of-Band de Management (ej. `192.168.122.0/24`).
2.  Instalar las dependencias de Python:
    ```bash
    pip install netmiko pyyaml
    ```
3.  Ejecutar el pipeline de despliegue en orden (Fases 01 a 05).