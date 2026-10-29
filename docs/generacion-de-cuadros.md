# LSFG-Android: prueba y límites

LSFG-Android es una app independiente. No es el Lossless Scaling de Windows instalado dentro del contenedor. En Android no rooteado, el proyecto usa MediaProjection y una capa overlay; no se inyecta directamente en la swapchain Vulkan del juego. El usuario debe aprobar la captura del sistema. Android permite elegir compartir una app individual en vez de toda la pantalla cuando el sistema ofrece esa opción.

## Configuración documentada

- Versión de LSFG-Android: 0.1.2.
- Paquete seleccionado como destino: com.biohazard7.re7.adaptive.
- Lossless.dll: suministrada por el usuario mediante el selector de archivos. No se incluye ni se redistribuye.
- Multiplicador configurado: 2×.
- Modo rendimiento: activado.
- Shaders FP16: activados.
- Captura: MediaProjection.
- Superposición: permiso de mostrar sobre otras apps habilitado.
- La sesión se inició y apareció la interfaz flotante de LSFG. La evidencia capturada no confirmó por sí sola que la imagen generada y su contador siguieran la escena del juego de forma estable.

## Interpretar FPS

Si un juego produce 35 FPS y un generador presenta dos cuadros por cada cuadro de entrada, el contador visual puede acercarse a 70. La simulación del juego, el muestreo de entrada y la respuesta de controles siguen limitados por la frecuencia base. La interpolación también puede añadir latencia o artefactos.

La prueba de este caso no guardó una medición final simultánea del HUD DXVK y del contador de salida LSFG. Por eso el reporte actual de más de 75 FPS queda documentado como reporte del usuario, no como evidencia de que RE7 renderice 75 FPS reales.

La documentación del proyecto upstream describe MediaProjection como ruta de captura y advierte latencia adicional. La versión 0.1.2 publicó correcciones de compatibilidad Vulkan, pantalla negra, estabilidad y transferencia de imagen. Los requisitos y limitaciones pueden cambiar; consulta la versión actual antes de repetir.

## Consentimiento y privacidad

MediaProjection requiere consentimiento de Android para cada sesión. No selecciones toda la pantalla si la intención es capturar solo el juego y Android ofrece seleccionar la app. Conserva activo el indicador del sistema y termina la sesión al acabar. No distribuyas DLL ni shaders extraídos.
