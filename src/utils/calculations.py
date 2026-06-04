import numpy_financial as npf

def calc_bond_payment(P, rate, years):
    r = rate / 12
    n = years * 12
    return npf.pmt(r, n, -P)

def calc_annual_rent(m_rent):
    return m_rent * 12

def calc_vacancy_loss(a_rent, loss_rate):
    return a_rent * loss_rate

def calc_monthly_expenses(levies, rates, maintenance = 0, insurance = 0, v_reserve = 0):
    return levies + rates + maintenance + insurance + v_reserve

def calc_annual_expenses(m_exps):
    return m_exps * 12

def calc_cashflow(m_rent, m_exps, m_mort):
    return m_rent - m_exps - m_mort

def calc_annual_cashflow(cashflow):
    return cashflow * 12

def calc_annual_noi(a_rent, a_exps):
    return a_rent - a_exps

def calc_cap_rate(a_noi, property_value):
    return a_noi / property_value * 100

def calc_roi(a_cashflow, property_price, closing_cost = 70000, reno_costs = 0):
    tot_investments = property_price + closing_cost + reno_costs
    return a_cashflow / tot_investments * 100

def calc_dscr(a_noi, m_mort):
    a_mort = m_mort * 12
    return a_noi / a_mort

def calc_expected_growth_rate(e_appr_rate, infla_rate):
    return e_appr_rate - infla_rate

def calc_break_even(a_exps, m_mort, a_rent):
    a_mort = m_mort * 12
    return (a_exps + a_mort) / a_rent

def calc_investment_score(cashflow, cap_rate, roi, dscr, inflation_adjusted_growth, break_even):

    norm_cashflow = max(min(cashflow / 3000, 1), 0.0)
    norm_cap_rate = max(cap_rate, 0) / 12
    norm_roi = max(roi,0) / 20
    norm_dscr = min(max(dscr,0) / 1.5, 1)
    norm_growth = max((inflation_adjusted_growth + 5) / 10,0)
    norm_break_even = 1 - (break_even / 1.0)

    investment_score = (
        0.25 * norm_cashflow +
        0.20 * norm_cap_rate +
        0.20 * norm_roi +
        0.15 * norm_dscr +
        0.10 * norm_growth +
        0.10 * norm_break_even
    ) * 100

    return  max(min(investment_score, 100), 0)