import numpy as np
from engine import PRESETS,simulate_credit,summarize,analytical_expected_loss,contributions,concentration_metrics

def test_reproducible():
 s=PRESETS['Small B2B Receivables'];a=simulate_credit(s.counterparties,5000,1);b=simulate_credit(s.counterparties,5000,1);assert np.array_equal(a.total_losses,b.total_losses)
def test_simulated_el_close_to_analytical():
 s=PRESETS['Mid-Market Counterparties'];r=simulate_credit(s.counterparties,150000,42,stochastic_lgd=False);sim=r.total_losses.mean();ana=analytical_expected_loss(s.counterparties);assert abs(sim-ana)/ana<.05
def test_stress_increases_loss():
 s=PRESETS['Small B2B Receivables'];base=summarize(simulate_credit(s.counterparties,50000,42),s.counterparties,s.reserve);bad=summarize(simulate_credit(s.counterparties,50000,42,2,.1),s.counterparties,s.reserve);assert bad['simulated_el']>base['simulated_el'];assert bad['var_95']>=base['var_95']
def test_tail_contributions_sum():
 s=PRESETS['Enterprise Counterparties'];c=contributions(simulate_credit(s.counterparties,30000,5),s.counterparties);assert np.isclose(c.tail_contribution.sum(),1,atol=.02)
def test_concentration_metrics():
 s=PRESETS['Solo Professional Invoices'];m=concentration_metrics(s.counterparties);assert 0<m['largest_exposure_share']<1;assert m['effective_counterparties']<=len(s.counterparties)
