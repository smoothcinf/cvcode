import scipy.optimize


def qualifying_bet_2way(stake: int, odds: float, odds_second_outcome: float) -> float:
    '''
    Computes and returns the recommended wager on the remaining outcome to achieve a fully hedged position after having placed
    a qualifying bet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2

    :rtype: list
    '''
    stake_outcome2 = stake * odds / odds_second_outcome
    return stake_outcome2


def qualifying_bet_3way(stake: int, odds: float, odds_second_outcome: float, odds_third_outcome: float) -> list:
    '''
    Computes and returns a list of recommended wagers on the remaining outcomes to achieve a fully hedged position after having placed
    a qualifying bet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2
    :param float odds_third_outcome: Odds offered on outcome 3

    :rtype: list
    '''
    stake_outcome2 = stake * odds / odds_second_outcome
    stake_outcome3 = stake * odds / odds_third_outcome
    return [stake_outcome2, stake_outcome3]


def freebet_2way(stake: int, odds: float, odds_second_outcome: float) -> float:
    '''
    Computes and returns the recommended wager on the remaining outcome to achieve a fully hedged position after having placed
    a freebet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2

    :rtype: list
    '''
    stake_outcome2 = stake * (odds - 1) / odds_second_outcome
    return stake_outcome2


def freebet_3way(stake: int, odds: float, odds_second_outcome: float, odds_third_outcome: float) -> list:
    '''
    Computes and returns a list of recommended wagers on the remaining outcomes to achieve a fully hedged position after having placed
    a freebet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2
    :param float odds_third_outcome: Odds offered on outcome 3

    :rtype: list
    '''
    stake_outcome2 = stake * (odds - 1) / odds_second_outcome
    stake_outcome3 = stake * (odds - 1) / odds_third_outcome
    return [stake_outcome2, stake_outcome3]


def rfbet_2way(stake: int, odds: float, odds_second_outcome: float) -> float:
    '''
    Computes and returns the recommended wager on the remaining outcome to achieve a fully hedged position after having placed
    a risk-free bet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2

    :rtype: list
    '''
    stake_outcome2 = stake * (odds - 1) / odds_second_outcome
    return stake_outcome2


def rfbet_3way(stake: int, odds: float, odds_second_outcome: float, odds_third_outcome: float) -> list:
    '''
    Computes and returns a list of recommended wagers on the remaining outcomes to achieve a fully hedged position after having placed
    a risk-free bet with a bookie

    :param int stake: Bet size
    :param float odds: Odds on the already placed bet
    :param float odds_second_outcome: Odds offered on outcome 2
    :param float odds_third_outcome: Odds offered on outcome 3

    :rtype: list
    '''
    stake_outcome2 = stake * (odds - 1) / odds_second_outcome
    stake_outcome3 = stake * (odds - 1) / odds_third_outcome
    return [stake_outcome2, stake_outcome3]


def exchange_calculator(stake, odds, lay_odds, bet_type, exchange_fee=0.02) -> int:
    """
    Computes how much to lay to make sure the back bet is fully hedged

    :param float stake: Stake wagered on the given outcome
    :param float odds: Odds on the given bet
    :param float lay_odds: Lay odds offered with the betting exchange on the given outcome
    :param str bet_type: QB/FB/RFB, must be in the list ["Qualifying bet", "Freebet", "Risk-free bet"]
    :param float exchange_fee: Fee applied by the betting exchange, 0.02 by default

    :return: Stake to be layed to neutralize position
    :rtype: int
    """
    if bet_type == "Qualifying bet":
        lay_stake = int(stake * odds / (lay_odds_betting_exchange - exchange_fee))
        return lay_stake
    elif bet_type == "Freebet":
        lay_stake = int(stake * (odds - 1) / (lay_odds_betting_exchange - exchange_fee))
        return lay_stake
    elif bet_type == "Risk-free bet":
        lay_stake = int(stake * (odds - 1) / (lay_odds_betting_exchange - exchange_fee))
        return lay_stake
    else:
        raise Exception(
            f'{bet_type} must be either "Qualifying bet", "Freebet" or "Risk-free bet"')

        
"""
NECESSARY FUNCTIONS FOR THE MASTER CALCULATOR
"""


