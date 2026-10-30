# SmartMaintenance DB

A learning and portfolio prototype for industrial maintenance tracking.

## Current scope

- Equipment register
- Failure history
- Maintenance intervention log
- KPI overview (machine count, failure count, downtime, average downtime per failure)
- Downtime chart by machine
- SQLite database created locally on first run

## Technology

- Python
- Streamlit
- SQLite
- Pandas
- Plotly

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal (usually http://localhost:8501).

## Demo data

The first launch inserts 3 example machines and 6 simulated failures. These are fictional demonstration records, not measurements from real equipment.

The database file is created at `data/smartmaintenance.db`. It is excluded from Git by `.gitignore`; keep operational data and sensitive company data out of a public repository.

## Important limitations

This is an educational prototype, not a production CMMS. Current downtime averages are not a validated MTTR unless downtime equals actual repair duration. MTBF and availability are not calculated because operating hours and planned production time are not yet captured.

No PLC, OPC UA, MQTT, sensor, or machine connection is implemented yet. Those can be added later behind a dedicated data-acquisition layer.

## Roadmap

1. Add input validation and tests
2. Add preventive maintenance planning
3. Add MTTR using actual repair duration
4. Define operating hours to calculate MTBF and availability
5. Add export to CSV / Excel
6. Add an optional industrial data connector (OPC UA / MQTT) after security and equipment requirements are known
