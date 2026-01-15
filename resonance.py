def calc_total_resonance(base_score, k_score, weight=0.25):
    """
    base_score : 你原本的共振分數
    k_score    : 康波數值 (-1 ~ 1)
    weight     : 康波權重
    """
    return base_score * (1 - weight) + k_score * weight
