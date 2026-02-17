"""
Relay Curve Definitions
Standards: IEC 60255, IEEE/ANSI C37, IEC 61363
"""

# ============================================================================
# IEC 60255 Standard Curves
# ============================================================================

IEC_CURVES = {
    'IEC_NI': {
        'k': 0.14, 
        'alpha': 0.02, 
        'name': 'IEC Normal Inverse',
        'standard': 'IEC 60255'
    },
    'IEC_VI': {
        'k': 13.5, 
        'alpha': 1.0, 
        'name': 'IEC Very Inverse',
        'standard': 'IEC 60255'
    },
    'IEC_EI': {
        'k': 80.0, 
        'alpha': 2.0, 
        'name': 'IEC Extremely Inverse',
        'standard': 'IEC 60255'
    },
    'IEC_LTI': {
        'k': 120.0, 
        'alpha': 1.0, 
        'name': 'IEC Long Time Inverse',
        'standard': 'IEC 60255'
    },
    'IEC_STI': {
        'k': 0.05, 
        'alpha': 0.04, 
        'name': 'IEC Short Time Inverse',
        'standard': 'IEC 60255'
    },
}

# ============================================================================
# IEEE/ANSI C37 Standard Curves
# ============================================================================

IEEE_CURVES = {
    'IEEE_MI': {
        'A': 0.0515, 
        'B': 0.02, 
        'p': 0.114, 
        'name': 'IEEE Moderately Inverse',
        'standard': 'IEEE C37.112'
    },
    'IEEE_VI': {
        'A': 19.61, 
        'B': 0.491, 
        'p': 2.0, 
        'name': 'IEEE Very Inverse',
        'standard': 'IEEE C37.112'
    },
    'IEEE_EI': {
        'A': 28.2, 
        'B': 0.1217, 
        'p': 2.0, 
        'name': 'IEEE Extremely Inverse',
        'standard': 'IEEE C37.112'
    },
}

# ANSI C37 Additional Curves
ANSI_CURVES = {
    'ANSI_ST': {
        'A': 0.02394,
        'B': 0.01694,
        'p': 0.02,
        'name': 'ANSI Short Time',
        'standard': 'ANSI C37.112'
    },
    'ANSI_LT': {
        'A': 5.95,
        'B': 0.18,
        'p': 2.0,
        'name': 'ANSI Long Time',
        'standard': 'ANSI C37.112'
    },
    'ANSI_DEF': {
        'A': 0.2663,
        'B': 0.0,
        'p': 0.0,
        'name': 'ANSI Definite Time',
        'standard': 'ANSI C37.112'
    },
}

# ============================================================================
# IEC 61363 Marine & Offshore Curves
# ============================================================================

IEC_61363_CURVES = {
    'IEC_61363_A': {
        'k': 0.0515,
        'alpha': 0.02,
        'name': 'IEC 61363 Type A (Standard Inverse)',
        'standard': 'IEC 61363',
        'application': 'Marine/Offshore general protection'
    },
    'IEC_61363_B': {
        'k': 13.5,
        'alpha': 1.0,
        'name': 'IEC 61363 Type B (Very Inverse)',
        'standard': 'IEC 61363',
        'application': 'Marine/Offshore motor protection'
    },
    'IEC_61363_C': {
        'k': 80.0,
        'alpha': 2.0,
        'name': 'IEC 61363 Type C (Extremely Inverse)',
        'standard': 'IEC 61363',
        'application': 'Marine/Offshore transformer protection'
    },
    'IEC_61363_LT': {
        'k': 120.0,
        'alpha': 1.0,
        'name': 'IEC 61363 Long Time',
        'standard': 'IEC 61363',
        'application': 'Marine/Offshore feeder protection'
    },
}

# ============================================================================
# Combined Curve Dictionary
# ============================================================================

ALL_CURVES = {}
ALL_CURVES.update(IEC_CURVES)
ALL_CURVES.update(IEEE_CURVES)
ALL_CURVES.update(ANSI_CURVES)
ALL_CURVES.update(IEC_61363_CURVES)

# ============================================================================
# Curve Type Detection
# ============================================================================

def get_curve_params(curve_type: str) -> dict:
    """
    Get curve parameters by curve type identifier
    
    Parameters:
    -----------
    curve_type : str - Curve identifier (e.g., 'IEC_NI', 'IEEE_VI', 'ANSI_ST')
    
    Returns:
    --------
    dict - Curve parameters
    
    Raises:
    -------
    ValueError - If curve type not found
    """
    if curve_type in ALL_CURVES:
        return ALL_CURVES[curve_type]
    else:
        available = ', '.join(sorted(ALL_CURVES.keys()))
        raise ValueError(
            f"Unknown curve type: {curve_type}\n"
            f"Available curves: {available}"
        )


def is_iec_curve(curve_type: str) -> bool:
    """Check if curve uses IEC formula"""
    return curve_type in IEC_CURVES or curve_type in IEC_61363_CURVES


def is_ieee_curve(curve_type: str) -> bool:
    """Check if curve uses IEEE/ANSI formula"""
    return curve_type in IEEE_CURVES or curve_type in ANSI_CURVES


def list_curves_by_standard(standard: str = None) -> list:
    """
    List available curves, optionally filtered by standard
    
    Parameters:
    -----------
    standard : str - Optional filter ('IEC 60255', 'IEEE C37.112', 'ANSI C37.112', 'IEC 61363')
    
    Returns:
    --------
    list - List of (curve_id, curve_name, standard) tuples
    """
    curves = []
    for curve_id, params in ALL_CURVES.items():
        curve_standard = params.get('standard', 'Unknown')
        if standard is None or curve_standard == standard:
            curves.append((curve_id, params['name'], curve_standard))
    
    return sorted(curves, key=lambda x: (x[2], x[0]))
