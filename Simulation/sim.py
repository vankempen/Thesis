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

#all knowing
#get_sellerWTA_foreknowledge
#get_customerWTP(hp, cp, r=10, m=m, p_f=p_f)
