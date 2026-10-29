# Reproducción desde un APK propio

Este flujo parte de un APK que el usuario tiene derecho a analizar y modificar. Está orientado a un port Android cuya clase ViewTransformation y control táctil coincidan con los anclajes del parche. No es un instalador de juego.

## 1. Preparar una copia de trabajo

Guarda el APK original sin modificar y calcula su hash local. Trabaja sobre una copia. Comprueba que el sistema tiene espacio para el APK, el directorio decodificado y el APK reconstruido.

No subas a este repositorio el APK, sus datos, claves de firma, DLL, drivers, partidas ni capturas con contenido del juego.

## 2. Herramientas

- Apktool para decodificar y reconstruir recursos y Smali.
- Java compatible con la versión local de Apktool.
- Android SDK Build Tools para zipalign y apksigner.
- ADB para instalar y observar el paquete de prueba.
- REA es opcional para evidencia de dispositivo, actividad, paquetes, ventanas, logs y hashes de adquisición.

Usa versiones fijadas durante una sesión y anótalas. El caso documentado usó Apktool local y REA 6.5.0; los números de versión describen ese entorno, no un requisito universal.

## 3. Decodificar

~~~bash
apktool d -f --no-src "$APK_PROPIO" -o decoded
~~~

--no-src conserva el flujo de Apktool pero evita decodificar DEX a Java, que no se necesita para este parche. Apktool genera Smali legible para aplicar el cambio.

Si la estructura Smali se asigna a otro smali_classesN, localiza las clases por paquete y ajusta las rutas del script. No copies a ciegas índices de otro APK.

## 4. Aplicar la transformación

Primero revisa el método de la versión decodificada. El script modifica solo estos dos anclajes:

- ViewTransformation.update(IIII)V: Math.min pasa a Math.max.
- TouchpadView.updateXform(IIII)V: se neutraliza la bifurcación fullscreen identificada.

~~~bash
python3 tools/patch_viewport.py decoded
~~~

El modo predeterminado informa si encuentra los anclajes, sin escribir. Para aplicar:

~~~bash
python3 tools/patch_viewport.py decoded --apply
~~~

Si el script informa que el patrón no coincide, detente y analiza el método de esa versión. No amplíes la búsqueda ni sustituyas instrucciones de forma global.

## 5. Recursos con extensión incorrecta

Durante este caso se encontraron recursos con sufijo .png cuyo encabezado no era PNG. Se inspeccionaron y se normalizaron antes de reconstruir, usando FFmpeg para convertir el primer cuadro. Esta operación puede perder animación si el recurso era animado. Haz inventario, conserva copia y revisa visualmente cada recurso afectado. No hagas conversión masiva si no es necesaria para compilar.

La utilidad histórica quedó fuera del repositorio porque apuntaba a rutas locales del Mac y no era segura para distribuir como herramienta lista para ejecutar.

## 6. Paquete de prueba y firma

Para una instalación paralela, cambia de forma coherente el identificador de paquete en el manifiesto y referencias pertinentes, además de etiqueta, versionCode y versionName. Comprueba que el APK reconstruido informa el nuevo identificador antes de instalar.

~~~bash
apktool b decoded -o unsigned.apk
zipalign -p -f 4 unsigned.apk aligned.apk
apksigner sign --ks "$ANDROID_TEST_KEYSTORE" --out test-signed.apk aligned.apk
apksigner verify --verbose test-signed.apk
~~~

La llave de prueba debe permanecer fuera del repositorio. No escribas contraseñas en el historial del shell. La firma nueva no equivale a la firma de la app original.

## 7. Instalar y observar

~~~bash
adb devices -l
adb -s "$SERIAL" install test-signed.apk
adb -s "$SERIAL" shell dumpsys activity activities
adb -s "$SERIAL" shell dumpsys window windows
adb -s "$SERIAL" exec-out screencap -p > local-capture.png
adb -s "$SERIAL" logcat -d -t 2000 > local-logcat.txt
~~~

En una sesión con varios dispositivos, usa el serial en todos los comandos. Si el equipo aparece offline, no instales ni lances nada: reconecta el dispositivo y vuelve a identificar el serial.

Con REA, la secuencia equivalente de inspección incluye rea list-adb-devices, rea inspect-adb-device SERIAL, rea inspect-adb-display SERIAL, rea inspect-adb-window SERIAL, rea list-adb-processes SERIAL y rea read-adb-logcat SERIAL --count 200. Sus operaciones de instalación, inicio y cierre cambian estado; úsalas solo cuando formen parte explícita de la prueba.

## 8. Orden de verificación

1. Confirma paquete y actividad de prueba, sin tocar la app original.
2. Confirma que el contenedor cargó el perfil, resolución y driver esperados.
3. Compara la misma escena antes y después en el mismo display.
4. Verifica el marco de actividad y superficie completa.
5. Comprueba controles en el centro y cerca de las cuatro esquinas.
6. Revisa logs por crash y renderer real.
7. Mide tiempo de cuadro y FPS en juego sostenido. No uses el límite configurado como medición.
8. Repite una escena diferente para buscar recortes o errores de control.

## Reversión

La reversión del experimento consiste en desinstalar el paquete de prueba y reinstalar la versión de prueba anterior desde una copia local. No desinstales ni sobrescribas el paquete original. Conserva el directorio de datos del juego y los respaldos de partidas antes de cambiar rutas o configuraciones.
