# Resumen de Videos de YouTube con IA

Este script de Python utiliza IA para generar un resumen de cualquier video de YouTube a partir de su transcripción.

## Propósito

El objetivo principal de este script es proporcionar un resumen rápido y conciso de un video de YouTube. Extrae la transcripción del video, la envía a un modelo de lenguaje grande (LLM) a través de AWS Bedrock y muestra un resumen estructurado que incluye:

*   Un resumen ejecutivo.
*   Los puntos más importantes.
*   Las conclusiones principales.

Además, el script calcula y muestra el costo asociado con el uso del modelo de IA, proporcionando transparencia sobre el consumo de tokens.

## Características

*   Extrae automáticamente la transcripción de un video de YouTube.
*   Utiliza el modelo **Claude 3 Haiku** a través de **AWS Bedrock** para generar el resumen.
*   Maneja la selección de idioma de la transcripción (prioriza español, luego inglés).
*   Calcula y muestra el uso de tokens (entrada y salida) y el costo total de la operación.
*   Presenta la información de manera clara y legible en la consola, utilizando la librería `rich`.

## Requisitos

Para utilizar este script, necesitas tener lo siguiente:

1.  **Python 3.x** instalado.
2.  Las librerías de Python especificadas en el archivo `requirements.txt`. Puedes instalarlas con el siguiente comando:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Credenciales de AWS**: Debes tener tus credenciales de AWS configuradas en tu entorno. El script utiliza `boto3` y necesita permisos para acceder al servicio **Bedrock** en la región `us-east-1`.

## Uso

Para ejecutar el script, simplemente proporciona la URL de un video de YouTube como argumento en la línea de comandos:

```bash
python local.py "URL_DEL_VIDEO_DE_YOUTUBE"
```

### Ejemplo

```bash
python local.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

El script procesará el video y mostrará el resumen, la información del video y los costos directamente en tu terminal.
