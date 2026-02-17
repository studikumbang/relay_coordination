# Relay Coordination Package

Professional ETAP-style protection coordination simulation library for Pandapower.

## Features

- **Relay Modeling**: IEC 60255, IEEE C37, IEC 61363 curves
- **Analysis**: Short circuit (IEC 60909) and Coordination analysis
- **Reporting**: Automatic CSV generation and TCC plotting
- **Easy API**: Simple integration with pandapower networks

## Installation

```bash
pip install relay_coordination
```

## API Reference

### 1. Device Creation

#### `add_ct(net, ...)`
Adds a Current Transformer to the network.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `net` | `pandapowerNet` | Required | The network object |
| `bus` | `int` | Required | Bus index where CT is located |
| `element` | `int` | Required | Index of the protected element (line/trafo) |
| `element_type` | `str` | Required | Type of element ("line", "trafo", "load") |
| `primary_rating` | `float` | Required | CT primary current (e.g., 200) |
| `secondary_rating` | `float` | 5.0 | CT secondary current (1 or 5) |
| `accuracy_class` | `str` | "5P20" | IEC/ANSI accuracy class |
| `burden_va` | `float` | 15.0 | Rated burden in VA |
| `name` | `str` | None | Name of the CT |

#### `add_relay(net, ...)`
Adds a Protection Relay connected to a CT.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `net` | `pandapowerNet` | Required | The network object |
| `ct` | `CT` | Required | Associated CT object |
| `cb` | `CircuitBreaker` | Required | Associated Circuit Breaker object |
| `manufacturer` | `str` | "Generic" | Relay manufacturer |
| `model` | `str` | "Overcurrent" | Relay model |
| **Phase Protection** | | | |
| `phase_pickup` | `float` | None | Pickup setting (A) |
| `phase_curve` | `str` | "IEC_NI" | Curve type (IEC_NI, IEEE_MI, etc.) |
| `phase_tms` | `float` | None | Time Multiplier Setting |
| `phase_inst_pickup` | `float` | None | Instantaneous pickup (A) |
| `phase_inst_delay` | `float` | 0.0 | Instantaneous time delay (s) |
| **Ground Protection** | | | |
| `ground_pickup` | `float` | None | Ground pickup setting (A) |
| `ground_curve` | `str` | "IEC_NI" | Curve type |
| `ground_tms` | `float` | None | Time Multiplier Setting |
| `ground_inst_pickup` | `float` | None | Ground instantaneous pickup (A) |

#### `add_cb(net, ...)`
Adds a Circuit Breaker.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `net` | `pandapowerNet` | Required | The network object |
| `bus` | `int` | Required | Bus index |
| `rated_voltage_kv` | `float` | Required | Rated voltage (kV) |
| `continuous_current_a` | `float` | Required | Rated continuous current (A) |
| `interrupting_rating_ka_sym` | `float` | Required | Symmetrical interrupting rating (kA) |
| `operating_time_cycles` | `float` | 5.0 | Opening time in cycles (at 60Hz) |
| `cb_type` | `str` | "VCB" | Type (VCB, ACB, OCB) |

### 2. Analysis Functions

#### `run_coordination_analysis(net, ...)`
Tests coordination between protective devices.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `net` | `pandapowerNet` | Required | The network object |
| `test_currents` | `List[float]` | None | List of fault currents to test (A) |
| `fault_type` | `str` | "phase" | "phase" or "ground" |
| `export_csv` | `bool` | True | Save results to CSV |
| `output_dir` | `str` | "data" | Output directory for CSV |

#### `run_sc_analysis(net, ...)`
Performs IEC 60909 short circuit calculation.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `net` | `pandapowerNet` | Required | The network object |
| `export_csv` | `bool` | True | Save results to CSV |
| `check_breakers` | `bool` | True | Check if fault duty exceeds breaker rating |
| `output_dir` | `str` | "data" | Output directory |

### 3. Plotting

#### `plot_tcc_curves(relays, ...)`
Generates Time-Current Characteristic curves.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `relays` | `List[Relay]` | Required | List of relay objects to plot |
| `current_min` | `float` | 10 | Minimum current on X-axis |
| `current_max` | `float` | 10000 | Maximum current on X-axis |
| `fault_type` | `str` | "phase" | "phase" or "ground" |
| `title` | `str` | "TCC..." | Plot title |
| `filename` | `str` | None | Output file (e.g. "tcc.png") |
| `figsize` | `tuple` | (10, 6) | Figure size (width, height) |

## Supported Curves

**IEC 60255:**
- `IEC_NI` (Normal Inverse)
- `IEC_VI` (Very Inverse)
- `IEC_EI` (Extremely Inverse)
- `IEC_LTI` (Long Time Inverse)

**IEEE C37.112:**
- `IEEE_MI` (Moderately Inverse)
- `IEEE_VI` (Very Inverse)
- `IEEE_EI` (Extremely Inverse)

**IEC 61363 (Marine):**
- `IEC_61363_S` (Short Time Delay)
- `IEC_61363_L` (Long Time Delay)
