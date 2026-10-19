# ColdCheck

**After a power cut, can I still use this?** ColdCheck is a Physical AI prototype that decides whether a cold-chain product (insulin pen, vaccine, milk) is still usable after a temperature excursion. It searches for live evidence with **Tavily**, reasons over it with **NVIDIA Nemotron** on **Nebius Token Factory**, cites its sources, and shows the verdict on real hardware: a traffic light with a buzzer and an LED matrix.

> Prototype built solo for the Nebius x NVIDIA Global AI Hackathon, **Physical AI** track.
> **This is not a medical device.** It is a decision-support experiment. Always follow the manufacturer's guidance and ask a pharmacist or doctor.

<!-- TODO: add demo video link, Devpost link and a photo of the hardware -->

## Status

| Works today | Not built yet |
|---|---|
| Tavily search -> Nemotron verdict with citations -> serial command to two boards | Real temperature sensor (currently temperature and hours are typed in) |
| Traffic light + buzzer (Arduino Uno) and LED matrix (Arduino UNO Q) driven by the verdict | Door-open detection (ultrasonic) and product selection (4x4 keypad) |
| Fail-safe rules in code (see below) | Tiered routing Nano / Super / Ultra |
| Consistency test harness that writes CSV evidence to `docs/evidence/` | Code-side decision layer and claim auditor |
| | Web dashboard and deployed demo |

## How it works

```
 product + temperature + hours
              |
              v
     Tavily search (storage stability, manufacturer guidance)
              |
              v
     Nemotron-3-Ultra on Nebius Token Factory
     -> VERDICT (GREEN / YELLOW / RED) + reasons with [n] citations
              |
              v
     fail-safe rules in code
              |
      +-------+--------+
      v                v
 Arduino Uno       Arduino UNO Q
 traffic light     LED matrix
 + buzzer          (G / Y / R)
```

**Fail-safe rules (in code, not in the prompt):**
- If the verdict cannot be parsed, the result is **RED**.
- A **GREEN** with no citation at all is lowered to **YELLOW**.
- If a board cannot be reached, the script says so instead of failing silently.

## Hardware

| Part | Role |
|---|---|
| Arduino Uno (clone, CH340) | Traffic light: green D13, yellow D12, red D11, buzzer D10 (LEDs with resistors) |
| Arduino UNO Q | Shows the verdict letter on its LED matrix |
| Laptop | Runs the Python script and talks to both boards over USB serial (115200 baud) |

Firmware lives in `firmware/` (one sketch per board). The sketches read a single letter (`G`, `Y` or `R`) and answer `OK:<letter>`.

## Setup

Requirements: Python 3.12+, both boards connected by USB, a Nebius Token Factory API key and a Tavily API key.

```powershell
git clone https://github.com/<galenrobles>/coldcheck.git
cd coldcheck
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install pyserial openai tavily-python python-dotenv
```

Create a `.env` file (never commit it; it is in `.gitignore`):

```
NEBIUS_BASE_URL=<base URL shown in your Token Factory dashboard>
NEBIUS_API_KEY=<your key>
TAVILY_API_KEY=<your key>
MODEL=nvidia/Nemotron-3-Ultra-550b-a55b
COM_PORTS=COM7,COM8
```

Upload the sketches in `firmware/` to each board, then close any serial monitor (it locks the port).

## Run

```powershell
python coldcheck_demo.py
```

The script asks for the product, the temperature and the hours out of range (press Enter for the defaults), prints the verdict with its sources, and sends the letter to every port listed in `COM_PORTS`.

## Evidence

`consistencia.py` repeats each case several times and saves a CSV with verdict, latency and tokens in `docs/evidence/`.

```powershell
python consistencia.py 3            # full suite, 3 runs per case
python consistencia.py 5 insulina   # insulin edge cases, 5 runs per case
```

Results with prompt v2 (Nemotron-3-Ultra, one Tavily search per case, 44 runs):

| Case | Verdicts |
|---|---|
| Insulin 5 C, 0 h | GREEN x3 |
| Insulin 25 C, 24 h | GREEN x5 |
| Insulin 28 C, 3 h | GREEN x3 |
| Insulin 32 C, 4 h | GREEN x2, YELLOW x3 (unstable, open problem) |
| Insulin 45 C, 6 h | RED x3 |
| Insulin -5 C, 4 h | RED x5 |
| Insulin 27 C, 624 h | RED x5 |
| Milk 4 C, 0 h | GREEN x3 |
| Milk 28 C, 3 h | RED x3 |
| Vaccine 5 C, 0 h | GREEN x3 |
| Vaccine 28 C, 3 h | RED x3 |
| Invented product, 28 C, 3 h | RED x3 |

The first prompt version gave a false RED for milk at 4 C and a GREEN for insulin at 27 C / 624 h, which motivated the stricter prompt and the fail-safe rules. The raw CSV files are in `docs/evidence/`.

## Limits

| This prototype shows | It does not show |
|---|---|
| The pipeline from live sources to a physical verdict works end to end | That the verdicts are medically correct |
| Verdicts were stable in most of the cases above | Stability beyond 3-5 runs per case, or across different searches |
| The system refuses to invent safety for an unknown product | That it works for brands, lots or formats it has not been tested on |
| Latency of a few seconds per decision | A latency guarantee: LLM calls are not real time, so hard limits belong in firmware |

Other limits: expected results in the test file are conservative expectations by the author, not clinical ground truth; sources returned by search can be off-topic and are not yet audited automatically; temperature and hours are manual inputs until the sensor is added.

## Models and tools

- **Nebius Token Factory** (OpenAI-compatible API) with **NVIDIA Nemotron-3-Ultra**.
- **Tavily** for live search of storage guidance and manufacturer information.
- Arduino Uno and Arduino UNO Q, Python with `pyserial`.

## Roadmap

1. Real temperature sensor and door-open detection.
2. Model extracts limits from sources as JSON; code compares them with the measured values and decides the color.
3. Nano/Super for fast triage and claim auditing, Ultra only for ambiguous cases.
4. Dashboard with a replay mode, so the project can be seen without the hardware.

## License

MIT. See `LICENSE`.
