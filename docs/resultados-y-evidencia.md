# Experimentos, configuración y evidencia

## Dispositivo y alcance

- Dispositivo: HONOR Magic V2, pantalla interior.
- GPU observada en el HUD del renderer: Adreno 740.
- Android observado: versión 16.
- El usuario autorizó probar primero una instalación paralela; luego autorizó usar la app original si hiciera falta. El experimento descrito mantuvo disponible el paquete original.
- No se publican serial ADB, rutas privadas completas, hashes de APK, contenido de juego ni capturas del juego.

## Secuencia de cambios

| Etapa | Resolución del contenedor | Driver reportado por configuración | DXVK | Resultado |
|---|---:|---|---:|---|
| Estado inicial guardado | 1024×800 | Turnip integrado indicado como turnip-oneui7-8gen2 | 35 | Se observaban franjas; no era una comparación controlada de una sola variable. |
| Prueba de encuadre | 1024×576 | Mismo Turnip integrado | 35 | Se aisló el cambio de tamaño del contenedor. |
| Perfil final de prueba | 1024×576 | Turnip Gen8 V38-patched | 70 | APK paralelo, transformación cover y transformación táctil alineada. |

Otros valores de perfil observados: Box64=PERFORMANCE, FEXCore=INTERMEDIATE, fullscreenStretched=true, DXVK 2.3.1 y modo variable en re7_config.ini. Son valores configurados. No prueban por sí mismos que cada capa de rendimiento esté activa en cada escena.

El archivo re7_config.ini del perfil de rendimiento dejó VSync apagado, sombras en LOW, sombras dinámicas apagadas, desenfoque y profundidad de campo apagados, y AO/SSR/SSSS/Bloom deshabilitados. La calidad de malla y textura quedó en STANDARD. Estos ajustes reducen algunos efectos costosos; no sustituyen una medición de rendimiento en la misma escena.

## Encuadre

Las capturas locales previas a la desconexión del dispositivo son 2344×2156 y muestran el menú de RE7 ocupando la imagen, con el HUD de DXVK y controles táctiles visibles. La transformación usa escalado uniforme tipo cover: llena el lienzo sin deformar, con recorte centrado cuando las proporciones difieren.

El usuario confirmó después que ya ve la pantalla completa. La captura final de esa declaración no pudo adquirirse porque ADB mostró el dispositivo como offline. Por tanto, el último estado completo es un reporte directo del usuario respaldado parcialmente por las capturas locales previas del APK de prueba.

## FPS: valores distintos

- Límite de DXVK configurado: 70 FPS.
- Una captura local del menú inicial mostró FPS 70 en el HUD.
- Una captura de transición de menú mostró FPS 25.
- Estos dos cuadros prueban que el HUD presentó valores distintos según la escena. No prueban más de 75 FPS reales sostenidos durante gameplay.
- El usuario informó después que el juego supera 75 FPS y llena la pantalla. Al no tener una captura final ni una lectura del overlay de LSFG, no se puede determinar si “75+” es FPS renderizado por el juego, cuadros interpolados mostrados o el valor de otro contador.

La verificación correcta separa: FPS del HUD DXVK, cuadros generados por LSFG, frecuencia del panel y respuesta/latencia de entrada. Un tope de 70 no crea 70 FPS si la carga no los alcanza.

## Estado conocido y pendiente

| Afirmación | Evidencia | Estado |
|---|---|---|
| El APK paralelo se instaló y abrió | Capturas del menú/título, actividad de prueba y proceso re7.exe en la inspección ADB previa | Verificado en la sesión de prueba |
| El área capturada ocupa 2344×2156 | Dimensiones de las capturas locales | Verificado para esas capturas |
| El perfil guardado tenía V38 y tope 70 | .container leído desde datos privados de la app de prueba | Verificado como configuración |
| El driver V38 fue el renderer activo en cada ejecución | Requeriría log/runtime del renderer asociado al mismo proceso | No demostrado solo con el valor de configuración |
| La escena final ya llena la pantalla | Reporte del usuario y capturas previas del menú de prueba | Reportado y respaldado parcialmente; falta captura final |
| Se sostienen más de 75 FPS reales en gameplay | Reporte del usuario; HUD anterior llegó a 70 en menú y bajó a 25 en transición | No medido independientemente |
| LSFG entrega más de 75 cuadros generados sobre RE7 | Configuración 2× y sesión iniciada; no se guardó captura final del juego con el contador de LSFG | No medido independientemente |

## Evidencia que quedó local

Los PNG originales y la copia de trabajo están en el Mac del usuario, fuera de este repositorio. El repo no replica el contenido del juego. Los archivos de captura se omitieron para evitar exponer rutas privadas y redistribuir escenas con derechos de autor.

## Próxima medición reproducible

En una futura sesión autorizada:

1. Conectar ADB y guardar el serial actual; identificar display interior y actividad.
2. Iniciar una escena estable con el mismo perfil V38.
3. Capturar 60 segundos de HUD DXVK y tiempos de cuadro con LSFG apagado.
4. Repetir la misma escena con LSFG 2×, misma resolución y límite.
5. Registrar por separado promedio, mínimo, frametime, temperatura, consumo, FPS del juego y FPS de salida del generador.
6. Verificar controles, artefactos y latencia percibida.
7. No afirmar 75 FPS reales a partir del contador del generador o de un menú.
