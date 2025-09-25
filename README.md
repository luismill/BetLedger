# BetLedger

BetLedger es una aplicación de escritorio escrita en Python y PySide6 para gestionar operaciones deportivas con coberturas entre un proveedor de origen y un exchange de contraposición. El proyecto incluye una calculadora financiera, gestión de cuentas y saldos, registro y liquidación de operaciones, seguimiento de incentivos, dashboard con indicadores, backups automáticos y exportación/importación en CSV.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.data.seed  # crea la base de datos con datos demo
python -m src.app
```

## Funcionalidades clave

* Calculadora de coberturas (`calificacion` y `credito_no_retorno`) con redondeo financiero y validación de tick-size.
* Gestión de cuentas con transacciones clasificadas (`deposit`, `withdrawal`, `op_lock`, `op_settlement`, etc.).
* Registro de operaciones con bloqueos de fondos y liquidaciones automáticas (`GANA_A`, `GANA_B`, `ANULADA`).
* Seguimiento de incentivos vinculados a cuentas.
* Dashboard con KPIs (beneficio total, ROI, número de operaciones, saldo total) y evolución temporal.
* Módulo comparador de precios con fuentes CSV/HTTP (sin scraping por defecto).
* Backups diarios del fichero SQLite conservando siete días.
* i18n sencilla con ficheros `locales/es.json` y `locales/en.json`.

## Casos de prueba manuales

Los siguientes escenarios ayudan a validar manualmente los cálculos de la calculadora:

### Calificación
1. `stake_a=25`, `odds_a=2.0`, `odds_b=2.1`, `commission_b=5%` → `hedge_stake_b≈24.39`, `exposure_b≈26.83`, pérdida esperada ≈ `1.83`.
2. `stake_a=10`, `odds_a=3.5`, `odds_b=3.6`, `commission_b=2%` → pérdida esperada < `0.5`.
3. `stake_a=50`, `odds_a=1.9`, `odds_b=1.95`, `commission_b=0%` → pérdida esperada < `1.0`.

### Crédito no retorno
1. `stake_a=20`, `odds_a=5.0`, `odds_b=5.2`, `commission_b=5%` → beneficio esperado ≈ `18.0`.
2. `stake_a=30`, `odds_a=4.5`, `odds_b=4.6`, `commission_b=0%` → beneficio esperado > `65`.
3. `stake_a=15`, `odds_a=7.0`, `odds_b=7.4`, `commission_b=5%` → rendimiento > `0.7`.

## Scripts de build

Se incluyen scripts básicos para empaquetar con PyInstaller:

```bash
pyinstaller --name BetLedger --windowed --onefile src/app.py
```

## Tests automatizados

Ejecutar todas las comprobaciones con:

```bash
pytest -q
```

Los tests cubren la calculadora, validaciones de tick-size, gestión de cuentas, ciclo de vida de operaciones, backups y seguridad de redondeo.
