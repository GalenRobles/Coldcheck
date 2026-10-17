python coldcheck_demo.py                                   
Producto [pluma de insulina sin abrir]:
Temperatura en °C [28]:                                                             
Horas fuera de rango [3]: 
VEREDICTO: VERDE  
Razones:
- La guía actualizada de Novo Nordisk permite almacenar insulinas sin abrir hasta 30 °C durante cuatro semanas antes de su uso [1].
- La FDA indica que los productos de insulina (viales o cartuchos, abiertos o sin abrir) pueden permanecer sin refrigeración entre 59 °F y 86 °F (≈15‑30 °C) hasta 28 días sin perder eficacia [4].
- Datos de fabricantes recopilados por Cochrane muestran que la insulina sin abrir tolera hasta 37 °C durante dos meses con pérdida mínima de actividad [2].
- Tu pluma estuvo solo 3 h a 28 °C, muy por debajo de los límites de temperatura y tiempo permitidos.

Incertidumbre: no se conoce la marca exacta, pero todas las fuentes cubren insulinas humanas en cartuchos/plumas sin abrir; ante la duda, el veredicto conservador sigue siendo VERDE.
(2.9 s)

Veredicto: VERDE
Placa respondió: OK:G
(.venv) PS C:\coldcheck> python coldcheck_demo.py
Producto [pluma de insulina sin abrir]:      
Temperatura en °C [28]: 
Horas fuera de rango [3]: 
VEREDICTO: VERDE  
Razones:
- La FDA y guías de almacenamiento seguro indican que la insulina sin abrir (vialeso cartuchos) puede permanecer sin refrigerar entre 59 °F y 86 °F (15‑30 °C) hasta 28 días sin perder eficacia [3][4].
- Cochrane reporta que los fabricantes han mostrado estabilidad a 25 °C hasta 6 meses y a 37 °C hasta 2 meses con pérdida mínima de actividad [2].
- Novo Nordisk ha extendido la etiqueta a 30 °C por 4 semanas antes de abrir [1].   
- 3 horas a 28 °C (82 °F) están muy por debajo de esos límites de tiempo y temperatura.

Incertidumbre: La etiqueta del producto concreto podría tener instrucciones más restrictivas; si el fabricante especifica un rango menor, seguir esa indicación. No se consideran aquí exposición a luz directa, congelación ni manipulación fuera del cartucho original.
(2.6 s)

Veredicto: VERDE
Placa respondió: OK:G
(.venv) PS C:\coldcheck> python coldcheck_demo.py
Producto [pluma de insulina sin abrir]: leche pasteurizada sin abrir
Temperatura en °C [28]: 
Horas fuera de rango [3]: 
VEREDICTO: ROJO  
Razones:
- La única fuente que aborda leche pasteurizada tradicional (no UHT) indica que **no se debe dejar nunca la leche fuera del refrigerador** y que **por cada hora por encima de 45 °F (≈7 °C) se pierde un día de vida útil** [1].
- A 28 °C (82 °F) la leche está muy por encima de ese umbral; 3 h en esa zona de peligro implican una reducción significativa de vida útil y riesgo de crecimiento bacteriano.
- Las demás fuentes tratan leche humana (con propiedades antibacterianas distintas)y no son aplicables a leche pasteurizada de vaca [2,4,5].
- La fuente [3] solo da tiempos de refrigeración/congelación, sin límite explícito a temperatura ambiente.

Incertidumbre: Las fuentes no proporcionan un límite de seguridad duro (p. ej., “máximo 2 h a 28 °C”) para leche pasteurizada cerrada; la regla del “día por hora” de [1] se refiere a vida útil, no a seguridad inmediata. Por conservación, se descarta.
(4.8 s)

Veredicto: ROJO
Placa respondió: OK:R
(.venv) PS C:\coldcheck> python coldcheck_demo.py
Producto [pluma de insulina sin abrir]: vacuna contra la influenza
Temperatura en °C [28]: 
Horas fuera de rango [3]: 
VEREDICTO: ROJO  
Razones:
- El rango correcto es 2–8 °C; 28 °C durante 3 h supera ampliamente el límite y el tiempo permitido (fuente [1]: >8 °C ≤20 min sin acción; aquí 3 h).
- Todo excursion fuera de rango obliga a etiquetar “No usar”, documentar y contactar al fabricante/programa de inmunización antes de decidir (fuentes [2], [3], [4]).
- Ninguna fuente dada avala la viabilidad tras 3 h a 28 °C; la estabilidad depende de datos del fabricante que no se aportan.
Incertidumbre: El fabricante podría tener datos de estabilidad que permitan su uso,pero sin esa confirmación expresa no debe administrarse.
(2.9 s)

Veredicto: ROJO
Placa respondió: OK:R