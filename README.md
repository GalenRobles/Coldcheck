# ColdCheck

**After a power cut, can I still use this?** ColdCheck is a Physical AI prototype that decides whether a cold-chain product (insulin pen, vaccine, milk) is still usable after a temperature excursion. It searches for live evidence with **Tavily**, extracts storage rules with **NVIDIA Nemotron** on **Nebius Token Factory**, verifies every rule against its source in code, and shows the verdict on real hardware: a traffic light with a buzzer, an LED matrix and a live temperature sensor.

> Prototype built solo for the Nebius x NVIDIA Global AI Hackathon, **Physical AI** track.
> **This is not a medical device.** It is a decision-support experiment. Always follow the manufacturer's guidance and ask a pharmacist or doctor.

<!-- TODO: demo video link, Devpost link, photo of the hardware -->

## Status

| Verified on hardware | Implemented, not yet verified on hardware | Not built yet |
|---|---|---|
| Traffic light + buzzer driven by serial letters (Arduino Uno) | Live loop `demo_vivo.py`: real temperature -> accumulated exposure -> verdict -> both boards (tested only with a simulated serial port) | Web dashboard and replay mode |
| LED matrix shows the verdict letter (Arduino UNO Q) | Sensor calibration with an ice bath | Door-open detection (ultrasonic) |
| NTC 10K temperature readout over serial (stable 19.5-19.6 C in a 20 s test) | | Product selection with the keypad |
| Tavily search -> Nemotron rule extraction -> code verification -> verdict, with real API calls | | Triage tier with Nemotron Super |

## How it works

```
 at start (once per product)
   Tavily search  ->  Nemotron Nano extracts rules as JSON
                      (temperature, duration, unit, source, exact quote)
                      if no rule can be verified -> escalate to Nemotron Ultra
   code verifies each rule: the quote must exist in the source and contain the
   temperature and the duration; the unit is converted to hours in code

 every second
   NTC sensor (Arduino Uno) -> temperature -> exposure time while above 8 C
   code judges the case against EVERY verified rule -> GREEN / YELLOW / RED
   -> letter G / Y / R to the traffic light (Uno) and the LED matrix (UNO Q)
```

**Decision rules (all in code, not in the prompt):**
- 2-8 C: GREEN, no model is called. 0 C or below: RED (freezing).
- Above 8 C: the case is evaluated against every verified rule.
  GREEN only if it meets all of them with less than half of the time used;
  RED only if it exceeds all of them or no rule can be verified;
  YELLOW if the sources disagree or half of the time or more is used.
- A rule that cannot be verified against its source is discarded. No verifiable evidence means RED.
- If the sensor fails 3 readings in a row, the result is RED.

**Models:** Nemotron Nano extracts the rules; Nemotron Ultra is used only when Nano's output cannot be verified. Nemotron Super is not used yet.

**Simulated time:** a real excursion lasts hours, so `demo_vivo.py --acel N` counts each real second above 8 C as `N` seconds of exposure. The elapsed time in the demo is **simulated**; the temperature is real.

## Repository layout

```
nucleo.py             extraction, verification and decision logic
demo.py               one-shot verdict (typed temperature and hours), optional boards
demo_vivo.py          live demo with the real sensor
evals/consistencia.py repeats cases and writes CSV evidence to docs/evidence/
evals/prueba_tavily.py   first with/without-search comparison
tools/                hardware helpers (read temperature, test the traffic light)
firmware/             Arduino sketches (semaforo_ntc, matriz_uno_q)
docs/                 evidence, hackathon checklist, feedback draft
archive/              earlier versions kept for reference
```

## Hardware

| Part | Role |
|---|---|
| Arduino Uno (clone) | Traffic light: green D13, yellow D12, red D11, buzzer D10; NTC 10K on A0 |
| NTC 10K waterproof probe + 8.2 kOhm fixed resistor | 5V -> NTC -> A0 -> 8.2k -> GND |
| Arduino UNO Q | Shows the verdict letter on its LED matrix |
| Laptop | Runs Python and talks to both boards over USB serial (115200 baud) |

## Setup

Requirements: Python 3.12+, both boards on USB, a Nebius Token Factory key and a Tavily key.

```powershell
git clone https://github.com/GalenRobles/coldcheck.git
cd coldcheck
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env     # then fill in your keys; never commit .env
```

Upload `firmware/semaforo_ntc` to the Arduino Uno and `firmware/matriz_uno_q` to the UNO Q (it needs the ArduinoGraphics library). Close any serial monitor before running the scripts.

## Run

```powershell
python demo.py --sin-placas                 # verdict only, no boards
python demo.py                              # verdict + letters to the boards
python tools/leer_temp.py COM8 20           # check the temperature readout
python demo_vivo.py --acel 28800            # live demo: 1 real second = 8 simulated hours
python evals/consistencia.py 3              # repeat every case 3 times, write CSV evidence
```

## Evidence

Raw CSV files are in `docs/evidence/`. All runs use one Tavily search per product reused across repetitions, so they measure model variability, not search variability. Expected outcomes are the author's conservative expectations, not clinical ground truth.

**Prompt-only version (44 runs, Nemotron Ultra decides the color):** no GREEN in clearly dangerous cases, but insulin at 32 C for 4 h was GREEN in 2 of 5 runs, which should not happen if the sources set 30 C as the limit.

**Decision layer, first run (36 runs, earlier iteration with min/max rules):** no GREEN in any case expected to be non-green; insulin at 32 C for 4 h became YELLOW 3 of 3; insulin at 25 C for 24 h was RED in 1 of 3 runs (a false alarm caused by an unstable extraction); an invented product was RED 3 of 3 with no verifiable rules. Nano extraction time dropped from 10-33 s to 0.6-2.7 s after shortening quotes and excluding irrelevant rules (two changes at once).

The later iterations (per-rule evaluation, unit conversion in code, duration verification) have not been re-measured yet.

## Limits

| This prototype shows | It does not show |
|---|---|
| The pipeline from live sources to a physical verdict works | That the verdicts are medically correct |
| Verdicts were stable in most cases tested | Stability beyond 3-5 runs per case or across different searches |
| It refuses to invent safety for an unknown product | That it works for brands, lots or formats it has not been tested on |
| Decisions after setup take no model calls | Real-time guarantees for the LLM step: hard limits belong in firmware |

Other limits: search results can be off-topic; rule verification checks that the quote exists and contains the numbers, not that the rule applies to the exact product; sensor accuracy depends on calibration (ice-bath check pending).

## Models and tools

- **Nebius Token Factory** (OpenAI-compatible API) with **NVIDIA Nemotron-3 Nano** and **Nemotron-3 Ultra**.
- **Tavily** for live search of storage guidance.
- Arduino Uno and Arduino UNO Q, Python with `pyserial`.

## License

MIT. See `LICENSE`.
