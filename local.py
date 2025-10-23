import json
import boto3
from youtube_transcript_api import YouTubeTranscriptApi
import re
import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import box
from rich.text import Text

# Inicializar Rich Console
console = Console()

# Configura el cliente de Bedrock
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
ytt_api = YouTubeTranscriptApi()

def extract_video_id(url):
    """Extrae el ID del video de diferentes formatos de URL de YouTube"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
        r'youtube\.com\/embed\/([^&\n?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError("URL de YouTube invalida")

def get_transcript(video_id):
    """Obtiene la transcripcion del video"""
    try:
        transcript_list = ytt_api.list(video_id)
        try:
            transcript = transcript_list.find_transcript(['es', 'es-ES', 'es-MX'])
        except:
            transcript = transcript_list.find_transcript(['en', 'en-US'])
        transcript_data = transcript.fetch()
        full_text = ' '.join(getattr(entry, 'text', '') for entry in transcript_data)
        return full_text
    except Exception as e:
        raise Exception(f"Error al obtener transcripcion: {str(e)}")

def calculate_cost(input_tokens, output_tokens):
    """Calcula el costo basado en los tokens usados"""
    # Precios de Claude 3 Haiku en us-east-1
    PRICE_INPUT_PER_MILLION = 0.25  # USD
    PRICE_OUTPUT_PER_MILLION = 1.25  # USD
    
    cost_input = (input_tokens / 1_000_000) * PRICE_INPUT_PER_MILLION
    cost_output = (output_tokens / 1_000_000) * PRICE_OUTPUT_PER_MILLION
    total_cost = cost_input + cost_output
    
    return {
        'cost_input': cost_input,
        'cost_output': cost_output,
        'total_cost': total_cost
    }

def display_token_usage(input_tokens, output_tokens, costs):
    """Muestra las estad�sticas de uso de tokens y costos"""
    
    # Crear tabla de uso
    usage_table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.ROUNDED,
        border_style="cyan"
    )
    
    usage_table.add_column("Tipo", style="yellow", width=15)
    usage_table.add_column("Tokens", justify="right", style="white")
    usage_table.add_column("Costo (USD)", justify="right", style="green")
    
    usage_table.add_row(
        "\U0001f4e5 Input",
        f"{input_tokens:,}",
        f"${costs['cost_input']:.6f}"
    )
    usage_table.add_row(
        "\U0001f4e4 Output",
        f"{output_tokens:,}",
        f"${costs['cost_output']:.6f}"
    )
    usage_table.add_section()
    usage_table.add_row(
        "\U0001f4b5 TOTAL",
        f"{input_tokens + output_tokens:,}",
        f"[bold]${costs['total_cost']:.6f}[/bold]"
    )
    
    console.print(Panel(
        usage_table,
        title="[bold]\U0001f4ca Uso de Tokens y Costos[/bold]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()

def generate_summary_with_bedrock(transcript):
    """Genera resumen usando Claude en Bedrock"""
    
    prompt = f"""Analiza la siguiente transcripci�n de un video de YouTube y proporciona:
1. Un resumen ejecutivo (2-3 parrafos)
2. Los puntos mas importantes (lista de 5-7 puntos clave)
3. Conclusiones principales

Transcripcion:
{transcript}

Por favor, estructura tu respuesta de manera clara y concisa."""
    
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"
    
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    })
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=body
    )
    
    response_body = json.loads(response['body'].read())
    summary = response_body['content'][0]['text']
    
    # Obtener metricas de uso
    usage = response_body.get('usage', {})
    input_tokens = usage.get('input_tokens', 0)
    output_tokens = usage.get('output_tokens', 0)
    
    # Calcular costos
    costs = calculate_cost(input_tokens, output_tokens)
    
    return summary, input_tokens, output_tokens, costs

def display_summary(video_id, summary):
    """Muestra el resumen con formato elegante usando Rich"""
    
    # Banner principal
    console.print()
    title = Text("\U0001f4f9 RESUMEN DE VIDEO DE YOUTUBE", style="bold cyan")
    console.print(Panel(
        title,
        box=box.DOUBLE,
        border_style="bright_cyan",
        padding=(1, 2)
    ))
    
    # Informacion del video
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="bold yellow")
    info_table.add_column(style="white")
    info_table.add_row("\U0001f517 Video ID:", video_id)
    info_table.add_row("\U0001f517 URL:", f"https://youtube.com/watch?v={video_id}")
    
    console.print(Panel(
        info_table,
        title="[bold]Informacion del Video[/bold]",
        border_style="yellow",
        box=box.ROUNDED
    ))
    
    console.print()
    
    # Resumen en formato Markdown
    console.print(Panel(
        Markdown(summary),
        title="[bold green]\U0001f4dd Resumen Generado por IA[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    
    console.print()

def main():
    """Funcion principal para ejecucion local"""
    
    # Banner de inicio
    console.print("\n[bold magenta]\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550[/bold magenta]")
    console.print("[bold cyan]  YouTube Video Summarizer con AI  [/bold cyan]")
    console.print("[bold magenta]\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550[/bold magenta]\n")
    
    if len(sys.argv) < 2:
        console.print("[red]\u274c Error:[/red] Debes proporcionar una URL de YouTube", style="bold")
        console.print("[yellow]Uso:[/yellow] python local.py <URL_de_YouTube>")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # 1. Extraer video ID
            task1 = progress.add_task("[cyan]Extrayendo ID del video...", total=None)
            video_id = extract_video_id(youtube_url)
            progress.update(task1, completed=True)
            console.print(f"[green]\u2713[/green] Video ID: [bold]{video_id}[/bold]")
            
            # 2. Obtener transcripci�n
            task2 = progress.add_task("[cyan]Obteniendo transcripcion del video...", total=None)
            transcript = get_transcript(video_id)
            progress.update(task2, completed=True)
            console.print(f"[green]\u2713[/green] Transcripci�n obtenida ([bold]{len(transcript):,}[/bold] caracteres)")
            
            # 3. Generar resumen con Bedrock
            task3 = progress.add_task("[cyan]Generando resumen con Claude AI...", total=None)
            summary, input_tokens, output_tokens, costs = generate_summary_with_bedrock(transcript)
            progress.update(task3, completed=True)
            console.print("[green]\u2713[/green] Resumen generado exitosamente\n")
        
        # 4. Mostrar resumen con formato elegante
        display_summary(video_id, summary)
        
        # 5. Mostrar estadisticas de uso y costos
        display_token_usage(input_tokens, output_tokens, costs)
        
        # Footer con informacion del modelo
        footer_text = Text()
        footer_text.append("Powered by ", style="dim")
        footer_text.append("AWS Bedrock", style="bold cyan")
        footer_text.append(" (", style="dim")
        footer_text.append("Claude 3 Haiku", style="bold yellow")
        footer_text.append(") \U0001f680", style="dim")
        console.print(footer_text)
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]\u274c Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
