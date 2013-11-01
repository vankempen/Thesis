priceTable = ""
r = 10

for flyFrom in storage.keys():
    for flyTo in storage[flyFrom].keys():
        hp, _ = get_ticketPrices(historical, flyFrom, flyTo)
        cp, mtp = get_ticketPrices(storage, flyFrom, flyTo)
        
        # print flyFrom, flyTo
        
        p_fRange = [0.80, 0.85, 0.90, 0.95]
        
        for m in [3, 7, 14]:
            mp_a = []
            ps_a = []
            
            sellerWTA = get_sellerWTA_foreknowledge(cp, m=m)  # TAKEN FROM FOR-LOOP!!!

            for p_f in p_fRange:
                custWTP = get_customerWTP(hp, cp, r=10, m=m, p_f=p_f)

                mp, ps = run_optionSimulation(cp, custWTP, sellerWTA, m=m, p_f=p_f, trials=100, allKnowing=True)

                mp_a.append(mp)
                ps_a.append(ps)

            mp_a = np.array(mp_a)
            ps_a = np.array(ps_a)

            v = zip(p_fRange, [mtp/100]*4, mp_a/100, mp_a/mtp*100, ps_a*100)
            priceTable += get_priceTableSegment(flyFrom, flyTo, m, v)

print priceTable
