                            gold_m_lower, gold_s_lower = divmod(gold_x1*predict_year +gold_const - 2*gold_std, 60)
                            gold_h_lower, gold_m_lower = divmod(gold_m_lower, 60)
                            gold_m_lower = int(gold_m_lower)
                            gold_s_lower=round(gold_s_lower,3)
                            if gold_s_lower<10:
                                gold_s_lower="0"+str(gold_s_lower)  
                                
                            gold_m_higher, gold_s_higher = divmod(gold_x1*predict_year +gold_const +2*gold_std, 60)
                            gold_h_higher, gold_m_higher = divmod(gold_m_higher, 60)
                            gold_m_higher = int(gold_m_higher)
                            gold_s_higher=round(gold_s_higher,3)
                            if gold_s_higher<10:
                                gold_s_higher="0"+str(gold_s_higher)  