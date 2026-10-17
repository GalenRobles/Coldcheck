import os, time
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient

load_dotenv()
llm = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])
tav = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
MODEL = os.environ["MODEL"]

SITUACION = "Se fue la luz durante 3 horas y el producto quedó a unos 28 °C. ¿Todavía se puede usar?"
PRODUCTOS = ["pluma de insulina sin abrir", "vacuna contra la influenza", "leche pasteurizada sin abrir"]

SYSTEM = ("Eres un asistente de apoyo para decidir si un producto refrigerado sigue siendo usable "
          "tras una excursión de temperatura. Responde en español con: VEREDICTO (VERDE/AMARILLO/ROJO), "
          "razones breves con cifras concretas y la incertidumbre que queda. Ante la duda, elige el "
          "veredicto más conservador. No eres un dispositivo médico.")

def ask(msg):
    t = time.time()
    r = llm.chat.completions.create(model=MODEL, temperature=0.2,
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": msg}])
    return r.choices[0].message.content, round(time.time() - t, 1)

def search(query, news=False):
    kw = dict(query=query, max_results=5, search_depth="advanced")
    if news:
        kw.update(topic="news", days=30)   # si da error, revisa los parámetros en la doc de Tavily
    return tav.search(**kw)["results"]

def fmt(results):
    return "\n\n".join(f"[{i+1}] {r['title']} ({r['url']})\n{r['content']}" for i, r in enumerate(results))

os.makedirs("out", exist_ok=True)
with open("out/resultados.md", "w", encoding="utf-8") as f:
    for p in PRODUCTOS:
        base = f"Producto: {p}. {SITUACION}"
        sin, t1 = ask(base)
        fuentes = search(f"{p} storage stability unrefrigerated temperature excursion manufacturer guidance")
        con, t2 = ask(f"{base}\n\nFUENTES:\n{fmt(fuentes)}\n\n"
                      "Usa SOLO estas fuentes para las cifras y cítalas como [n]. Si no cubren el caso, dilo.")
        alertas = search(f"{p} recall safety alert", news=True)
        f.write(f"# {p}\n\n## SIN Tavily ({t1}s)\n{sin}\n\n## CON Tavily ({t2}s)\n{con}\n\n## Fuentes\n{fmt(fuentes)}\n\n"
                "## Alertas recientes (titulares)\n" +
                "\n".join(f"- {r['title']} ({r['url']})" for r in alertas) + "\n\n---\n\n")
        print("listo:", p)