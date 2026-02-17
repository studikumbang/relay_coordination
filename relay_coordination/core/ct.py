"""
Current Transformer (CT) Module
ETAP-compatible CT modeling with IEC/ANSI accuracy classes
"""
import warnings
from typing import Optional


class CT:
    """Current Transformer Model (ETAP-compatible)"""
    
    def __init__(self, 
                 net,
                 bus: int,
                 element: Optional[int] = None,
                 element_type: str = "transformer",
                 primary_rating: float = 200.0,
                 secondary_rating: float = 5.0,
                 burden_va: float = 15.0,
                 accuracy_class_iec: str = "5P20",
                 accuracy_class_ansi: str = "C100",
                 ct_type: str = "Bar",
                 name: str = "CT"):
        """
        Initialize Current Transformer
        
        Parameters:
        -----------
        net : pandapower network
        bus : int - Bus index where CT is located
        element : int - Protected element index (transformer, line, etc.)
        element_type : str - Type of element ("transformer", "line", "ext_grid")
        primary_rating : float - Primary current rating (A)
        secondary_rating : float - Secondary current rating (1A or 5A standard)
        burden_va : float - CT burden in VA (includes cable + relay burden)
        accuracy_class_iec : str - IEC accuracy class (e.g., "5P20", "10P10")
            Format: <error%>P<ALF>, where ALF = Accuracy Limit Factor
        accuracy_class_ansi : str - ANSI accuracy class (e.g., "C100", "C200")
            Number indicates max secondary voltage before saturation
        ct_type : str - CT construction type
            Options: "Wound", "Bar", "Bushing", "Window/Zero Sequence"
        name : str - CT identifier
        """
        self.net = net
        self.bus = bus
        self.element = element
        self.element_type = element_type
        self.primary_rating = primary_rating
        self.secondary_rating = secondary_rating
        self.ratio = primary_rating / secondary_rating
        self.burden_va = burden_va
        self.accuracy_class_iec = accuracy_class_iec
        self.accuracy_class_ansi = accuracy_class_ansi
        self.ct_type = ct_type
        self.name = name
        
        # Parse IEC accuracy class
        self._parse_iec_class()
        
        # Store in network
        if not hasattr(net, 'protection'):
            net.protection = {}
        if 'ct' not in net.protection:
            net.protection['ct'] = []
        
        self.index = len(net.protection['ct'])
        net.protection['ct'].append(self)
        
    def _parse_iec_class(self):
        """Parse IEC accuracy class string (e.g., '5P20')"""
        try:
            parts = self.accuracy_class_iec.replace('P', ' ').split()
            self.composite_error_pct = float(parts[0])
            self.alf = float(parts[1])  # Accuracy Limit Factor
        except:
            warnings.warn(f"Could not parse IEC class {self.accuracy_class_iec}, using defaults")
            self.composite_error_pct = 5.0
            self.alf = 20.0
    
    def secondary_current(self, primary_current: float) -> float:
        """
        Calculate secondary current from primary current
        
        Parameters:
        -----------
        primary_current : float - Primary current in A
        
        Returns:
        --------
        float - Secondary current in A
        """
        # Simple linear transformation (saturation modeling can be added)
        i_secondary = primary_current / self.ratio
        
        # Check if within accuracy limit
        i_limit = self.secondary_rating * self.alf
        if i_secondary > i_limit:
            warnings.warn(f"{self.name}: Secondary current {i_secondary:.2f}A exceeds accuracy limit {i_limit:.2f}A - CT may saturate")
        
        return i_secondary
    
    def primary_current(self, secondary_current: float) -> float:
        """Calculate primary current from secondary current"""
        return secondary_current * self.ratio
    
    def __repr__(self):
        return f"CT(name={self.name}, ratio={self.primary_rating}/{self.secondary_rating}, class={self.accuracy_class_iec})"


def add_ct(net, 
           bus: int,
           element: Optional[int] = None,
           element_type: str = "transformer",
           primary_rating: float = 200.0,
           secondary_rating: float = 5.0,
           burden_va: float = 15.0,
           accuracy_class_iec: str = "5P20",
           accuracy_class_ansi: str = "C100",
           ct_type: str = "Bar",
           name: str = "CT") -> CT:
    """
    Add Current Transformer to network (ETAP-style)
    
    See CT class for parameter descriptions
    """
    return CT(net=net, bus=bus, element=element, element_type=element_type,
              primary_rating=primary_rating, secondary_rating=secondary_rating,
              burden_va=burden_va, accuracy_class_iec=accuracy_class_iec,
              accuracy_class_ansi=accuracy_class_ansi, ct_type=ct_type, name=name)
