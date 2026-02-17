"""
Coordination Analysis Module
Simplified API for protection coordination testing with automatic reporting
"""
import pandas as pd
from typing import List, Optional
from relay_coordination.analysis.reports import export_coordination_table


def run_coordination_analysis(net, 
                              test_currents: Optional[List[float]] = None, 
                              fault_type: str = "phase",
                              export_csv: bool = True, 
                              output_dir: str = 'data'):
    """
    Run coordination analysis with automatic reporting (similar to pp.runpp())
    
    Tests all relays at specified fault currents and prints formatted results.
    Optionally exports CSV tables.
    
    Parameters:
    -----------
    net : pandapower network with protection devices
    test_currents : List[float] - Test current values in Amperes (default: [100, 200, 500, 1000, 2000, 5000])
    fault_type : str - "phase" or "ground"
    export_csv : bool - Export coordination table to CSV
    output_dir : str - Output directory for CSV files (default: 'data')
    
    Returns:
    --------
    pd.DataFrame - Coordination table
    """
    if export_csv:
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    if test_currents is None:
        test_currents = [100, 200, 500, 1000, 2000, 5000]
    
    if not hasattr(net, 'protection') or 'relay' not in net.protection:
        print("No relays found in network")
        return None
    
    print("\n" + "="*80)
    print(f"PROTECTION COORDINATION ANALYSIS ({fault_type.upper()} FAULTS)")
    print("="*80)
    
    relays = net.protection['relay']
    
    # Generate coordination data
    data = []
    for I_fault in test_currents:
        row = {'Fault Current (A)': I_fault}
        
        for relay in relays:
            trip_time = relay.calculate_trip_time(I_fault, fault_type)
            
            if trip_time is not None:
                # Determine which element operated
                if fault_type == "phase":
                    if relay.phase_inst_enabled and relay.phase_inst_pickup and I_fault >= relay.phase_inst_pickup:
                        element = "50"
                    else:
                        element = "51"
                else:  # ground
                    if relay.ground_inst_enabled and relay.ground_inst_pickup and I_fault >= relay.ground_inst_pickup:
                        element = "50N"
                    else:
                        element = "51N"
                
                # Add CB total time if available
                if relay.cb:
                    total_time = relay.cb.total_clearing_time(I_fault, fault_type)
                    row[f"{relay.name} Relay (s)"] = f"{trip_time:.4f} ({element})"
                    row[f"{relay.name} Total (s)"] = f"{total_time:.4f}"
                else:
                    row[f"{relay.name} (s)"] = f"{trip_time:.4f} ({element})"
            else:
                if relay.cb:
                    row[f"{relay.name} Relay (s)"] = "No trip"
                    row[f"{relay.name} Total (s)"] = "No trip"
                else:
                    row[f"{relay.name} (s)"] = "No trip"
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Print formatted table
    print(f"\nCoordination Table:")
    print(df.to_string(index=False))
    
    # Export to CSV
    if export_csv:
        import os
        filename = os.path.join(output_dir, f'coordination_table_{fault_type}.csv')
        
        # Create clean version for CSV (remove element labels)
        csv_data = []
        for I_fault in test_currents:
            row = {'Fault Current (A)': I_fault}
            for relay in relays:
                trip_time = relay.calculate_trip_time(I_fault, fault_type)
                if trip_time is not None:
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
            csv_data.append(row)
        
        csv_df = pd.DataFrame(csv_data)
        csv_df.to_csv(filename, index=False)
        print(f"\n✓ Coordination table exported to {filename}")
    
    return df


def check_selectivity(net, fault_current: float, fault_type: str = "phase", min_margin: float = 0.3):
    """
    Check selectivity between relays (coordination margin)
    
    Parameters:
    -----------
    net : pandapower network
    fault_current : float - Test fault current (A)
    fault_type : str - "phase" or "ground"
    min_margin : float - Minimum required time margin (seconds)
    
    Returns:
    --------
    dict - Selectivity check results
    """
    if not hasattr(net, 'protection') or 'relay' not in net.protection:
        return None
    
    relays = net.protection['relay']
    trip_times = []
    
    for relay in relays:
        trip_time = relay.calculate_trip_time(fault_current, fault_type)
        if trip_time is not None:
            trip_times.append((relay.name, trip_time))
    
    # Sort by trip time
    trip_times.sort(key=lambda x: x[1])
    
    print(f"\nSelectivity Check at {fault_current}A ({fault_type}):")
    print(f"{'Relay':<15} {'Trip Time (s)':<15} {'Margin (s)':<15} {'Status':<10}")
    print("-" * 60)
    
    results = []
    for i, (relay_name, trip_time) in enumerate(trip_times):
        if i == 0:
            print(f"{relay_name:<15} {trip_time:<15.4f} {'N/A':<15} {'Primary':<10}")
            results.append({'relay': relay_name, 'trip_time': trip_time, 'margin': None, 'selective': True})
        else:
            margin = trip_time - trip_times[i-1][1]
            selective = margin >= min_margin
            status = '✓ OK' if selective else '✗ FAIL'
            print(f"{relay_name:<15} {trip_time:<15.4f} {margin:<15.4f} {status:<10}")
            results.append({'relay': relay_name, 'trip_time': trip_time, 'margin': margin, 'selective': selective})
    
    return results