def weighted_odds(stakes_vector, odds_vector) -> float:
    """
    Computes the weighted odds for a given set of bets (stake, odds)
    """
    total_payoff = 0
    for i in range(len(stakes_vector)):
        total_payoff += stakes_vector[i] * odds_vector[i]
    weighted_odds = total_payoff / sum(stakes_vector)
    return weighted_odds


def return_to_player_2way(odds_1: float, odds_2: float) -> float:
    '''
    Computes how much margin is applied to the game given the two odds

    :param: float odds_1: The odds offered on outcome 1
    :param: float odds_2: The odds offered on outcome 2

    :return: Percentage of wagered money returned to the players in decimal form with 1 being 100 %
    :rtype: float

    '''
    return_to_player = 1 / (1 / odds_1 + 1 / odds_2)
    return return_to_player


def return_to_player_3way(odds_1: float, odds_X: float, odds_2: float) -> float:
    '''
    Computes how much margin is applied to the game given the three odds

    :param: float odds_1: The odds offered on outcome 1
    :param: float odds_1: The odds offered on outcome X
    :param: float odds_1: The odds offered on outcome 2

    :return: Percentage of wagered money returned to the players in decimal form with 1 being 100 %
    :rtype: float

    '''
    return_to_player = 1 / (1 / odds_1 + 1 / odds_X + 1 / odds_2)
    return return_to_player


"""
MASTER CALCULATORS
"""


