"""
Short Circuit Analysis Module
Simplified API for IEC 60909 short circuit analysis with automatic reporting
"""
import pandas as pd
from typing import Optional


def run_sc_analysis(net, export_csv: bool = True, check_breakers: bool = True, output_dir: str = 'data'):
    """
    Run short circuit analysis with automatic reporting (similar to pp.runpp())
    
    Performs IEC 60909 short circuit calculation and prints formatted results.
    Optionally exports CSV files and checks breaker adequacy.
    
    Parameters:
    -----------
    net : pandapower network
    export_csv : bool - Export results to CSV files
    check_breakers : bool - Verify breaker interrupting capability
    output_dir : str - Output directory for CSV files (default: 'data')
    
    Returns:
    --------
    dict - Summary results
    """
    if export_csv:
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    import pandapower.shortcircuit as sc
    from relay_coordination.analysis.reports import export_sc_report, export_breaker_adequacy
    
    print("\n" + "="*80)
    print("SHORT CIRCUIT ANALYSIS (IEC 60909)")
    print("="*80)
    
    try:
        # Calculate short circuit currents
        sc.calc_sc(net, case='max', ip=True, ith=True, tk_s=1.0)
        
        print(f"\nShort Circuit Results:")
        print(net.res_bus_sc[['ikss_ka', 'ip_ka']])
        
        # Check breaker ratings
        if check_breakers and hasattr(net, 'protection') and 'cb' in net.protection:
            print("\nCircuit Breaker Adequacy Check:")
            print(f"{'Breaker':<15} {'Bus':<20} {'Fault (kA)':<12} {'Rating (kA)':<12} {'Status':<10}")
            print("-" * 75)
            
            for cb in net.protection['cb']:
                bus_idx = cb.bus
                if bus_idx < len(net.res_bus_sc):
                    ikss = net.res_bus_sc.at[bus_idx, 'ikss_ka']
                    bus_name = net.bus.at[bus_idx, 'name']
                    adequate = cb.check_interrupting_capability(ikss)
                    status = '✓ OK' if adequate else '✗ UPGRADE'
                    
                    print(f"{cb.name:<15} {bus_name:<20} {ikss:<12.2f} {cb.interrupting_rating_ka_sym:<12.2f} {status:<10}")
        
        # Export CSV files
        if export_csv:
            import os
            sc_file = os.path.join(output_dir, 'short_circuit_results.csv')
            export_sc_report(net, sc_file)
            
            if check_breakers and hasattr(net, 'protection') and 'cb' in net.protection:
                breaker_file = os.path.join(output_dir, 'breaker_adequacy.csv')
                export_breaker_adequacy(net, breaker_file)
        
        return {
            'converged': True,
            'max_fault_current_ka': net.res_bus_sc['ikss_ka'].max()
        }
        
    except Exception as e:
        print(f"Short circuit analysis failed: {str(e)}")
        return {'converged': False, 'error': str(e)}
