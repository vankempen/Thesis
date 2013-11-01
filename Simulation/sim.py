def run_allSimulation(sellerWTA_f, custWTP_f, p_fRange=None, r=10, allKnowing=False):
    """
    return priceTable str for LaTeX with statistics on ALL airport combinations
    
    sellerWTA_f: function ref which returns seller's WTA
        see run_singleSimulation
    custWTP_f: function ref which returns customer's WTP
        see run_singleSimulation
    pf_Range: list with p_f's to consider
    r: risk aversity = 1+(1/r)
    allKnowing: is seller all knowing?
    """
    
    priceTable = ""
    
    # run simulation for every available airport combination
    for flyFrom in storage.keys():
        for flyTo in storage[flyFrom].keys():
            priceTable += run_singleSimulation(flyFrom, flyTo, p_fRange, r)
    return priceTable


def run_singleSimulation(flyFrom, flyTo, sellerWTA_f, custWTP_f, p_fRange=None, r=10, allKnowing=False):
    """
    return priceTable row for specific route
    
    sellerWTA_f: function ref which returns seller's WTA
        hp: historical prices
        cp: current prices
        m: maturity
    custWTP_f: function ref which returns customer's WTP
        hp: historical prices
        cp: current prices
        r: risk averion level
        m: maturity
        p_f: probability of flying
    pf_Range ([0.80, 0.85, 0.90, 0.95]): list with p_f's to consider
    r: risk aversity = 1+(1/r)
    allKnowing: is seller all knowing?
    """
    
    if p_fRange == None:
        p_fRange = [0.80, 0.85, 0.90, 0.95]
    
    priceTable = ""
    
    hp, _ = get_ticketPrices(historical, flyFrom, flyTo)
    cp, mtp = get_ticketPrices(storage, flyFrom, flyTo)
    
    # print flyFrom, flyTo
    
    for m in [3, 7, 14]:  # maturity in days
        mp_a = []
        ps_a = []
        
        sellerWTA = sellerWTA_f(hp, cp, m)
    
        for p_f in p_fRange:
            custWTP = custWTP_f(hp, cp, r=10, m=m, p_f=p_f)
    
            mp, ps = run_optionSimulation(cp, custWTP, sellerWTA, m=m, p_f=p_f, trials=100, allKnowing=allKnowing)
    
            mp_a.append(mp)
            ps_a.append(ps)
    
        mp_a = np.array(mp_a)
        ps_a = np.array(ps_a)
    
        v = zip(p_fRange, [mtp/100]*4, mp_a/100, mp_a/mtp*100, ps_a*100)
        priceTable += get_priceTableSegment(flyFrom, flyTo, m, v)    
    
    return priceTable


# all knowing with foreknowledge
run_singleSimulation(get_sellerWTA_foreknowledge, get_customerWTP, allKnowing=True)
#run_allSimulation(get_sellerWTA_foreknowledge, get_customerWTP, allKnowing=True)


# Black Scholes
def d1(S0, K, r, sigma, T):
    return (np.log(S0/K) + (r + sigma**2 / 2) * T)/(sigma * np.sqrt(T))
 
def d2(S0, K, r, sigma, T):
    return (np.log(S0/K) + (r - sigma**2 / 2) * T)/(sigma * np.sqrt(T))
 
def BlackScholes(hp, S0, T, r=0.01, call=True):
    """
    hp: historical prices
    S0: airfare at time 0
    T: maturity in days
    r: risk-free interest rate
    call: call (True) or put (False)
    """
    #volatility
    hpLN = np.log(hp)
    dRet = (hpLN.T.shift(1).T - hpLN)
    dRetMean = dRet.mean().mean()
    sigmaDaily = np.sqrt(((dRet - dRetMean)**2).mean().mean())
    sigma = sigmaDaily*np.sqrt(365)
    
    K = S0  # strike price == S0
    if call:
        return S0 * ss.norm.cdf(d1(S0, K, r, sigma, T)) - K * np.exp(-r * T) * ss.norm.cdf(d2(S0, K, r, sigma, T))
    return K * np.exp(-r * T) * ss.norm.cdf(-d2(S0, K, r, sigma, T)) - S0 * ss.norm.cdf(-d1(S0, K, r, sigma, T))

run_singleSimulation(BlackScholes, get_customerWTP, allKnowing=False)
#run_allSimulation(BlackScholes, get_customerWTP, allKnowing=False)


# Monte Carlo
def MonteCarlo(hp, cp, m, N=1000000):
    """
    return Monte Carlo estimation
    
    hp: historical prices
    cp: current prices (not used)
    m: maturity
    N: number of trials
    """
    dRet = hp.T.shift(1).T/hp
    
    expIncr = np.zeros(hp.size[1])
    
    for dbb in xrange(m-1, hp.size[1]):
        simRet = np.ones(N)
        for i in range(m):
            simRet *= np.random.choice(hp[:, dbb - i], N)
        expIncr[dbb] = simRet.mean()

    return expIncr

run_singleSimulation(MonteCarlo, get_customerWTP, allKnowing=False)
#run_allSimulation(MonteCarlo, get_customerWTP, allKnowing=False)
