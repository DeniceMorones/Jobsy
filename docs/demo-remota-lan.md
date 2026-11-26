# Demo remota de Jobsy en red local (RF-18, RF-19, RNF-26)

Alcance: dos equipos en la **misma red privada** (mismo Wi-Fi o switch). Sin VPN y sin exposición a Internet.

## 1. Modelo de seguridad (qué protege y qué no)

| Medida | Dónde se aplica |
|---|---|
| El acceso remoto está **apagado por defecto** | Sin `--listen-host` no se abre ningún puerto |
| Solo una IP concreta (nunca `0.0.0.0` ni `::`) | `config.py` rechaza comodines al arrancar |
| Solo direcciones y redes **privadas** | `--listen-host` y `--allow-cidr` públicos o `/0` se rechazan |
| Lista de IPs permitidas obligatoria | `--allow-cidr` (repetible); el resto se cierra sin respuesta |
| Límite de conexiones (8 en total, 2 por IP) | `--max-remote-connections`, `--max-connections-per-ip` |
| Mensajes acotados y con plazos | Protocolo v1: máx. 1 MiB, 5 s por mensaje, 30 s de inactividad |
| Sin secretos en logs | Se registran solo las IPs y comandos descritos sin argumentos (RNF-15) |

**Limitaciones conocidas (declararlas en la entrega):**
- No hay cifrado ni autenticación del cliente (el ADR-009 propone mTLS; **no está implementado**). Cualquier equipo cuya IP esté en `--allow-cidr` puede ejecutar comandos. Úsese solo en una red de confianza.
- La lista de IPs filtra por dirección de origen, que no es una identidad.

## 2. Equipo servidor (Windows + WSL2)

### 2.1 Red de WSL2
WSL2 por defecto usa NAT: otros equipos no llegan a su IP. Dos opciones.

**Opción A (recomendada): modo mirrored** (Windows 11 22H2 o superior). Conserva la IP real del cliente, así que `--allow-cidr` funciona.
1. En Windows, crear o editar `C:\Users\<usuario>\.wslconfig`:
   ```
   [wsl2]
   networkingMode=mirrored
   ```
2. En PowerShell: `wsl --shutdown` y volver a abrir WSL.
3. Permitir el puerto en el firewall (PowerShell **como administrador**; ajustar la red):
   ```
   New-NetFirewallRule -DisplayName "Jobsy demo" -Direction Inbound -Protocol TCP -LocalPort 8765 -RemoteAddress 192.168.1.0/24 -Profile Private -Action Allow
   ```
4. Si el firewall de Hyper-V bloquea: `Set-NetFirewallHyperVVMSetting -Name '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -DefaultInboundAction Allow` (revertir después de la demo).

**Opción B: portproxy** (si mirrored no está disponible). Atención: el cliente llega al daemon con la IP del anfitrión Windows, no con su IP real. El filtro de IPs lo debe hacer entonces el firewall de Windows (`-RemoteAddress` de la regla), y `--allow-cidr` debe incluir la subred de WSL. Además todos los clientes cuentan como una sola IP para `--max-connections-per-ip`.
```
wsl hostname -I                      # p. ej. 172.20.10.5
netsh interface portproxy add v4tov4 listenaddress=<IP_LAN_WINDOWS> listenport=8765 connectaddress=<IP_WSL> connectport=8765
New-NetFirewallRule -DisplayName "Jobsy demo" -Direction Inbound -Protocol TCP -LocalPort 8765 -RemoteAddress 192.168.1.0/24 -Profile Private -Action Allow
```
Al terminar: `netsh interface portproxy delete v4tov4 listenaddress=<IP_LAN_WINDOWS> listenport=8765`.

### 2.2 IP del servidor
```
hostname -I          # en WSL (modo mirrored muestra la IP de la LAN)
```
Ejemplo: `192.168.1.50`.

### 2.3 Arrancar el daemon
```
jobsy-daemon --listen-host 192.168.1.50 --allow-cidr 192.168.1.0/24
```
(Con la opción B usar `--listen-host <IP_WSL> --allow-cidr 172.16.0.0/12`.)
El log debe decir `Acceso remoto habilitado en 192.168.1.50:8765`.

## 3. Equipo cliente
Requiere el repositorio y el entorno de Jobsy (solo el CLI; no necesita daemon).
```
jobsy --host 192.168.1.50 --port 8765 health
jobsy --host 192.168.1.50 run -- bash -c "echo hola desde otro equipo"
jobsy --host 192.168.1.50 list
jobsy --host 192.168.1.50 status <ID>
jobsy --host 192.168.1.50 output <ID>
jobsy --host 192.168.1.50 cancel <ID>
```
O bien `export JOBSY_HOST=192.168.1.50` y usar `jobsy list` sin repetir el host.

## 4. Evidencia para RNF-26 (capturas sugeridas)
1. **No escucha en todas las interfaces:** `ss -ltn | grep 8765` muestra `192.168.1.50:8765`, nunca `0.0.0.0:8765`.
2. **Rechazo de comodín:** `jobsy-daemon --listen-host 0.0.0.0 --allow-cidr 192.168.1.0/24` termina con el error `no puede ser 0.0.0.0`.
3. **Rechazo de red pública:** `--allow-cidr 8.8.8.0/24` y `--allow-cidr 0.0.0.0/0` terminan con error.
4. **Apagado por defecto:** arrancar sin `--listen-host` y comprobar que `ss -ltn | grep 8765` no muestra nada.
5. **IP no permitida:** desde un equipo fuera de `--allow-cidr`, el CLI falla con "No se pudo comunicar" y el log del daemon registra la IP rechazada.
6. **Sin reenvío de puertos en el router** (comprobación manual): el puerto 8765 no está publicado hacia Internet.

## 5. Cierre de la demo
Detener el daemon con Ctrl+C; verificar `ss -ltn | grep 8765` vacío y que no queda el socket Unix. Revertir `portproxy`, la regla de firewall y `.wslconfig` si ya no se necesitan.