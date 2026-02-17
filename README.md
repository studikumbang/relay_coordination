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

Or install from source:

```bash
git clone https://github.com/yourusername/relay_coordination.git
cd relay_coordination
pip install -e .
```

## Quick Start

```python
import pandapower as pp
import relay_coordination as rc

net = pp.create_empty_network()
# ... build network ...

# Add protection
ct = rc.add_ct(net, bus=0, primary_rating=200, secondary_rating=5)
relay = rc.add_relay(net, ct=ct, phase_pickup=100)

# Run analysis
rc.run_coordination_analysis(net)

# Plot TCC
rc.plot_tcc_curves([relay], filename="tcc.png", figsize=(12, 8))
```

## Data Export

All analysis results and plots are automatically saved to the `./data/` directory by default.
