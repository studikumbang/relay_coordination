"""
Simple Relay Coordination Example
Minimal example showing basic usage of the relay_coordination package
"""
import pandapower as pp
import relay_coordination as rc

# Create simple network
net = pp.create_empty_network()

# Create bus
bus = pp.create_bus(net, vn_kv=20., name="MV Bus")

# Add external grid with short circuit data
pp.create_ext_grid(net, bus=bus, vm_pu=1.0, s_sc_max_mva=500)

# Add protection devices
cb = rc.add_cb(net, bus=bus, rated_voltage_kv=24.0, 
               interrupting_rating_ka_sym=25.0, name="CB1")

ct = rc.add_ct(net, bus=bus, primary_rating=200, 
               secondary_rating=5, name="CT1")

relay = rc.add_relay(net, ct=ct, cb=cb,
                     phase_pickup=150.0,
                     phase_curve="IEC_NI",
                     phase_tms=0.3,
                     phase_inst_pickup=900.0,
                     name="Relay1")

# Test protection at various fault currents
print("\nTesting protection at various fault currents:")
print(f"{'Current (A)':<15} {'Trip Time (s)':<15}")
print("-" * 30)

for I in [100, 200, 400, 800, 1600]:
    trip_time = relay.calculate_trip_time(I)
    if trip_time:
        print(f"{I:<15} {trip_time:<15.4f}")
    else:
        print(f"{I:<15} {'No trip':<15}")

# Print protection summary
rc.print_protection_summary(net)

print("\n✓ Simple example complete!")
