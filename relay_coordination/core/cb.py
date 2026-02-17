"""
Circuit Breaker (CB) Module
ETAP-compatible breaker modeling with interrupting ratings and operating times
"""
import warnings
from typing import Optional


class CircuitBreaker:
    """Circuit Breaker Model (ETAP-compatible)"""
    
    def __init__(self,
                 net,
                 bus: int,
                 relay=None,
                 rated_voltage_kv: float = 24.0,
                 continuous_current_a: float = 630.0,
                 interrupting_rating_ka_sym: float = 25.0,
                 interrupting_rating_ka_asym: float = 25.0,
                 making_capacity_ka_peak: float = 63.0,
                 operating_time_cycles: float = 3.0,
                 operating_time_ms: Optional[float] = None,
                 cb_type: str = "VCB",
                 name: str = "CB"):
        """
        Initialize Circuit Breaker
        
        Parameters:
        -----------
        net : pandapower network
        bus : int - Bus index where CB is located
        relay : Relay object - Associated protection relay
        rated_voltage_kv : float - Rated operating voltage (kV)
        continuous_current_a : float - Maximum continuous current without overheating (A)
        interrupting_rating_ka_sym : float - Symmetrical breaking capacity (kA RMS)
            Must exceed maximum fault current at this location
        interrupting_rating_ka_asym : float - Asymmetrical breaking capacity (kA RMS)
            Accounts for DC offset component at fault inception
        making_capacity_ka_peak : float - Peak making capacity (kA peak)
            Ability to close into an active short circuit
            Typically = 2.5 × interrupting_rating_ka_sym
        operating_time_cycles : float - Total clearing time in cycles (60Hz)
            Typical values: 3-5 cycles for MV breakers
        operating_time_ms : float - Total clearing time in milliseconds (alternative)
            If specified, overrides operating_time_cycles
        cb_type : str - Circuit breaker type
            Options: "VCB" (Vacuum), "SF6" (Gas), "Oil", "ACB" (Air), "MCCB"
        name : str - CB identifier
        """
        self.net = net
        self.bus = bus
        self.relay = relay
        self.rated_voltage_kv = rated_voltage_kv
        self.continuous_current_a = continuous_current_a
        self.interrupting_rating_ka_sym = interrupting_rating_ka_sym
        self.interrupting_rating_ka_asym = interrupting_rating_ka_asym
        self.making_capacity_ka_peak = making_capacity_ka_peak
        self.cb_type = cb_type
        self.name = name
        self.state = "closed"  # "open" or "closed"
        
        # Operating time calculation
        if operating_time_ms is not None:
            self.operating_time = operating_time_ms / 1000.0  # Convert to seconds
        else:
            # Convert cycles to seconds (assuming 60Hz)
            self.operating_time = operating_time_cycles / 60.0
        
        # Store in network
        if not hasattr(net, 'protection'):
            net.protection = {}
        if 'cb' not in net.protection:
            net.protection['cb'] = []
        
        self.index = len(net.protection['cb'])
        net.protection['cb'].append(self)
    
    def total_clearing_time(self, fault_current: float, fault_type: str = "phase") -> Optional[float]:
        """
        Calculate total clearing time (relay trip time + CB operating time)
        
        Parameters:
        -----------
        fault_current : float - Fault current (A)
        fault_type : str - "phase" or "ground"
        
        Returns:
        --------
        float - Total clearing time in seconds, or None if doesn't trip
        """
        if self.relay is None:
            return None
        
        relay_time = self.relay.calculate_trip_time(fault_current, fault_type)
        if relay_time is None:
            return None
        
        return relay_time + self.operating_time
    
    def trip(self):
        """Open the circuit breaker"""
        self.state = "open"
        print(f"{self.name} TRIPPED - State: OPEN")
    
    def close(self):
        """Close the circuit breaker"""
        self.state = "closed"
        print(f"{self.name} CLOSED - State: CLOSED")
    
    def check_interrupting_capability(self, fault_current_ka: float) -> bool:
        """
        Verify CB can safely interrupt the fault current
        
        Parameters:
        -----------
        fault_current_ka : float - Fault current in kA
        
        Returns:
        --------
        bool - True if CB rating is adequate
        """
        if fault_current_ka > self.interrupting_rating_ka_sym:
            warnings.warn(
                f"{self.name}: Fault current {fault_current_ka:.2f}kA exceeds "
                f"interrupting rating {self.interrupting_rating_ka_sym:.2f}kA - "
                f"BREAKER MAY FAIL!"
            )
            return False
        return True
    
    def __repr__(self):
        return f"CB(name={self.name}, type={self.cb_type}, rating={self.interrupting_rating_ka_sym}kA, state={self.state})"


def add_cb(net,
           bus: int,
           relay=None,
           rated_voltage_kv: float = 24.0,
           continuous_current_a: float = 630.0,
           interrupting_rating_ka_sym: float = 25.0,
           interrupting_rating_ka_asym: float = 25.0,
           making_capacity_ka_peak: float = 63.0,
           operating_time_cycles: float = 3.0,
           operating_time_ms: Optional[float] = None,
           cb_type: str = "VCB",
           name: str = "CB") -> CircuitBreaker:
    """
    Add Circuit Breaker to network (ETAP-style)
    
    See CircuitBreaker class for parameter descriptions
    """
    return CircuitBreaker(net=net, bus=bus, relay=relay, rated_voltage_kv=rated_voltage_kv,
                          continuous_current_a=continuous_current_a,
                          interrupting_rating_ka_sym=interrupting_rating_ka_sym,
                          interrupting_rating_ka_asym=interrupting_rating_ka_asym,
                          making_capacity_ka_peak=making_capacity_ka_peak,
                          operating_time_cycles=operating_time_cycles,
                          operating_time_ms=operating_time_ms,
                          cb_type=cb_type, name=name)
