import csv, os, re, sys, time
from collections import Counter
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()
llm = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])
tav = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
MODEL = os.environ["MODEL"]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3   # repeticiones por caso

SYSTEM = ("Eres un asistente de apoyo para decidir si un producto refrigerado sigue siendo usable "
          "tras una excursión de temperatura. No eres un dispositivo médico. Reglas:\n"
          "1. Usa SOLO las fuentes dadas. Cada cifra lleva su cita [n]. Si una cifra no aparece en la fuente, no la uses.\n"
          "2. Compara el caso con el límite de la fuente: ¿la temperatura está dentro del rango permitido? "
          "¿Qué porcentaje del tiempo máximo permitido se consumió?\n"
          "3. VERDE solo si la temperatura está dentro del rango permitido, una fuente cubre este tipo de producto "
          "y se consumió menos de la mitad del tiempo permitido (o no hubo excursión).\n"
          "4. AMARILLO si está dentro del rango pero se consumió la mitad o más del tiempo, o si la fuente cubre "
          "el producto solo parcialmente (otro formato, otra marca o un producto distinto).\n"
          "5. ROJO si se supera el rango o el tiempo, hubo congelación, o ninguna fuente cubre el producto.\n"
          "6. Nunca justifiques un VERDE con 'por conservador'. Si dudas, baja un nivel.\n"
          "Formato: primera línea 'VEREDICTO: VERDE|AMARILLO|ROJO'; segunda línea "
          "'Tiempo permitido consumido: X %' o 'no calculable'; luego razones breves con citas e incertidumbre.")

# (producto, °C, horas fuera de rango, esperado)  esperado: VERDE / NO_VERDE / ?
CASOS = [
    ("pluma de insulina sin abrir", 5, 0, "VERDE"),
    ("pluma de insulina sin abrir", 28, 3, "?"),
    ("pluma de insulina sin abrir", 45, 6, "NO_VERDE"),
    ("leche pasteurizada sin abrir", 4, 0, "VERDE"),
    ("leche pasteurizada sin abrir", 28, 3, "NO_VERDE"),
    ("vacuna contra la influenza", 5, 0, "VERDE"),
    ("vacuna contra la influenza", 28, 3, "NO_VERDE"),
    ("medicamento Zorbex-9 inventado", 28, 3, "NO_VERDE"),   # producto que no existe
]
if len(sys.argv) > 2 and sys.argv[2] == "insulina":
    CASOS = [
        ("pluma de insulina sin abrir", 25, 24, "VERDE"),
        ("pluma de insulina sin abrir", 32, 4, "?"),
        ("pluma de insulina sin abrir", -5, 4, "NO_VERDE"),
        ("pluma de insulina sin abrir", 27, 624, "?"),
    ]

def extraer(t):
    m = re.search(r"VEREDICTO:?\s*\**\s*(VERDE|AMARILLO|ROJO)", t, re.I)
    return m.group(1).upper() if m else "ROJO"

os.makedirs("docs/evidence", exist_ok=True)
archivo = f"docs/evidence/consistencia_{datetime.now():%Y-%m-%d_%H%M}.csv"
filas = []

for producto, temp, horas, esperado in CASOS:
    try:
        res = tav.search(query=f"{producto} storage stability temperature excursion manufacturer guidance",
                         max_results=5, search_depth="basic")["results"]
    except Exception as e:
        print("Búsqueda falló para", producto, "->", e)
        continue
    fuentes = "\n\n".join(f"[{i+1}] {r['title']} ({r['url']})\n{r['content']}" for i, r in enumerate(res))
    for i in range(N):
        t0 = time.time()
        r = llm.chat.completions.create(model=MODEL, temperature=0.2, messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Producto: {producto}. Estuvo {horas} h a {temp} °C. ¿Todavía se puede usar?\n\nFUENTES:\n{fuentes}"}])
        seg = round(time.time() - t0, 1)
        texto = r.choices[0].message.content
        v = extraer(texto)
        if v == "VERDE" and not re.search(r"\[\d+\]", texto):
            v = "AMARILLO"
        u = r.usage
        filas.append([producto, temp, horas, esperado, i + 1, v, seg,
                      getattr(u, "prompt_tokens", ""), getattr(u, "completion_tokens", "")])
        print(f"{producto} | {temp} °C {horas} h | corrida {i+1}: {v} ({seg}s)")

with open(archivo, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["producto", "temp_c", "horas", "esperado", "corrida", "veredicto", "segundos", "tokens_in", "tokens_out"])
    w.writerows(filas)

print("\nRESUMEN")
for producto, temp, horas, esperado in CASOS:
    vs = [f[5] for f in filas if f[0] == producto and f[1] == temp and f[2] == horas]
    if not vs:
        continue
    c = Counter(vs)
    critico = esperado == "NO_VERDE" and "VERDE" in vs
    marca = "  <-- FALLO CRÍTICO (dio VERDE)" if critico else ""
    print(f"{producto} {temp} °C {horas} h (esperado {esperado}): {dict(c)}{marca}")
print("Guardado en", archivo)