def master_calculator_2way(wagerB_1, oddsB_1, wagerB_2, oddsB_2,
                           wagerR_1, oddsR_1, wagerR_2, oddsR_2,
                           wagerF_1, oddsF_1, wagerF_2, oddsF_2,
                           odds_1, odds_2,
                           rf_stake_returned_as_freebet=False) -> list:
    """
    Computes and returns a list of recommended wagers on the two outcomes to achieve a fully hedged position after having placed
    any combination of qualifying, risk-free and freebets with any combination of bookies

    :param float wagerB_1: Total size wagered on qualifying bets on outcome 1
    :param float oddsB_1: Weighted odds qualifying bets, outcome 1
    :param float wagerB_2: Total size wagered on qualifying bets on outcome 2
    :param float oddsB_2: Weighted odds qualifying bets, outcome 2

    :param float wagerR_1: Total size wagered on risk-free bets on outcome 1
    :param float oddsR_1: Weighted odds risk-free bets, outcome 1
    :param float wagerR_2: Total size wagered on risk-free bets on outcome 2
    :param float oddsR_2: Weighted odds risk-free bets, outcome 2

    :param float wagerF_1: Total size wagered on freebets on outcome 1
    :param float oddsF_1: Weighted odds freebets, outcome 1
    :param float wagerF_2: Total size wagered on freebets on outcome 2
    :param float oddsF_2: Weighted odds freebets, outcome 2

    :param float odds_1: Best available market odds to use for hedging purposes on outcome 1
    :param float odds_2: Best available market odds to use for hedging purposes on outcome 2

    :param bool rf_stake_returned_as_freebet: False by default, fill in whether returned stake on risk-free bets are in freebet credits or cash,
                                        - if in freebet credits, set param to True
                                        - if in cash, set param to False

    :return: List of recommended wagers [RW_outcome1, RW_outcome2], RW = Recommended Wager
    :rtype: list
    """

    """
    SETS UP NECESSARY PARAMETERS DEPENDING ON THE TYPE OF RISK-FREE BET OFFERED.
    """
    if not rf_stake_returned_as_freebet:
        share_returnedR_1 = 1
        share_returnedR_2 = 1
    else:
        share_returnedR_1 = 0.7
        share_returnedR_2 = 0.7

    """
    SETS UP INTERNAL PAYOFF FUNCTIONS ACTING ON THE FUNCTION PARAMETERS
    """

    def payoff_outcome_1(stakes_vector: list) -> float:
        """
        Computes the payoff in the case where outcome 1 occurs

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: payoff in dollars
        :rtype: float
        """
        wager_1 = stakes_vector[0]
        wager_2 = stakes_vector[1]
        payoff = wagerB_1 * (oddsB_1 - 1) - wagerB_2 + wagerR_1 * (oddsR_1 - 1) - (1 - share_returnedR_2) * wagerR_2 + wagerF_1 * (oddsF_1 - 1) + \
            wager_1 * (odds_1 - 1) - wager_2
        return payoff

    def payoff_outcome_2(stakes_vector: list) -> float:
        """
        Computes the payoff in the case where outcome 2 occurs

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: payoff in dollars
        :rtype: float
        """
        wager_1 = stakes_vector[0]
        wager_2 = stakes_vector[1]
        payoff = wagerB_2 * (oddsB_2 - 1) - wagerB_1 + wagerR_2 * (oddsR_2 - 1) - (
            1 - share_returnedR_1) * wagerR_1 + wagerF_2 * (oddsF_2 - 1) + wager_2 * (odds_2 - 1) - wager_1
        return payoff

    """
    OUR AIM IS TO FIND THE STAKES VECTOR WHICH MAXIMIZES OUR NET PROFIT GIVEN THE FOLLOWING CONSTRAINTS:
    wager_1 ≥ 0, wager_2 ≥ 0
    payoff_outcome_1 = payoff_outcome_2 WHICH TRANSLATES INTO THE CONDITION:
    payoff_outcome_1 - payoff_outcome_2 = 0

    IN CASE THE HOUSE EDGE IS NEGATIVE (E.G. POSSIBLE BY COMBINING ODDS FROM DIFFERENT BETTING SOURCES), NAIVELY APPLYING
    AN OPTIMIZATION ALGORITHM WILL RESULT IN RECOMMENDED "INFINITE" WAGERS SINCE ARBITRAGE OPPORTUNITIES (IN PRACTICE NOT EXECUTABLE)
    EXIST, HENCE IN THIS CASE A SLIGHT ADJUSTMENT IS NECESSARY FOR THE RESULT TO CONVERGE.
    WE SOLVE IT BY FINDING max{payoff_outcome_1, payoff_outcome_2} AND SETTING RW_outcome(i) = 0 IF
    max{} = payoff_outcome_i SINCE NO MONEY SHOULD BE WAGERED ON THIS OUTCOME
    """

    def prepare_minimization(stakes_vector: list) -> float:
        """
        Prepares for optimization by returning -payoff since the scipy algorithms minimizes
        while our objective is to maximize

        The choice of payoff function is arbitrary since our main constraint forces them
        all to be equal

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: -payoff in dollars
        :rtype: float
        """
        return -payoff_outcome_1(stakes_vector)

    """
    SPLITS INTO CASES DEPENDING ON RTP OFFERED BY SPECIFIED ODDS.
    UNDER NORMAL CIRCUMSTANCES THE FIRST CASE WILL COME INTO PLAY.
    """
    rtp = return_to_player_2way(odds_1, odds_2)

    if rtp < 1:
        """
        SETS UP CONSTRAINTS AND PRODUCES THE RESULT
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
        """
        initial_guess = (0, 0)
        bounds = ((0, None), (0, None))
        constraints = (
            {'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_2(x)})
        result = scipy.optimize.minimize(
            fun=prepare_minimization, x0=initial_guess, bounds=bounds, constraints=constraints)

        recommended_wagers = [int(result.x[0]), int(result.x[1])]
        return recommended_wagers

    else:
        """
        SETS UP CONSTRAINTS AND PRODUCES THE RESULT
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
        """
        payoffs = [payoff_outcome_1([0, 0]), payoff_outcome_2([0, 0])]
        index = None
        for payoff in payoffs:
            if payoff == max(payoffs):
                index = payoffs.index(payoff)
                break
        if index is None:
            raise Exception(
                "There was a problem with the algorithm, please check rtp >= 1 case")

        else:
            if index == 0:
                bounds = ((0, 0), (0, None))
            elif index == 1:
                bounds = ((0, None), (0, 0))

            initial_guess = (0, 0)
            constraints = (
                {'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_2(x)})
            result = scipy.optimize.minimize(
                fun=prepare_minimization, x0=initial_guess, bounds=bounds, constraints=constraints)

            recommended_wagers = [int(result.x[0]), int(result.x[1])]
            return recommended_wagers


def master_calculator_3way(wagerB_1, oddsB_1, wagerB_X, oddsB_X, wagerB_2, oddsB_2,
                           wagerR_1, oddsR_1, wagerR_X, oddsR_X, wagerR_2, oddsR_2,
                           wagerF_1, oddsF_1, wagerF_X, oddsF_X, wagerF_2, oddsF_2,
                           odds_1, odds_X, odds_2,
                           rf_stake_returned_as_freebet=False) -> list:
    """
    Computes and returns a list of recommended wagers on the three outcomes to achieve a fully hedged position after having placed
    any combination of qualifying, risk-free and freebets with any combination of bookies

    :param float wagerB_1: Total size wagered on qualifying bets on outcome 1
    :param float oddsB_1: Weighted odds qualifying bets, outcome 1
    :param float wagerB_X: Total size wagered on qualifying bets on outcome X
    :param float oddsB_X: Weighted odds qualifying bets, outcome X
    :param float wagerB_2: Total size wagered on qualifying bets on outcome 2
    :param float oddsB_2: Weighted odds qualifying bets, outcome 2

    :param float wagerR_1: Total size wagered on risk-free bets on outcome 1
    :param float oddsR_1: Weighted odds risk-free bets, outcome 1
    :param float wagerR_X: Total size wagered on risk-free bets on outcome X
    :param float oddsR_X: Weighted odds risk-free bets, outcome X
    :param float wagerR_2: Total size wagered on risk-free bets on outcome 2
    :param float oddsR_2: Weighted odds risk-free bets, outcome 2

    :param float wagerF_1: Total size wagered on freebets on outcome 1
    :param float oddsF_1: Weighted odds freebets, outcome 1
    :param float wagerF_X: Total size wagered on freebets on outcome X
    :param float oddsF_X: Weighted odds freebets, outcome X
    :param float wagerF_2: Total size wagered on freebets on outcome 2
    :param float oddsF_2: Weighted odds freebets, outcome 2

    :param float odds_1: Best available market odds to use for hedging purposes on outcome 1
    :param float odds_X: Best available market odds to use for hedging purposes on outcome X
    :param float odds_2: Best available market odds to use for hedging purposes on outcome 2

    :param bool rf_stake_returned_as_freebet: False by default, fill in whether returned stake on risk-free bets are in freebet credits or cash,
                                        - if in freebet credits, set param to True
                                        - if in cash, set param to False

    :return: List of recommended wagers [RW_outcome1, RW_outcomeX, RW_outcome2], RW = Recommended Wager
    :rtype: list
    """

    """
    SETS UP NECESSARY PARAMETERS DEPENDING ON THE TYPE OF RISK-FREE BET OFFERED.
    """
    if not rf_stake_returned_as_freebet:
        share_returnedR_1 = 1
        share_returnedR_X = 1
        share_returnedR_2 = 1
    else:
        share_returnedR_1 = 0.7
        share_returnedR_X = 0.7
        share_returnedR_2 = 0.7

    """
    SETS UP INTERNAL PAYOFF FUNCTIONS ACTING ON THE FUNCTION PARAMETERS
    """

    def payoff_outcome_1(stakes_vector: list) -> float:
        """
        Computes the payoff in the case where outcome 1 occurs

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: payoff in dollars
        :rtype: float
        """
        wager_1 = stakes_vector[0]
        wager_X = stakes_vector[1]
        wager_2 = stakes_vector[2]
        payoff = wagerB_1 * (oddsB_1 - 1) - wagerB_X - wagerB_2 + wagerR_1 * (oddsR_1 - 1) - (1 - share_returnedR_X) * wagerR_X - \
            (1 - share_returnedR_2) * wagerR_2 + wagerF_1 * (oddsF_1 - 1) + \
            wager_1 * (odds_1 - 1) - wager_X - wager_2
        return payoff

    def payoff_outcome_X(stakes_vector: list) -> float:
        """
        Computes the payoff in the case where outcome X occurs

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: payoff in dollars
        :rtype: float
        """
        wager_1 = stakes_vector[0]
        wager_X = stakes_vector[1]
        wager_2 = stakes_vector[2]
        payoff = wagerB_X * (oddsB_X - 1) - wagerB_1 - wagerB_2 + wagerR_X * (oddsR_X - 1) - (1 - share_returnedR_1) * wagerR_1 - \
            (1 - share_returnedR_2) * wagerR_2 + wagerF_X * (oddsF_X - 1) + \
            wager_X * (odds_X - 1) - wager_1 - wager_2
        return payoff

    def payoff_outcome_2(stakes_vector: list) -> float:
        """
        Computes the payoff in the case where outcome 2 occurs

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: payoff in dollars
        :rtype: float
        """
        wager_1 = stakes_vector[0]
        wager_X = stakes_vector[1]
        wager_2 = stakes_vector[2]
        payoff = wagerB_2 * (oddsB_2 - 1) - wagerB_1 - wagerB_X + wagerR_2 * (oddsR_2 - 1) - (1 - share_returnedR_1) * wagerR_1 - \
            (1 - share_returnedR_X) * wagerR_X + wagerF_2 * (oddsF_2 - 1) + \
            wager_2 * (odds_2 - 1) - wager_1 - wager_X
        return payoff

    """
    OUR AIM IS TO FIND THE STAKES VECTOR WHICH MAXIMIZES OUR NET PROFIT GIVEN THE FOLLOWING CONSTRAINTS:
    wager_1 ≥ 0, wager_X ≥ 0, wager_2 ≥ 0
    payoff_outcome_1 = payoff_outcome_X = payoff_outcome_2 WHICH TRANSLATES INTO THE TWO CONDITIONS:
    payoff_outcome_1 - payoff_outcome_X = 0
    payoff_outcome_1 - payoff_outcome_2 = 0

    IN CASE THE HOUSE EDGE IS NEGATIVE (E.G. POSSIBLE BY COMBINING ODDS FROM DIFFERENT BETTING SOURCES), NAIVELY APPLYING
    AN OPTIMIZATION ALGORITHM WILL RESULT IN RECOMMENDED "INFINITE" WAGERS SINCE ARBITRAGE OPPORTUNITIES (IN PRACTICE NOT EXECUTABLE)
    EXIST, HENCE IN THIS CASE A SLIGHT ADJUSTMENT IS NECESSARY FOR THE RESULT TO CONVERGE.
    WE SOLVE IT BY FINDING max{payoff_outcome_1, payoff_outcome_X, payoff_outcome_2} AND SETTING RW_outcome(i) = 0 IF
    max{} = payoff_outcome_i SINCE NO MONEY SHOULD BE WAGERED ON THIS OUTCOME
    """

    def prepare_minimization(stakes_vector: list) -> float:
        """
        Prepares for optimization by returning -payoff since the scipy algorithms minimizes
        while our objective is to maximize

        The choice of payoff function is arbitrary since our main constraint forces them
        all to be equal

        :param: list stakes_vector: A List containing the stakes on the three outcomes. E.g. [100, 240, 652] if 100 $
                was wagered on the first outcome, 240 $ on the second one and so on...

        :return: -payoff in dollars
        :rtype: float
        """
        return -payoff_outcome_1(stakes_vector)

    """
    SPLITS INTO CASES DEPENDING ON RTP OFFERED BY SPECIFIED ODDS.
    UNDER NORMAL CIRCUMSTANCES THE FIRST CASE WILL COME INTO PLAY.
    """
    rtp = return_to_player_3way(odds_1, odds_X, odds_2)

    if rtp < 1:
        """
        SETS UP CONSTRAINTS AND PRODUCES THE RESULT
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
        """
        initial_guess = (0, 0, 0)
        bounds = ((0, None), (0, None), (0, None))
        constraints = ({'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_X(x)},
                       {'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_2(x)})
        result = scipy.optimize.minimize(
            fun=prepare_minimization, x0=initial_guess, bounds=bounds, constraints=constraints)

        recommended_wagers = [int(result.x[0]), int(
            result.x[1]), int(result.x[2])]
        return recommended_wagers

    else:
        """
        SETS UP CONSTRAINTS AND PRODUCES THE RESULT
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
        """
        payoffs = [payoff_outcome_1([0, 0, 0]), payoff_outcome_X(
            [0, 0, 0]), payoff_outcome_2([0, 0, 0])]
        index = None
        for payoff in payoffs:
            if payoff == max(payoffs):
                index = payoffs.index(payoff)
                break
        if index is None:
            raise Exception(
                "There was a problem with the algorithm, please check rtp >= 1 case")

        else:
            if index == 0:
                bounds = ((0, 0), (0, None), (0, None))
            elif index == 1:
                bounds = ((0, None), (0, 0), (0, None))
            else:
                bounds = ((0, None), (0, None), (0, 0))

            initial_guess = (0, 0, 0)
            constraints = ({'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_X(x)},
                           {'type': 'eq', 'fun': lambda x: payoff_outcome_1(x) - payoff_outcome_2(x)})
            result = scipy.optimize.minimize(
                fun=prepare_minimization, x0=initial_guess, bounds=bounds, constraints=constraints)

            recommended_wagers = [int(result.x[0]), int(
                result.x[1]), int(result.x[2])]
            return recommended_wagers
