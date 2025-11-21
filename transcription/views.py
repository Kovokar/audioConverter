from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import whisper
import google.generativeai as genai
import os

# Carregar modelo Whisper uma vez
whisper_model = whisper.load_model("base")

# Configurar Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')

def correct_with_gemini(text):
    """Corrige o texto usando Gemini"""
    print("\n\n",text, "\n\n")
    prompt = f"""
Você está corrigindo uma transcrição de um laudo médico. 
Corrija APENAS erros evidentes de digitação, ortografia, gramática, concordância, acentuação e pontuação.

IMPORTANTE:
- Mantenha o sentido original e preserve ao máximo as palavras usadas.
- Não reescreva o texto por completo.
- Não altere informações clínicas.
- Não interprete o exame.
- Não invente dados.
- Apenas corrija o que estiver claramente errado.
- Quando houver frases quebradas, una-as de forma natural e mínima.
- Estruture o texto apenas quando for evidente que se tratam de seções (“Análise:”, “Considerações:”, etc.).
Texto a corrigir:
{text}
Responda APENAS com o texto corrigido, sem explicações adicionais.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        print("\n\n",response.text, "\n\n")
        return response.text
    except Exception as e:
        print(f"Erro no Gemini: {e}")
        return text  # Retorna o texto original se houver erro

@csrf_exempt
@require_http_methods(["POST"])
def transcribe_audio(request):
    
    
    # modelos = listar_modelos_gemini(settings.GEMINI_API_KEY)

    # for m in modelos:
    #     print(f"- {m['name']}")
        
    # return JsonResponse({'modelos': modelos})
        
    if 'audio' not in request.FILES:
        return JsonResponse({'error': 'Nenhum arquivo enviado'}, status=400)
    
    audio_file = request.FILES['audio']
    
    # Salvar temporariamente
    temp_path = f'/tmp/{audio_file.name}'
    with open(temp_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    
    try:
        # Transcrever com Whisper
        result = whisper_model.transcribe(temp_path, language='pt')
        transcription = result['text']
        
        # Corrigir com Gemini
        corrected_text = correct_with_gemini(transcription)
        
        return JsonResponse({
            'transcription': transcription,
            'corrected_text': corrected_text,
            'success': True
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Limpar arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
def listar_modelos_gemini(api_key):
    """Lista modelos disponíveis e que suportam generateContent"""
    genai.configure(api_key=api_key)

    try:
        modelos = genai.list_models()
    except Exception as e:
        print("Erro ao listar modelos:", e)
        return []

    modelos_validos = []

    for m in modelos:
        # Apenas modelos que suportam generateContent
        if "generateContent" in m.supported_generation_methods:
            modelos_validos.append({
                "name": m.name,
                "description": getattr(m, "description", ""),
                "generation_methods": m.supported_generation_methods
            })

    return modelos_validos