# RE7 Android: adaptación de pantalla en Honor Magic V2

Caso de ingeniería para adaptar, desde un APK existente, la vista de un port de Resident Evil 7 basado en una capa de compatibilidad Android. El experimento se realizó en un Honor Magic V2 con un APK de prueba separado de la instalación original.

Este repositorio publica el método, un parche pequeño de bytecode Smali y la evidencia técnica descrita. **No contiene APK, juego, datos, partidas, drivers, Lossless.dll ni capturas del contenido del juego.** No está afiliado con Capcom, los autores del port, Winlator, Turnip ni Lossless Scaling.

## Resultado

- Se cambió la transformación de vista de **contain** a **cover**: la imagen conserva su proporción, cubre el área de dibujo y recorta el excedente centrado.
- Se ajustó el mapeo de entrada táctil para que coincida con el recorte de pantalla completa.
- Se reconstruyó el APK y se instaló como aplicación de prueba con identificador distinto, manteniendo instalada la original.
- El perfil final documentado usó un contenedor de 1024×576, Turnip Gen8 V38 parcheado, DXVK 2.3.1 con límite configurado en 70, Box64 en rendimiento y FEXCore en perfil intermedio.
- El usuario reportó después que ya ve la pantalla completa y más de 75 FPS. Esa medición final no se pudo volver a capturar por ADB: el teléfono quedó desconectado. Las capturas anteriores muestran 70 FPS en el menú inicial y 25 durante una transición de menú; por eso el reporte de >75 se conserva como resultado comunicado, no como medición reproducible de FPS reales sostenidos. Ver [resultados](docs/resultados-y-evidencia.md).

## Qué significa “solo con el APK”

No tuvimos el proyecto fuente Android del port. Partimos del APK, lo decodificamos con Apktool, editamos dos métodos de la capa Android representada en Smali y reconstruimos un APK de prueba. Esto cambió el escalado del lienzo y la transformación táctil. No reescribió el motor del juego ni convirtió el ejecutable de PC en código Android nativo.

## Documentos

- [Arquitectura y diagnóstico](docs/arquitectura-y-diagnostico.md)
- [Reproducción desde un APK propio](docs/reproduccion.md)
- [Experimentos, configuración y evidencia](docs/resultados-y-evidencia.md)
- [Evaluación de LSFG-Android](docs/generacion-de-cuadros.md)
- [Fuentes y herramientas](docs/fuentes-y-herramientas.md)
- [Límites y distribución](docs/distribucion-y-limites.md)

El parche está en [tools/patch_viewport.py](tools/patch_viewport.py). Es deliberadamente pequeño y se detiene si la estructura Smali no coincide con la esperada.

## Gráfico del cambio

~~~mermaid
flowchart LR
    A[APK propio del port] --> B[Apktool decodifica recursos y DEX]
    B --> C[Parche Smali: contain a cover]
    C --> D[Parche de coordenadas táctiles]
    D --> E[Apktool reconstruye APK]
    E --> F[Zipalign y firma de prueba]
    F --> G[Paquete de prueba separado]
    G --> H[Contenedor y driver por aplicación]
    H --> I[Capturar escena, superficie y HUD]
~~~

## Reproducción rápida

~~~bash
apktool d -f --no-src "$APK_PROPIO" -o decoded
python3 tools/patch_viewport.py decoded --apply
apktool b decoded -o unsigned.apk
~~~

La guía completa explica firma, instalación paralela, copias de seguridad y validación. Usa solo APKs y datos que tengas derecho a modificar. Cambiar el identificador de paquete y firmar con otra llave crea una compilación distinta; no sustituye ni actualiza la app original.

## Principios aprendidos

1. Mide el área real de la ventana y de la superficie de render. La resolución física del panel por sí sola no identifica dónde se forman las franjas.
2. min(escalaX, escalaY) conserva todo el cuadro y deja bandas cuando las proporciones no coinciden. max(escalaX, escalaY) llena el lienzo, pero recorta una dimensión.
3. Si se transforma la imagen, hay que aplicar la transformación inversa a la entrada táctil.
4. Mantén el juego, los datos y las partidas fuera del repositorio público.
5. Un límite de FPS solo fija un techo. No prueba que el juego lo sostenga.
6. La generación de cuadros interpola la salida mostrada; no demuestra que la simulación o el muestreo de entrada funcionen a esa frecuencia.
