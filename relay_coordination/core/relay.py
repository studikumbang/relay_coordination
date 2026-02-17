"""
Protection Relay Module
ETAP-compatible relay modeling with IEC 60255, IEEE/ANSI C37, and IEC 61363 curves
"""
import numpy as np
import pandas as pd
from typing import Optional
from relay_coordination.core.curves import get_curve_params, is_iec_curve, is_ieee_curve


class Relay:
    """Protection Relay Model (ETAP-compatible)"""
    
    def __init__(self,
                 net,
                 ct,
                 cb,
                 manufacturer: str = "Schneider",
                 model: str = "Easergy P3U20",
                 # Phase overcurrent (51)
                 phase_pickup: float = None,
                 phase_curve: str = "IEC_NI",
                 phase_tms: float = 0.4,
                 phase_enabled: bool = True,
                 # Instantaneous (50)
                 phase_inst_pickup: float = None,
                 phase_inst_delay: float = 50.0,  # ms
                 phase_inst_enabled: bool = True,
                 # Ground overcurrent (51N)
                 ground_pickup: float = None,
                 ground_curve: str = "IEC_NI",
                 ground_tms: float = 0.4,
                 ground_enabled: bool = True,
                 # Ground instantaneous (50N)
                 ground_inst_pickup: float = None,
                 ground_inst_delay: float = 50.0,  # ms
                 ground_inst_enabled: bool = True,
                 name: str = "Relay"):
        """
        Initialize Protection Relay
        
        Parameters:
        -----------
        net : pandapower network
        ct : CT object - Associated current transformer
        cb : CircuitBreaker object - Associated circuit breaker
        manufacturer : str - Relay manufacturer (Schneider, Siemens, ABB, SEL, GE, etc.)
        model : str - Relay model number
        
        Phase Overcurrent (51 - Time Overcurrent):
        phase_pickup : float - Pickup current threshold (A primary or multiple of In)
        phase_curve : str - Time-current curve type (IEC_NI, IEC_VI, IEC_EI, IEEE_MI, etc.)
        phase_tms : float - Time Multiplier Setting (0.05-1.0 for IEC, 1-10 for ANSI)
        phase_enabled : bool - Enable phase overcurrent element
        
        Instantaneous (50 - High-set):
        phase_inst_pickup : float - Instantaneous pickup (I>>, A primary)
        phase_inst_delay : float - Operating delay in milliseconds
        phase_inst_enabled : bool - Enable instantaneous element
        
        Ground Overcurrent (51N - Earth fault time):
        ground_pickup : float - Ground fault pickup (A primary)
        ground_curve : str - Ground fault curve type
        ground_tms : float - Ground fault TMS
        ground_enabled : bool - Enable ground overcurrent
        
        Ground Instantaneous (50N - Earth fault inst):
        ground_inst_pickup : float - Ground instantaneous pickup
        ground_inst_delay : float - Ground delay in ms
        ground_inst_enabled : bool - Enable ground instantaneous
        
        name : str - Relay identifier
        """
        self.net = net
        self.ct = ct
        self.cb = cb
        self.manufacturer = manufacturer
        self.model = model
        self.name = name
        
        # Phase overcurrent (51)
        self.phase_pickup = phase_pickup
        self.phase_curve = phase_curve
        self.phase_tms = phase_tms
        self.phase_enabled = phase_enabled
        
        # Instantaneous (50)
        self.phase_inst_pickup = phase_inst_pickup
        self.phase_inst_delay = phase_inst_delay / 1000.0  # Convert ms to s
        self.phase_inst_enabled = phase_inst_enabled
        
        # Ground overcurrent (51N)
        self.ground_pickup = ground_pickup
        self.ground_curve = ground_curve
        self.ground_tms = ground_tms
        self.ground_enabled = ground_enabled
        
        # Ground instantaneous (50N)
        self.ground_inst_pickup = ground_inst_pickup
        self.ground_inst_delay = ground_inst_delay / 1000.0  # Convert ms to s
        self.ground_inst_enabled = ground_inst_enabled
        
        # Store in network
        if not hasattr(net, 'protection'):
            net.protection = {}
        if 'relay' not in net.protection:
            net.protection['relay'] = []
        
        self.index = len(net.protection['relay'])
        net.protection['relay'].append(self)
        
        # Link CB to this relay
        if cb is not None:
            cb.relay = self
    
    def calculate_trip_time(self, fault_current: float, fault_type: str = "phase") -> Optional[float]:
        """
        Calculate relay trip time for given fault current
        
        Parameters:
        -----------
        fault_current : float - Fault current magnitude (A primary)
        fault_type : str - "phase" or "ground"
        
        Returns:
        --------
        float - Trip time in seconds, or None if relay doesn't trip
        """
        # Convert to secondary current
        i_secondary = self.ct.secondary_current(fault_current)
        i_primary = fault_current
        
        if fault_type == "phase":
            # Check instantaneous element (50) first
            if self.phase_inst_enabled and self.phase_inst_pickup is not None:
                if i_primary >= self.phase_inst_pickup:
                    return self.phase_inst_delay
            
            # Check time-overcurrent element (51)
            if self.phase_enabled and self.phase_pickup is not None:
                if i_primary >= self.phase_pickup:
                    trip_time = self._calculate_curve_time(
                        i_primary, 
                        self.phase_pickup, 
                        self.phase_curve, 
                        self.phase_tms
                    )
                    return trip_time
        
        elif fault_type == "ground":
            # Check ground instantaneous (50N)
            if self.ground_inst_enabled and self.ground_inst_pickup is not None:
                if i_primary >= self.ground_inst_pickup:
                    return self.ground_inst_delay
            
            # Check ground time-overcurrent (51N)
            if self.ground_enabled and self.ground_pickup is not None:
                if i_primary >= self.ground_pickup:
                    trip_time = self._calculate_curve_time(
                        i_primary,
                        self.ground_pickup,
                        self.ground_curve,
                        self.ground_tms
                    )
                    return trip_time
        
        return None  # Relay doesn't trip
    
    def _calculate_curve_time(self, current: float, pickup: float, curve_type: str, tms: float) -> float:
        """
        Calculate trip time using IEC 60255, IEEE/ANSI C37, or IEC 61363 curves
        
        IEC Formula: t = TMS × K / ((I/Ipickup)^α - 1)
        IEEE/ANSI Formula: t = TD × (A / ((I/Ipickup)^p - B))
        
        Parameters:
        -----------
        current : float - Fault current (A)
        pickup : float - Pickup threshold (A)
        curve_type : str - Curve identifier
        tms : float - Time multiplier setting
        
        Returns:
        --------
        float - Operating time in seconds
        """
        M = current / pickup  # Current multiple
        
        if M <= 1.0:
            return float('inf')  # Below pickup, never trips
        
        # Get curve parameters from centralized curves module
        params = get_curve_params(curve_type)
        
        # IEC curves (IEC 60255, IEC 61363)
        if is_iec_curve(curve_type):
            k = params['k']
            alpha = params['alpha']
            t = tms * k / (M**alpha - 1.0)
            return t
        
        # IEEE/ANSI curves
        elif is_ieee_curve(curve_type):
            A = params['A']
            B = params['B']
            p = params['p']
            t = tms * (A / (M**p - B))
            return t
        
        else:
            raise ValueError(f"Unknown curve type: {curve_type}")
    
    def generate_tcc_data(self, current_range: np.ndarray, fault_type: str = "phase") -> pd.DataFrame:
        """
        Generate Time-Current Characteristic (TCC) curve data
        
        Parameters:
        -----------
        current_range : np.ndarray - Array of current values (A)
        fault_type : str - "phase" or "ground"
        
        Returns:
        --------
        pd.DataFrame - DataFrame with columns ['current', 'time']
        """
        times = []
        for i in current_range:
            t = self.calculate_trip_time(i, fault_type)
            times.append(t if t is not None else np.nan)
        
        return pd.DataFrame({
            'current': current_range,
            'time': times
        })
    
    def __repr__(self):
        return f"Relay(name={self.name}, model={self.manufacturer} {self.model})"


