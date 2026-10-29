# Fuentes y herramientas

## Herramientas observadas en el caso

- Apktool 3.0.3 local: decodificación y reconstrucción del APK.
- ADB: consulta del paquete, configuración privada del contenedor, procesos, actividad, logs y capturas.
- REA CLI 6.5.0: soporte para inspección y evidencia de APK/dispositivo; depende del ADB que ya tenga el operador.
- FFmpeg: conversión puntual de recursos cuyo sufijo decía .png pero cuya firma no era PNG.
- Android SDK Build Tools: necesarios para alinear y firmar una reconstrucción local.

REA complementa ADB; no reemplaza ni administra el transporte del dispositivo. Sus operaciones de captura y lectura pueden ser de solo lectura, mientras que instalar, iniciar, detener y desinstalar una app cambian estado. Revisa la documentación de cada operación.

## Referencias externas

- [REA: análisis de dispositivos Android por ADB](https://github.com/morluto/rea/blob/main/docs/adb-device-analysis.md)
- [REA: inspección estática de APK Android](https://github.com/morluto/rea/blob/main/docs/android-analysis.md)
- [Apktool: documentación oficial](https://apktool.org/docs/)
- [LSFG-Android: release 0.1.2](https://github.com/FrankBarretta/LSFG-Android/releases/tag/0.1.2)
- [LSFG-Android: repositorio y README](https://github.com/FrankBarretta/LSFG-Android)
- [Android: MediaProjection](https://developer.android.com/media/grow/media-projection)
- [Android: hacer una app fold-aware](https://developer.android.com/develop/adaptive-apps/guides/foldables/make-your-app-fold-aware)

## Usar REA con criterio

Antes de una sesión, vuelve a descubrir serial, modelo, versión Android, actividad, display y paquetes. Guarda la salida como evidencia local fuera del repo. No publiques seriales ADB, logs completos, dumps del dispositivo, rutas privadas, listas de archivos personales o identificadores de cuenta.
