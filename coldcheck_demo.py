import os, re, time
import serial
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()
llm = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])
tav = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
MODEL = os.environ["MODEL"]
PUERTO = os.getenv("COM_PORT", "COM7")
MAPA = {"VERDE": "G", "AMARILLO": "Y", "ROJO": "R"}

SYSTEM = ("Eres un asistente de apoyo para decidir si un producto refrigerado sigue siendo usable "
          "tras una excursión de temperatura. Responde en español con: VEREDICTO: (VERDE/AMARILLO/ROJO), "
          "razones breves citando las fuentes como [n], y la incertidumbre que queda. Usa SOLO las fuentes "
          "dadas para las cifras; si no cubren el caso, dilo. Ante la duda, elige el veredicto más "
          "conservador. No eres un dispositivo médico.")

def extraer(texto):
    m = re.search(r"VEREDICTO:?\s*\**\s*(VERDE|AMARILLO|ROJO)", texto, re.I)
    if not m:
        print("No encontré un veredicto claro: uso ROJO por precaución.")
        return "ROJO"
    return m.group(1).upper()

producto = input("Producto [pluma de insulina sin abrir]: ") or "pluma de insulina sin abrir"
temp = input("Temperatura en °C [28]: ") or "28"
horas = input("Horas fuera de rango [3]: ") or "3"

res = tav.search(query=f"{producto} storage stability temperature excursion manufacturer guidance",
                 max_results=5, search_depth="basic")["results"]
fuentes = "\n\n".join(f"[{i+1}] {r['title']} ({r['url']})\n{r['content']}" for i, r in enumerate(res))

t0 = time.time()
r = llm.chat.completions.create(model=MODEL, temperature=0.2, messages=[
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": f"Producto: {producto}. Estuvo {horas} h a {temp} °C. ¿Todavía se puede usar?\n\nFUENTES:\n{fuentes}"}])
texto = r.choices[0].message.content
print(texto, f"\n({round(time.time()-t0, 1)} s)\n")

v = extraer(texto)
print("Veredicto:", v)
try:
    with serial.Serial(PUERTO, 115200, timeout=2) as s:
        time.sleep(2)
        s.write(MAPA[v].encode())
        print("Placa respondió:", s.readline().decode(errors="ignore").strip())
except Exception as e:
    print("No pude hablar con la placa:", e)