def add_relay(net,
              ct,
              cb,
              manufacturer: str = "Schneider",
              model: str = "Easergy P3U20",
              phase_pickup: float = None,
              phase_curve: str = "IEC_NI",
              phase_tms: float = 0.4,
              phase_enabled: bool = True,
              phase_inst_pickup: float = None,
              phase_inst_delay: float = 50.0,
              phase_inst_enabled: bool = True,
              ground_pickup: float = None,
              ground_curve: str = "IEC_NI",
              ground_tms: float = 0.4,
              ground_enabled: bool = True,
              ground_inst_pickup: float = None,
              ground_inst_delay: float = 50.0,
              ground_inst_enabled: bool = True,
              name: str = "Relay") -> Relay:
    """
    Add Protection Relay to network (ETAP-style)
    
    See Relay class for parameter descriptions
    """
    return Relay(net=net, ct=ct, cb=cb, manufacturer=manufacturer, model=model,
                 phase_pickup=phase_pickup, phase_curve=phase_curve, phase_tms=phase_tms,
                 phase_enabled=phase_enabled, phase_inst_pickup=phase_inst_pickup,
                 phase_inst_delay=phase_inst_delay, phase_inst_enabled=phase_inst_enabled,
                 ground_pickup=ground_pickup, ground_curve=ground_curve, ground_tms=ground_tms,
                 ground_enabled=ground_enabled, ground_inst_pickup=ground_inst_pickup,
                 ground_inst_delay=ground_inst_delay, ground_inst_enabled=ground_inst_enabled,
                 name=name)
