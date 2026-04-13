import numpy as np

def calculate_metrics(df):
    """
    Evaluates the plan based on population variance and parity.
    """
    constituency_totals = df.groupby('constituency_id')['population'].sum()
    mean_pop = constituency_totals.mean()
    
    # Population Deviation (Lower is better)
    pop_variance = (constituency_totals.std() / mean_pop) * 100
    
    # Demographic Parity (Simplified check on socio-score balance)
    socio_parity = df.groupby('constituency_id')['socio_score'].mean().std()
    
    return {
        "pop_variance_pct": round(pop_variance, 2),
        "socio_parity_score": round(socio_parity, 2),
        "total_constituencies": int(len(constituency_totals))
    }