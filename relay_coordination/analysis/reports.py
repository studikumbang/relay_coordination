"""
Reporting Functions
Automated report generation and CSV export for protection studies
"""
import pandas as pd
from typing import List, Optional


def print_protection_summary(net):
    """
    Print summary of all protection devices in network
    
    Parameters:
    -----------
    net : pandapower network with protection devices
    """
    if not hasattr(net, 'protection'):
        print("No protection devices found in network")
        return
    
    num_cts = len(net.protection.get('ct', []))
    num_relays = len(net.protection.get('relay', []))
    num_cbs = len(net.protection.get('cb', []))
    
    print("\n" + "="*80)
    print("PROTECTION SYSTEM SUMMARY")
    print("="*80)
    print(f"\nNetwork has {num_cts} CTs, {num_relays} Relays, {num_cbs} CBs")
    
    if num_cts > 0:
        print("\nCurrent Transformers:")
        for ct in net.protection['ct']:
            print(f"  {ct}")
    
    if num_relays > 0:
        print("\nProtection Relays:")
        for relay in net.protection['relay']:
            print(f"  {relay}")
    
    if num_cbs > 0:
        print("\nCircuit Breakers:")
        for cb in net.protection['cb']:
            print(f"  {cb}")


def export_coordination_table(net, filename: str, test_currents: List[float], fault_type: str = "phase"):
    """
    Export coordination table to CSV file
    
    Parameters:
    -----------
    net : pandapower network
    filename : str - Output CSV filename
    test_currents : List[float] - Test current values (A)
    fault_type : str - "phase" or "ground"
    """
    if not hasattr(net, 'protection') or 'relay' not in net.protection:
        print("No relays found in network")
        return
    
    relays = net.protection['relay']
    
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
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✓ Coordination table exported to {filename}")


def export_sc_report(net, filename: str):
    """
    Export short circuit analysis results to CSV
    
    Parameters:
    -----------
    net : pandapower network with short circuit results
    filename : str - Output CSV filename
    """
    if not hasattr(net, 'res_bus_sc'):
        print("No short circuit results found. Run short circuit analysis first.")
        return
    
    # Export bus short circuit results
    net.res_bus_sc.to_csv(filename, index=True)
    print(f"✓ Short circuit report exported to {filename}")


def export_breaker_adequacy(net, filename: str):
    """
    Export breaker adequacy check results to CSV
    
    Parameters:
    -----------
    net : pandapower network
    filename : str - Output CSV filename
    """
    if not hasattr(net, 'protection') or 'cb' not in net.protection:
        print("No circuit breakers found in network")
        return
    
    if not hasattr(net, 'res_bus_sc'):
        print("No short circuit results found. Run short circuit analysis first.")
        return
    
    data = []
    for cb in net.protection['cb']:
        bus_idx = cb.bus
        if bus_idx < len(net.res_bus_sc):
            ikss = net.res_bus_sc.at[bus_idx, 'ikss_ka']
            adequate = ikss <= cb.interrupting_rating_ka_sym
            
            data.append({
                'CB Name': cb.name,
                'Bus': net.bus.at[bus_idx, 'name'],
                'Fault Current (kA)': f"{ikss:.2f}",
                'CB Rating (kA)': f"{cb.interrupting_rating_ka_sym:.2f}",
                'Adequate': 'Yes' if adequate else 'No'
            })
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✓ Breaker adequacy report exported to {filename}")
