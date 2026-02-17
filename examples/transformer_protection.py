"""
Simple Transformer Protection Example
Clean, minimal example using the relay_coordination package
"""
import pandapower as pp
import relay_coordination as rc
import numpy as np

# Create network
net = pp.create_empty_network()

# Create buses
b1 = pp.create_bus(net, vn_kv=20., name="Bus 1 (20kV)")
b2 = pp.create_bus(net, vn_kv=0.4, name="Bus 2 (400V)")
b3 = pp.create_bus(net, vn_kv=0.4, name="Bus 3 (400V)")

# Create bus elements
pp.create_ext_grid(net, bus=b1, vm_pu=1.02, name="Grid Connection",
                   s_sc_max_mva=1000, s_sc_min_mva=800, rx_max=0.1, rx_min=0.1)
pp.create_load(net, bus=b3, p_mw=0.1, q_mvar=0.05, name="Load")

# Create branch elements
t1 = pp.create_transformer(net, hv_bus=b1, lv_bus=b2, std_type="0.4 MVA 20/0.4 kV", name="Trafo")
pp.create_line(net, from_bus=b2, to_bus=b3, length_km=0.1, name="Line", std_type="NAYY 4x50 SE")

# Calculate transformer nominal currents
In_MV = (5500 * 1000) / (np.sqrt(3) * 20 * 1000)  # 158.77 A
In_LV = (5500 * 1000) / (np.sqrt(3) * 0.4 * 1000)  # 7938.57 A

print(f"Transformer nominal current (MV): {In_MV:.2f} A")
print(f"Transformer nominal current (LV): {In_LV:.2f} A")

# ============================================================================
# MV SIDE PROTECTION (20kV)
# ============================================================================

cb_mv = rc.add_cb(net, bus=b1, rated_voltage_kv=24.0, continuous_current_a=630.0,
                  interrupting_rating_ka_sym=25.0, operating_time_cycles=3.0,
                  cb_type="VCB", name="CB_MV")

ct_mv = rc.add_ct(net, bus=b1, element=t1, element_type="transformer",
                  primary_rating=200, secondary_rating=2, name="CT_MV")

relay_mv = rc.add_relay(net, ct=ct_mv, cb=cb_mv,
                        manufacturer="Schneider", model="Easergy P3U20",
                        phase_pickup=0.72 * In_MV,      # 114.32 A
                        phase_curve="IEC_NI",
                        phase_tms=0.4,
                        phase_inst_pickup=6.0 * In_MV,  # 952.63 A
                        phase_inst_delay=50.0,
                        ground_pickup=0.25 * In_MV,     # 39.69 A
                        ground_tms=0.4,
                        ground_inst_pickup=5.0 * 0.25 * In_MV,  # 198.46 A
                        ground_inst_delay=400.0,
                        name="Relay_MV")

# ============================================================================
# LV SIDE PROTECTION (400V)
# ============================================================================

cb_lv = rc.add_cb(net, bus=b2, rated_voltage_kv=0.69, continuous_current_a=1250.0,
                  interrupting_rating_ka_sym=40.0, operating_time_cycles=5.0,
                  cb_type="ACB", name="CB_LV")

ct_lv = rc.add_ct(net, bus=b2, element=t1, element_type="transformer",
                  primary_rating=800, secondary_rating=5, name="CT_LV")

relay_lv = rc.add_relay(net, ct=ct_lv, cb=cb_lv,
                        manufacturer="Schneider", model="Easergy P3U20",
                        phase_pickup=1.2 * In_LV,       # 9526.28 A
                        phase_curve="IEC_NI",
                        phase_tms=0.2,  # Faster for selectivity
                        phase_inst_pickup=8.0 * In_LV,  # 63508.53 A
                        phase_inst_delay=30.0,
                        ground_pickup=0.3 * In_LV,      # 2381.57 A
                        ground_tms=0.2,
                        ground_inst_pickup=6.0 * 0.3 * In_LV,  # 14289.42 A
                        ground_inst_delay=300.0,
                        name="Relay_LV")

# ============================================================================
# RUN ANALYSES (One-liner, handles everything)
# ============================================================================

# Power flow
print("\nRunning power flow...")
pp.runpp(net)
print(f"✓ Converged: {net.converged}")

# Short circuit analysis (IEC 60909)
rc.run_sc_analysis(net)

# Coordination analysis
rc.run_coordination_analysis(net, fault_type="phase")
rc.run_coordination_analysis(net, fault_type="ground")

# Protection summary
rc.print_protection_summary(net)

# Generate TCC curves
print("\nGenerating TCC curves...")
rc.plot_tcc_curves([relay_mv, relay_lv], fault_type="phase",
                   title="Phase Overcurrent Coordination (51/50)",
                   filename="tcc_phase_coordination.png")

rc.plot_tcc_curves([relay_mv, relay_lv], fault_type="ground",
                   title="Ground Fault Coordination (51N/50N)",
                   filename="tcc_ground_coordination.png")

print("\n" + "="*80)
print("✓ Simulation Complete!")
print("="*80)
