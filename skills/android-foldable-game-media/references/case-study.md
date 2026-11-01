# Informe técnico reproducible: juegos, ports y aplicaciones multimedia en un plegable Android

| Campo | Valor |
|---|---|
| Versión del informe | 1.1 |
| Corte de evidencia | 2026-11-01 |
| Dispositivo de referencia | HONOR Magic V2, panel interior desplegado salvo que se indique otra cosa |
| Repositorio | [`elysium-vanguard-android-adaptive-engineering`](https://github.com/jordelmir/elysium-vanguard-android-adaptive-engineering) |

Este es un informe técnico con estructura científica y pasos de reproducción. No afirma revisión por pares. Su objetivo es que otra persona o agente pueda repetir el diagnóstico sin convertir observaciones puntuales en reglas universales.

## Resumen

Nueve grupos reúnen el trabajo pedido en un HONOR Magic V2: adaptar un port Winlator de *Resident Evil 7*; investigar cierre, driver, FPS y controles de *Halo 2*; ajustar *Sekiro*; buscar rendimiento estable en *Left 4 Dead 2*; adaptar el port Android de *Need for Speed: Most Wanted* (2012); ubicar datos de *Just Cause 2*; construir un clon separado de *PES 6*, importar una ISO europea y probar una adaptación de pantalla y tacto; adaptar el escalado de video de un clon de YouTube; y analizar tareas de USB/almacenamiento relacionadas con *PES 2017* y *Zelda: Breath of the Wild*. El repositorio conserva resultados de distinta fuerza: configuración, instalación, ejecución, medición y reportes del usuario se etiquetan por separado.

El hallazgo geométrico principal es que “pantalla completa” depende de la ventana y superficie activas. En una lectura del clon de YouTube, la actividad ocupaba `2156×2344`, mientras que `SurfaceView` medía `2156×1212` (16:9). La app podía estar a pantalla completa y aun así conservar un video apaisado con bandas arriba y abajo. Para mostrar el video completo sin deformarlo, el modo debe conservar aspecto y aceptar espacio libre; para llenar el área con `zoom` se recorta el cuadro, y `stretch` lo deforma.

## Preguntas de ingeniería

1. ¿La franja viene de Android, la ventana, el renderer, el juego o la relación de aspecto del video?
2. ¿Cómo preservar el APK original y los datos al probar una modificación en un plegable?
3. ¿Qué evidencia demuestra que un driver, límite de FPS, mapeo táctil o modo de escala está activo?
4. ¿Cómo crear un clon de una app Android sin pisar la original y preservar sus datos al actualizarlo?
5. ¿Qué resultados se pueden reutilizar y cuáles son solamente pedidos o reportes del usuario?

## Material y método

### Entorno observado

- El panel interior del Magic V2 aparece en las capturas en ambos sentidos: `2156×2344` en orientación vertical y `2344×2156` en horizontal.
- El usuario seleccionó únicamente la pantalla interior desplegada para el caso Halo 2.
- El entorno de pruebas usó ADB; la identidad del serial se omite porque es temporal y no hace falta para reproducir el método.
- Para RE7, el repositorio conserva los datos del contenedor, perfil, patch Smali y límites de evidencia. Véanse [`README.md`](../../../README.md), [`arquitectura-y-diagnostico.md`](../../../docs/arquitectura-y-diagnostico.md), [`reproduccion.md`](../../../docs/reproduccion.md) y [`resultados-y-evidencia.md`](../../../docs/resultados-y-evidencia.md).

### Método general

1. Identificar paquete, build, arquitectura, actividad, proceso, display, ventana y archivos requeridos por el port.
2. Guardar la app original, configuración y partidas; crear un baseline visual del mismo video/escena.
3. Medir actividad, superficie y contenido por separado. No inferir dimensiones de ventana a partir de la resolución nominal del panel.
4. Clasificar el fallo antes de cambiar algo: layout, ratio/viewport, entrada táctil, renderer/driver, archivos del juego o rendimiento.
5. Elegir un cambio reversible y específico de la app; cambiar una variable por intento.
6. Comparar la misma escena y verificar la configuración activa en runtime.
7. Informar los resultados con el estado de evidencia: configurado, instalado, iniciado, reproducido, verificado o reportado.

### Criterio geométrico

Para un cuadro de origen `W×H` dentro de un área disponible `A×B`:

```text
scale_x = A / W
scale_y = B / H
fit/contain = min(scale_x, scale_y)  # muestra todo, conserva aspecto
cover/zoom  = max(scale_x, scale_y)  # cubre el área, recorta una dimensión
stretch     = escalar X e Y por separado  # cubre el área, deforma
```

El recorte centrado en un juego también exige transformar las coordenadas táctiles con la inversa de la misma escala/traslación. En video, una aplicación puede conservar el cuadro en `Fit` y extender un fondo ambiental detrás; eso rellena el panel sin inventar píxeles de la escena ni recortar el video.

## Resultados por caso

| Caso | Resultado que puede afirmarse | Límite de la evidencia guardada |
|---|---|---|
| RE7 | Patch de viewport/touch y perfil `1024×576`, V38, DXVK con techo 70 documentados | Driver activo por proceso y FPS reales sostenidos no demostrados en captura final |
| Halo 2 | Usuario reportó volver a límite de 60 FPS tras tirones a 120 y prueba a 70; panel interior y controles táctiles eran el alcance | Límite final no medido; no hay log completo que pruebe el arreglo del cierre ni V38 activo |
| Sekiro | Se reportó que la pantalla mejoró; título y gameplay mostraron encuadres distintos | Falta estado final comparable de ambos; marca `TEST BUILD` no se demuestra removida |
| Left 4 Dead 2 | Pedido de optimización de estabilidad y FPS | No se retuvieron ajustes, paquete ni mediciones |
| NFS Most Wanted 2012 | Pantalla completa reportada; 90 FPS solicitado como objetivo | Límite persistido y FPS sostenido no medidos; Lossless se dejó fuera del objetivo final |
| Just Cause 2 | Se reorganizaron archivos para que el usuario seleccionara la carpeta desde el port | El destino exacto y un recibo de arranque no quedaron registrados |
| PES 6 | Clon separado instalado; ISO europea aceptada y copiada; el port llegó a escena 8 | El usuario reportó que quedó; la captura tras el parche aún mostraba bandas en selección de idioma y ADB quedó offline antes de confirmar los hooks y el táctil |
| YouTube | Clon `bill.youtube` construido, instalado y abierto | Botón de escala requirió reinicio; modo elegido y cobertura de todos los tipos de video no confirmados |
| USB / almacenamiento | Se pidió resetear un USB para PC, limpiar PES y revisar cachés/“Otros” | El sistema de archivos del USB y el espacio realmente liberado no quedaron en una medición final reproducible |

### Caso 1 — *Resident Evil 7*: APK adaptativo y perfil de rendimiento

**Arquitectura:** port Windows en un contenedor Android con FEXCore/Box64, DXVK/VKD3D y Vulkan; el trabajo fue en la capa Android representada por Smali, no una recompilación del motor del juego.

**Cambio documentado:** la transformación de `contain` a `cover` en `ViewTransformation.update(IIII)V`, además de alinear la transformación táctil de pantalla completa en `TouchpadView.updateXform(IIII)V`. El script [`tools/patch_viewport.py`](../../../tools/patch_viewport.py) valida anclajes versionados y falla si el Smali no coincide. La compilación de prueba usó otro ID de paquete y dejó instalado el original.

**Perfil conservado por el repo:** contenedor `1024×576`, Turnip Gen8 V38 parcheado, DXVK 2.3.1 con límite configurado de 70, Box64 `PERFORMANCE`, FEXCore `INTERMEDIATE`; algunos efectos gráficos fueron reducidos. El repo describe V38 como perfil probado/configurado, pero deja claro que el uso real de V38 por cada proceso requiere logs runtime. El límite 70 no es FPS sostenido.

El objetivo de FPS cambió a lo largo de la conversación: primero se pidió 120, luego 90 con idioma español y una mejora visual manteniendo rendimiento, y después 60 al notar el máximo del menú del juego. El perfil final conservado en el repositorio registra un límite de 70. Al repetir el caso, usa el perfil/versionado actual del repositorio y confirma la petición vigente; ninguno de esos límites garantiza FPS sostenidos. El cambio de idioma debe verificarse en textos del juego, no solo en el wrapper.

El usuario expresó que no quería tratar la temperatura como restricción para esa iteración. La regla reutilizable es respetar esa prioridad y reportar la lectura térmica, sin confundirla con FPS o estabilidad demostrados.

**Evidencia y límites:** las capturas locales del repo muestran el menú de RE7 y lecturas distintas según la escena. El usuario comunicó luego pantalla completa y más de 75 FPS; no quedó una captura final independiente que pruebe FPS reales sostenidos. El perfil está documentado en [`resultados-y-evidencia.md`](../../../docs/resultados-y-evidencia.md); no se debe copiar a un port distinto sin el mismo loader y evidencia.

### Caso 2 — *Halo 2*: cierre al iniciar gameplay, driver y pantalla interior

**Entradas conocidas:** el usuario indicó que el APK se cerraba al entrar a jugar y proporcionó [Ayanokoji989/Halo-2](https://github.com/Ayanokoji989/Halo-2). Su README describe opciones añadidas y advierte que comportamiento y compatibilidad varían con GPU y driver. El usuario solicitó aplicar el driver V38 que tenía en `apks`, adaptar la pantalla al Magic V2 y reubicar los controles táctiles para hacerlos más pequeños y evitar solapamientos; después eligió solamente la pantalla interior desplegada. También pidió Lossless/60 FPS, luego intentó 120, reportó tirones, pidió bajar a 70 y finalmente volver a 60.

**Estado de resultado:** el usuario reportó que terminó en 60 FPS, pero no se conservó medición del juego. No hay captura de gameplay posterior, log de crash completo ni prueba de renderer V38 activo; tampoco evidencia simultánea que confirme cuadros generados o latencia Lossless/LSFG. Por tanto 60 es un ajuste reportado, no FPS sostenidos medidos; el cierre y el objetivo de driver no son un arreglo demostrado. Al repetirlo, identifica la build exacta y conserva `logcat`, tombstone, proceso y escena del crash antes de cambiar driver; prueba después un solo cambio y repite el mismo punto de entrada.

### Caso 3 — *Sekiro: Shadows Die Twice*: título, gameplay, bandas y marcas de prueba

**Síntomas pedidos:** abrir los archivos propios desde Android; conseguir una vista adaptativa en el panel interior del Magic V2; corregir bandas negras en el título y gameplay; investigar una banda rojiza/esquinas rojas, preguntar si el driver V38 parcheado podría ayudar y quitar la marca “TEST BUILD”; evitar que los controles táctiles se recorten.

**Observación importante:** el usuario informó que el gameplay llegó a verse más grande y mostró una captura donde el título aún parecía usar otra área de render. Esto indica que menú/título y gameplay pueden tomar caminos de superficie o ratios distintos. No se debe aplicar un cambio a una sola pantalla y declarar todo el port adaptativo. La marca TEST BUILD puede formar parte de una imagen o build de prueba; no se debe eliminar pintando sobre la escena ni editando assets ajenos sin una fuente autorizada.

**Estado de resultado:** la conversación incluye reportes parciales de mejora, pero el registro que se conserva no identifica una comparación A/B de driver, un cambio final reproducible ni una captura de ambos estados después del último arreglo. Repetir el diagnóstico en menú/título y gameplay con el mismo display, postura, rotación y configuración; revisar superficie, juego y mapeo por separado. Mantener las bandas cinematográficas del propio juego si son parte del contenido original.

### Caso 4 — *Left 4 Dead 2*: objetivo de rendimiento y estabilidad

**Pedido conocido:** configurar el juego Android para el mayor rendimiento, estabilidad y FPS posibles.

**Estado de resultado:** no se conservó build/package exacto, valores de config, escena, driver activo ni mediciones posteriores. No hay un perfil publicable para este título en este informe. Al reproducir, inspecciona documentación/versiones del port y mide una escena real de juego antes de recomendar una calidad o límite; no heredes valores de RE7.

### Caso 5 — *Need for Speed: Most Wanted* (port Android de 2012)

**Pedido y secuencia conocida:** el usuario identificó el port de 2012, informó que el juego estaba abierto y que sus archivos estaban en el administrador de archivos en `NFSMW`; luego pidió adaptar la pantalla al Magic V2. Informó que la pantalla completa ya funcionaba y pidió rendimiento, primero hasta 90 FPS y Lossless Scaling, y después dejó Lossless de lado manteniendo la meta de 90 FPS.

**Estado de resultado:** la conversación visible no conserva paquete exacto, estructura final de archivos, configuración persistida, lectura de FPS real ni prueba de Lossless. Por ello “pantalla completa” queda como resultado reportado por el usuario y “90 FPS” como objetivo, no como frecuencia medida. Al repetir, localiza la ruta documentada por ese port, valida archivos, conserva la carpeta fuente y distingue límite configurado, FPS del juego y frecuencia del panel.

### Caso 6 — *PES 2017*, *Zelda: Breath of the Wild*, USB y almacenamiento

El análisis mencionó una entrada de *Zelda BOTW* estimada en 8.8 GiB, una copia de prueba de *PES 2017* estimada en 176.5 GiB y cerca de 2.0 GiB de *Clash of Clans*. El usuario pidió borrar todo PES y revisar cachés elegidas, con un máximo estimado de 3.2 GiB. También se encontró un archivo temporal de Chrome con tamaño aparente de 9.4 GiB y solo unos 25 MiB asignados. El usuario pidió borrarlo de todos modos. Esas cifras describen el inventario previo; no equivalen a espacio efectivamente liberado.

El Termux informaba 5.7 GiB de datos. Esa categoría podía incluir proyectos y archivos personales, por lo que no se trató como caché sin inspección de las rutas. El usuario también pidió resetear un USB conectado al Android para usarlo en PC. La conversación no conserva el sistema de archivos, la tabla de particiones ni un montaje de verificación en PC. Al repetirlo, elige un formato compatible con los sistemas destino, valida la capacidad y vuelve a leer la estructura después del formateo.

Al repetir una limpieza, vuelve a medir la carpeta exacta, distingue tamaño aparente de bloques ocupados y verifica que la copia no sea compartida con otro port. Conserva un inventario del objetivo; elimina solo lo que el usuario nombró explícitamente. No deduzcas que “Otros” es contenido temporal ni borres datos de apps para liberar almacenamiento cuando la instrucción solo dice caché. Informa los bytes realmente recuperados después de la operación.

### Caso 7 — *Just Cause 2*: ubicar archivos para el port

El usuario indicó que el port estaba abierto y que el juego residía en una carpeta `JustCause2` del almacenamiento. Pidió organizar los archivos y recibir la ruta para seleccionarla manualmente en el port. La conversación no conserva la ruta final ni una validación de ejecutable/datos o recibo de arranque; no la inventes a partir del nombre de la carpeta. Al repetir, inspecciona primero la estructura que exige esa versión del port, conserva la carpeta fuente y entrega la ruta exacta que queda en el dispositivo.

### Caso 8 — Clon de YouTube para escala del video en el Magic V2

**Objetivo:** responder a las franjas superior/inferior de la aplicación mod, ofreciendo un clon separado con un control de escala que pueda usarse con los videos a pantalla completa. El requisito de no perder información se trata como preservación del cuadro en `Default/Fit`; `Zoom` y `Stretch` se exponen como decisiones con costos explícitos.

**Entradas/build registradas:**

- App original observada: paquete `app.rvx.android.youtube`, versión `20.14.43`; quedó instalada.
- Un intento de volver a parchear ese APK ya modificado no encontró patches compatibles y no se instaló.
- Base limpia usada para el clon: YouTube `21.13.164`, obtenida de [esta entrada de APKMirror](https://www.apkmirror.com/apk/google-inc/youtube/youtube-21-13-164-release/youtube-21-13-164-4-android-apk-download/), SHA-256 `c193daf879d36e04886c34dcc44580b1c98c20534165d306c2a04b8025fc3f46`. APKMirror es un mirror de terceros; la cadena de firma de la base se verificó antes de parchear. Para repetir, usa una copia autorizada de la misma versión y verifica su firma/hash.
- Morphe Desktop CLI `1.20.0`, SHA-256 `679f579b3ad743ac0ca697ef71e57430d00be59411b04494afd1845c43fb79f`; bundle Anddea `4.3.0`, SHA-256 `deb9dbe2fe1d70300d3fe4b6c99c0042a6f3095dfb932e5d79ca40eaeb59f454`.
- Patches: `Fullscreen video scale`, `GmsCore support`, `Settings for YouTube`, `Ambient mode control`, `Custom branding for YouTube`.
- Ajustes de patch usados: paquete del clon `bill.youtube`, vendor group `app.revanced`, comprobación de GmsCore activa, patch de manifest, etiqueta de ajustes `RVX`, marca visible `YouTube Adaptive` y el icono original.
- Resultado: APK firmado por separado, paquete verificado como `bill.youtube`, versión `21.13.164`, target SDK 36, tamaño `195,462,047` bytes y SHA-256 de salida `fd46b8fff078a33ba0dbb062f3d775a67f7814579e66d465837621bdb3e506ce`. El reporte de Morphe describía el package base `com.google.android.youtube`; por eso se verificó el ID final directamente desde el manifiesto.

**Instalación/runtime:** `adb install` terminó en `Success`; se confirmó que el original y el clon aparecen como paquetes distintos; el clon abrió la actividad principal sin crash inmediato. GmsCore mostró un selector de cuentas; no se eligió cuenta. Se denegó la solicitud de notificaciones. La verificación de arranque no equivale a comprobar que todos los tipos de video usan la escala.

**Lectura geométrica del player:** la jerarquía UI informó actividad/player de `2156×2344` y `SurfaceView` de `[0,566][2156,1778]`, esto es `2156×1212` con relación `16:9`. La ventana ocupa el panel interior, pero el cuadro de video conserva 16:9; la franja visible no prueba por sí sola que falte una configuración global de pantalla.

**Ajuste in-app:** se encontró `YouTube → Settings → RVX → Player → Player buttons → Overlay buttons → Show video scale button`. Al intentar activarlo, la UIAutomation reportó “Restart required”. El estado final de ese reinicio y el ciclo `Default/Stretch/Zoom` no quedaron verificados tras la interrupción del trabajo. El clon sí incluye el patch en el binario, pero no se afirma que el usuario ya tenga Zoom persistido ni que la vista llene el panel en todos los videos.

**Trade-off:** en una pantalla casi cuadrada, ampliar una imagen 16:9 hasta ocupar la altura recorta una fracción grande de sus bordes horizontales. `Stretch` conserva todos los extremos, pero altera figuras y texto. Para mantener toda la información, usa `Default/Fit`; si el usuario prioriza cobertura total, habilita Zoom y comprueba que entiende el recorte. Una alternativa visual es ambient/background fill detrás de un video en Fit.

La petición posterior de quitar el 100 % de los anuncios no forma parte del trabajo de escala descrito aquí; este registro no confirma que se haya aplicado un cambio de anuncios.

### Caso 9 — *PES 6*: clon limpio, ISO europea, pantalla completa y tacto

**Base y datos:** el APK original identificado en el dispositivo era `com.pes6port.iso`; el usuario confirmó que estaba limpio y pidió un clon separado. Se copió el APK instalado, se cambió el identificador a `com.pes6port.iso.touchfix`, se le dio una etiqueta distinta y se firmó con una llave local de prueba. La instalación del clon y una actualización posterior conservaron separado el original. La llave y los APK permanecen en el Mac; no se publican.

La ISO seleccionada fue *Pro Evolution Soccer 6 (Europe) (En,Fr,De,Es,It)*, de 1,248,329,728 bytes. El log del clon indicó `ISO correcta` y confirmó que la copia terminó en los datos de esa app. En la misma ejecución, el renderer detectó Adreno 740, preparó una resolución interna de 1440×816 y llegó a la escena 8 con lecturas cercanas a 30 FPS. Esas lecturas se refieren al juego antes del parche de escala y no prueban 60 FPS.

**Parche de prueba:** se dividió el `libpes6.so` incluido en el APK de prueba en una biblioteca núcleo y un cargador pequeño. El cargador intercepta las llamadas `glBlitFramebuffer` que copian el FBO del juego a la superficie EGL y escala el cuadro a las dimensiones de la superficie. También redirige `pes6_launcher_window_point` a coordenadas normalizadas por el ancho y alto completos, para que los toques del menú correspondan a la imagen extendida. Esto aplica `Stretch`: cubre la superficie sin recorte, pero deforma la relación original. Requiere comprobar los controles por separado.

El APK actualizado se verificó con `apksigner`, mantuvo el mismo paquete/llave del clon, se instaló correctamente y abrió `NativeActivity`. El archivo `pes6.iso` persistió después de la actualización. Una captura tomada en la selección de idioma todavía mostraba bandas arriba y abajo. El usuario indicó luego “ya quedó”; ADB pasó a `offline` antes de leer los logs específicos del cargador o verificar el toque físico. Estado de evidencia: **actualización instalada y éxito reportado por el usuario; hook activo, pantalla 100 % y tacto final no verificados independientemente**. Para cerrar la reproducción se necesita una captura posterior en la misma escena y una prueba táctil en menú y gameplay.

## Receta reproducible del clon de YouTube

Los comandos son una plantilla para una nueva copia autorizada; no redistribuyas el APK base, el clon firmado ni la llave. Fija las versiones y hashes para poder comparar. Revisa compatibilidad nuevamente antes de repetir porque los patches y builds cambian.

```bash
java -jar "$MORPHE_JAR" list-versions \
  --patches "$PATCH_BUNDLE" \
  --filter-package-names com.google.android.youtube

java -jar "$MORPHE_JAR" list-patches \
  --patches "$PATCH_BUNDLE" --with-options

java -jar "$MORPHE_JAR" patch \
  --patches "$PATCH_BUNDLE" --exclusive \
  --enable "Fullscreen video scale" \
  --enable "GmsCore support" \
  --enable "Settings for YouTube" \
  --enable "Ambient mode control" \
  --enable "Custom branding for YouTube" \
  --options 'packageNameYouTube=bill.youtube' \
  --options 'gmsCoreVendorGroupId=app.revanced' \
  --options 'checkGmsCore=true' \
  --options 'disableCoreServices=false' \
  --options 'patchAllManifest=true' \
  --options 'rvxSettingsLabel=RVX' \
  --options 'customName=YouTube Adaptive' \
  --options 'appIcon=original' \
  --out youtube-adaptive-clone.apk \
  --result-file patch-result.json \
  "$BASE_YOUTUBE_APK"

aapt dump badging youtube-adaptive-clone.apk | head
apksigner verify --verbose youtube-adaptive-clone.apk
unzip -t youtube-adaptive-clone.apk

adb devices -l
adb -s "$SERIAL" shell pm list packages
adb -s "$SERIAL" install youtube-adaptive-clone.apk
adb -s "$SERIAL" shell monkey -p bill.youtube 1
```

Use Java 21 for the recorded Morphe Desktop 1.20.0 setup. The patch CLI supports multiple named patches and typed options; use `--exclusive` so unlisted patches are not silently added. Never put a signing keystore/password, ADB serial, account state, downloaded APK, game data or private capture in this repo.

## Cómo repetir la medición de pantalla

1. Identifica el display interior y toma una captura explícita de ese display.
2. Guarda jerarquía UI, ventana y listado de superficies mientras reproduces un video conocido.
3. Registra bounds de la actividad y del `SurfaceView`/surface, y calcula su relación de aspecto.
4. En el clon, activa el botón de escala, reinicia si el diálogo lo solicita y abre el mismo video en modo de pantalla completa.
5. Cicla `Default`, `Stretch`, `Zoom`; en cada estado guarda captura y bounds. Confirma si la preferencia persiste al cambiar de video y después de cerrar/abrir la app.
6. Repite al menos con video estándar, Shorts, feed/miniplayer e incrustado. La afirmación “todos los videos” requiere resultados para cada clase probada y una lista explícita de lo que quedó fuera.
7. Confirma que el paquete activo sigue siendo `bill.youtube`, que el original no cambió, y que no se seleccionó una cuenta durante la verificación.

## Límite de inferencia y validez

Los resultados son de un solo dispositivo y aplicaciones/builds específicos. No se controlaron todas las codificaciones, relaciones de aspecto, contenidos servidos por servidor, posturas, orientaciones, escenas ni versiones. El usuario reportó algunas mejoras; el informe conserva ese dato como reporte cuando falta una captura verificable. Los ajustes de driver y rendimiento no son portables entre juegos solo por compartir el mismo hardware. El clon es un artefacto de prueba local y el modo de escala requiere comprobación por tipo de reproducción.

## Referencias

1. Repo y perfil RE7: [`README`](../../../README.md), [`diagnóstico`](../../../docs/arquitectura-y-diagnostico.md), [`método APK`](../../../docs/reproduccion.md), [`evidencia`](../../../docs/resultados-y-evidencia.md), [`LSFG`](../../../docs/generacion-de-cuadros.md).
2. Android Developers, [Make your app fold aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware) y [Use window size classes](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes).
3. Morphe Desktop, [CLI documentation](https://github.com/MorpheApp/morphe-desktop/blob/main/docs/documentation.md).
4. Anddea, [patch list and compatible YouTube versions](https://github.com/anddea/revanced-patches), incluido `Fullscreen video scale`.
5. Repo Halo proporcionado por el usuario, [Ayanokoji989/Halo-2](https://github.com/Ayanokoji989/Halo-2).
