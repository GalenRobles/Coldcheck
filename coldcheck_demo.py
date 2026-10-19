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
if v == "VERDE" and not re.search(r"\[\d+\]", texto):
    v = "AMARILLO"
    print("Verde sin ninguna fuente citada: lo bajo a AMARILLO.")
print("Veredicto:", v)
puertos = [p.strip() for p in os.getenv("COM_PORTS", "COM7").split(",") if p.strip()]
print("Puertos que voy a usar:", puertos)
for puerto in puertos:
    try:
        with serial.Serial(puerto, 115200, timeout=3) as s:
            time.sleep(3)              # el Uno clásico se reinicia al abrir el puerto
            s.reset_input_buffer()
            s.write(MAPA[v].encode())
            s.flush()
            resp = s.readline().decode(errors="ignore").strip()
            print(f"{puerto}: {'OK -> ' + resp if resp else 'sin respuesta de la placa'}")
    except Exception as e:
        print(f"{puerto}: ERROR -> {e}")