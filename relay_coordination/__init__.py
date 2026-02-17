"""
Relay Coordination Package for Pandapower
ETAP-style protection coordination simulation
"""

__version__ = "1.0.0"
__author__ = "Relay Coordination Team"

# Core classes
from relay_coordination.core.ct import CT
from relay_coordination.core.relay import Relay
from relay_coordination.core.cb import CircuitBreaker

# Helper functions for adding devices
from relay_coordination.core.ct import add_ct
from relay_coordination.core.relay import add_relay
from relay_coordination.core.cb import add_cb

# Analysis functions
from relay_coordination.analysis.coordination import run_coordination_analysis
from relay_coordination.analysis.short_circuit import run_sc_analysis
from relay_coordination.analysis.reports import (
    print_protection_summary,
    export_coordination_table
)

# Plotting functions
from relay_coordination.plotting.tcc import plot_tcc_curves, generate_coordination_table

__all__ = [
    # Version
    '__version__',
    
    # Core classes
    'CT',
    'Relay',
    'CircuitBreaker',
    
    # Helper functions
    'add_ct',
    'add_relay',
    'add_cb',
    
    # Analysis
    'run_coordination_analysis',
    'run_sc_analysis',
    'print_protection_summary',
    'export_coordination_table',
    
    # Plotting
    'plot_tcc_curves',
    'generate_coordination_table',
]
