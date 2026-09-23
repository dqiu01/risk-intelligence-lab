import numpy as np
from engine import PRESETS,simulate_integrated,summarize,tail_contributions,dependency_comparison

def test_reproducible():
 s=PRESETS['Growing Small Business'];a=simulate_integrated(s.risks,5000,42,1);b=simulate_integrated(s.risks,5000,42,1);assert np.array_equal(a.total_losses,b.total_losses)
def test_mean_close_to_sum_of_marginal_means():
 s=PRESETS['Mid-Market Company'];r=simulate_integrated(s.risks,120000,3,1);target=sum(x.mean_loss for x in s.risks);assert abs(r.total_losses.mean()-target)/target<.025
def test_tail_contributions_sum():
 s=PRESETS['Large Organization'];c=tail_contributions(simulate_integrated(s.risks,30000,5,1));assert np.isclose(c.tail_contribution.sum(),1,atol=.01)
def test_dependency_increases_variability():
 s=PRESETS['Growing Small Business'];a=summarize(simulate_integrated(s.risks,60000,7,0),s.risks,s.reserve);b=summarize(simulate_integrated(s.risks,60000,7,1.25),s.risks,s.reserve);assert b['volatility']>a['volatility'];assert b['es_95']>a['es_95']
def test_curve_generated():
 s=PRESETS['Individual / Household'];d=dependency_comparison(s,10000,2);assert len(d)==6;assert d.correlation_scale.iloc[0]==0
