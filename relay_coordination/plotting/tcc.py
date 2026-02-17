"""
Time-Current Characteristic (TCC) Curve Plotter
Generates ETAP-style TCC coordination curves
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from typing import List
from matplotlib.ticker import ScalarFormatter


def plot_tcc_curves(relays: List,  
                    current_min: float = 10, 
                    current_max: float = 10000,
                    fault_type: str = "phase",
                    title: str = "Time-Current Coordination Curve",
                    filename: str = None,
                    figsize: tuple = (12, 8)):
    """
    Plot TCC curves for multiple relays on log-log scale
    
    Parameters:
    -----------
    relays : List[Relay] - List of relay objects to plot
    current_min : float - Minimum current to plot (A)
    current_max : float - Maximum current to plot (A)
    fault_type : str - "phase" or "ground"
    title : str - Plot title
    filename : str - Save plot to file (optional)
    """
    
    # Create current range (log-spaced)
    current_range = np.logspace(np.log10(current_min), np.log10(current_max), 500)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color palette
    colors = plt.cm.tab10(np.linspace(0, 1, len(relays)))
    
    # Plot each relay's TCC curve
    for idx, relay in enumerate(relays):
        color = colors[idx]
        
        # Generate TCC data
        times = []
        for i in current_range:
            t = relay.calculate_trip_time(i, fault_type)
            times.append(t if t is not None else np.nan)
        
        times = np.array(times)
        
        # Plot time-overcurrent curve (51/51N)
        if fault_type == "phase":
            pickup = relay.phase_pickup
            curve_label = f"{relay.name} - 51 ({relay.phase_curve})"
        else:
            pickup = relay.ground_pickup
            curve_label = f"{relay.name} - 51N ({relay.ground_curve})"
        
        # Plot curve (excluding instantaneous portion)
        valid = ~np.isnan(times) & (times > 0.01)  # Filter out instantaneous trips
        if np.any(valid):
            ax.loglog(current_range[valid], times[valid], 
                     color=color, linewidth=2.5, label=curve_label)
        
        # Plot instantaneous element (50/50N)
        if fault_type == "phase" and relay.phase_inst_enabled and relay.phase_inst_pickup:
            inst_pickup = relay.phase_inst_pickup
            inst_delay = relay.phase_inst_delay
            
            # Vertical line at instantaneous pickup
            ax.vlines(inst_pickup, 0.01, 100, colors=color, linestyles='dotted')
        
        elif fault_type == "ground" and relay.ground_inst_enabled and relay.ground_inst_pickup:
            inst_pickup = relay.ground_inst_pickup
            
            ax.vlines(inst_pickup, 0.01, 100, colors=color, linestyles='dotted')
    
    # Formatting
    ax.set_xlabel('Current (A)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (s)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.legend(loc='upper right', fontsize=9, framealpha=0.9)
    
    # Automatic axis limits based on data
    # Find the minimum pickup current and maximum fault current from all relays
    min_pickup = float('inf')
    max_inst_pickup = 0
    
    for relay in relays:
        if fault_type == "phase":
            if relay.phase_pickup:
                min_pickup = min(min_pickup, relay.phase_pickup)
            if relay.phase_inst_pickup:
                max_inst_pickup = max(max_inst_pickup, relay.phase_inst_pickup)
        else:  # ground
            if relay.ground_pickup:
                min_pickup = min(min_pickup, relay.ground_pickup)
            if relay.ground_inst_pickup:
                max_inst_pickup = max(max_inst_pickup, relay.ground_inst_pickup)
    
    # Set intelligent limits
    if min_pickup != float('inf'):
        x_min = min_pickup * 0.5  # 50% below minimum pickup
    else:
        x_min = current_min
    
    if max_inst_pickup > 0:
        x_max = max_inst_pickup * 2.0  # 2x above max instantaneous
    else:
        x_max = current_max
    
    # Ensure we don't violate parameter limits
    x_min = max(x_min, current_min)
    x_max = min(x_max, current_max)
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.01, 100)
    
    # Add standard time labels on y-axis
    ax.set_yticks([0.01, 0.05, 0.1, 0.5, 1, 5, 10, 50, 100])
    ax.yaxis.set_major_formatter(ScalarFormatter())
    
    plt.tight_layout()
    
    # Save or show
    if filename:
        # Save to ./data/ directory by default if only filename provided
        if not os.path.dirname(filename):
            output_dir = "data"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            filename = os.path.join(output_dir, filename)
            
        plt.savefig(filename, dpi=300)
        print(f"TCC curve saved to {filename}")
        plt.close()
    else:
        plt.show()
    
    return fig, ax


def generate_coordination_table(relays: List, 
                                 test_currents: List[float],
                                 fault_type: str = "phase") -> pd.DataFrame:
    """
    Generate coordination table showing trip times at various fault currents
    
    Parameters:
    -----------
    relays : List[Relay] - List of relays
    test_currents : List[float] - Test current levels (A)
    fault_type : str - "phase" or "ground"
    
    Returns:
    --------
    pd.DataFrame - Coordination table
    """
    
    data = []
    
    for I_fault in test_currents:
        row = {'Fault Current (A)': I_fault}
        
        for relay in relays:
            trip_time = relay.calculate_trip_time(I_fault, fault_type)
            
            if trip_time is not None:
                # Add CB operating time if available
                if relay.cb:
                    total_time = relay.cb.total_clearing_time(I_fault, fault_type)
                    row[f"{relay.name} Relay (s)"] = f"{trip_time:.4f}"
                    row[f"{relay.name} Total (s)"] = f"{total_time:.4f}"
                else:
                    row[f"{relay.name} (s)"] = f"{trip_time:.4f}"
            else:
                if relay.cb:
                    row[f"{relay.name} Relay (s)"] = "No trip"
                    row[f"{relay.name} Total (s)"] = "No trip"
                else:
                    row[f"{relay.name} (s)"] = "No trip"
        
        data.append(row)
    
    return pd.DataFrame(data)


if __name__ == "__main__":
    print("TCC Plotter - Use this module to visualize relay coordination")
    print("Import and call plot_tcc_curves() with your relay objects")
