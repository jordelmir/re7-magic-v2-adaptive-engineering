# Arquitectura y diagnóstico

## Alcance del cambio

El paquete Android funciona como contenedor para ejecutar un binario de Windows. La configuración observada identifica FEXCore y Box64, DXVK/VKD3D y un renderer Vulkan. Por eso “redimensionar el APK” significa corregir la transformación de superficie y entrada de la capa Android del contenedor. No significa portar el motor del juego a Android.

El cambio se hizo sobre un paquete de prueba:

- Paquete original observado: com.biohazard7.re7
- Paquete de prueba: com.biohazard7.re7.adaptive
- Etiqueta de prueba: RE7 Adaptive Test
- Versión final de prueba observada: 1.1-re7-v38-70-test

El identificador diferente permitió instalar el experimento junto al original y mantener separadas sus preferencias y datos privados de aplicación. Los archivos del juego permanecieron en almacenamiento compartido.

## Separar tres clases de franjas

Antes de cambiar código, clasifica las bandas:

1. **Letterbox de Android:** queda fuera del marco de la actividad. Se investiga con dumpsys window y el área de actividad.
2. **Barras del renderer o del contenedor:** la actividad ocupa el área disponible, pero el rectángulo de render respeta una proporción distinta.
3. **Barras dibujadas por el propio juego:** forman parte de la escena o de una secuencia cinematográfica.

Una captura del dispositivo no basta por sí sola. Compara el marco de actividad, la superficie de la ventana, el rectángulo de render y la captura. El parche de este caso actuó en la transformación de vista del contenedor. No cambió la política global de tamaño o densidad del teléfono.

## Causa en la transformación

La clase ViewTransformation recibía el tamaño exterior del lienzo y el tamaño interior de la imagen. La escala elegida era el mínimo entre la escala horizontal y vertical:

~~~text
scaleX = outerWidth / innerWidth
scaleY = outerHeight / innerHeight
scale = min(scaleX, scaleY)
~~~

Ese cálculo implementa contain: muestra la imagen completa, conserva su proporción y deja espacio vacío en el eje que no coincide.

La corrección reemplazó min por max:

~~~text
scale = max(scaleX, scaleY)
renderWidth  = ceil(innerWidth  * scale)
renderHeight = ceil(innerHeight * scale)
offsetX = (outerWidth  - renderWidth)  / 2
offsetY = (outerHeight - renderHeight) / 2
~~~

El render cubre así el lienzo y se centra. Cuando las proporciones no coinciden, offsetX u offsetY es negativo y el exceso queda recortado. La imagen no se estira, aunque parte del borde original puede quedar fuera de pantalla. Para llenar una proporción distinta sin recortar, el juego tendría que exponer una cámara o un viewport que admita esa proporción.

## Causa del joystick y mapeo táctil

El control TouchpadView.updateXform seleccionaba una rama distinta cuando la superficie estaba en pantalla completa. La rama de pantalla completa escalaba los eventos de forma distinta de la transformación del renderer. Después de aplicar cover, eso podía desalinear el toque respecto del punto visible.

El parche conserva el tamaño del método y neutraliza la bifurcación específica de esta versión para que la ruta de pantalla completa aplique la traslación y escala inversa de la imagen recortada. La guía no presenta ese cambio de Smali como universal: aplica solo si el método de la versión analizada conserva la misma condición y estructura. El script verifica los anclajes y falla si no coinciden.

## Flujo de render y prueba

~~~mermaid
flowchart TD
    APK[APK del contenedor] --> SMALI[Smali: ViewTransformation]
    SMALI --> SCALE[Escala cover centrada]
    SCALE --> SURFACE[Superficie disponible del Magic V2]
    TOUCH[Toque físico] --> MAP[Transformación inversa]
    MAP --> GAME[Coordenada del juego]
    SURFACE --> FRAME[Captura de escena y HUD]
    GAME --> FRAME
~~~

Mantén constantes la escena, orientación, postura del teléfono, driver y ajustes al comparar. Cambia una variable por iteración. Comprueba al menos menú y juego, y revisa que los botones táctiles sigan donde se ven.

## Qué no cambia este parche

- No elimina franjas que el propio juego dibuja.
- No amplía por sí solo el campo de visión ni modifica la cámara del juego.
- No mejora por sí solo los FPS.
- No convierte el port en una app Android nativa.
- No prueba que el driver configurado se haya cargado correctamente en una ejecución; esa conclusión requiere evidencia del runtime.
