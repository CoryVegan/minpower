'''Test the constraint behavior of the bids'''

from attest import Tests,Assert
import logging
logging.basicConfig( level=logging.CRITICAL, format='%(levelname)s: %(message)s')

from minpower import optimization,powersystems,schedule,solve,config,bidding
from minpower.powersystems import Generator
from minpower.optimization import value

from test_utils import *

bidding = Tests()


@bidding.test
def linear():
    '''
    Create a linear bid curve for one generators.
    Ensure that correct cost is valued for the load.
    '''
    a=5
    b=30
    Pd=221
    generators=[ Generator(costcurvestring='{}+{}P'.format(a,b)) ]
    problem,times,buses=solve_problem(generators,make_load(Pd))
    cost = Assert(generators[0].bid[times[0]].output())
    assert cost == a+b*Pd

@bidding.test
def cubic_convex():
    '''
    Create a cubic, convex bid curve for one generators.
    Ensure that linearized cost is within +5% of the true cost
    '''
    Pd=221
    a=5
    b=30
    c=.2
    d=.1
    generators=[ Generator(costcurvestring='{}+{}P+{}P^2+{}P^3'.format(a,b,c,d)) ]
    problem,times,buses=solve_problem(generators,make_load(Pd))
    cost = Assert(value(generators[0].bid[times[0]].output()))
    actual_cost = a+ b*Pd+ c*Pd**2 + d*Pd**3
    assert actual_cost <= cost <= 1.05*actual_cost

@bidding.test
def cubic_non_convex():
    '''
    Create a cubic, but non-convex (negative cubic term) bid curve for one generators.
    Ensure that linearized cost is within +5% of the true cost
    '''
    Pd=221
    a=5
    b=30
    c=.2
    d=.0001
    generators=[ Generator(costcurvestring='{}+{}P+{}P^2 - {}P^3'.format(a,b,c,d)) ]
    problem,times,buses=solve_problem(generators,make_load(Pd))
    
    cost = Assert(generators[0].bid[times[0]].output())
    actual_cost = a+ b*Pd+ c*Pd**2 + -1*d*Pd**3
    assert actual_cost <= cost <= 1.05*actual_cost

if __name__ == "__main__": bidding.run()
