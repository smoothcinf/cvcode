import pandas as pd
import betfairlightweight
from betfairlightweight.filters import market_filter, price_data
from datetime import datetime, date, timedelta
from betfair_lists import betfair_teams, betfair_market_types, betfair_outcome_types


def lay_bet_calculator(stake, odds, lay_odds_betting_exchange, bet_type, fee=0.02) -> int:
    """
    Computes how much to lay to make sure the back bet is fully hedged

    :param float stake: Stake wagered on the given outcome
    :param float odds: Odds on the given bet
    :param float odds: Odds offered with the betting exchange on the given outcome
    :param str bet_type: QB/FB/RFB, must be in the list ["Qualifying bet", "Freebet", "Risk-free bet"]
    :param float fee: Fee applied by the betting exchange, 0.02 by default

    :return: Stake to be layed to neutralize position
    :rtype: int
    """
    if bet_type == "Qualifying bet":
        lay_stake = int(stake * odds / (lay_odds_betting_exchange - fee))
        return lay_stake
    elif bet_type == "Freebet":
        lay_stake = int(stake * (odds - 1) / (lay_odds_betting_exchange - fee))
        return lay_stake
    elif bet_type == "Risk-free bet":
        lay_stake = int(stake * (odds - 1) / (lay_odds_betting_exchange - fee))
        return lay_stake
    else:
        raise Exception(
            f'{bet_type} must be either "Qualifying bet", "Freebet" or "Risk-free bet"')
        return None


def hedge_bet(
        betfair_client: betfairlightweight.apiclient.APIClient,
        home_team: str,
        away_team: str,
        market: str,
        outcome: str,
        bet_type: str,
        stake: int,
        odds: float,
        date: str = date.today().isoformat(),
        continuous_output: bool = True,
        verification: bool = False) -> dict:
    """
    Assumes a logged in betfairlightweight.APIClient() session with the BETFAIR API.
    Hedges a back bet by calculating the lay stake [conditional on current market odds] and sending
    the lay order (limit order) to the exchange.

    :param betfairlightweight.apiclient.APIClient betfair_client: A logged in betfairlightweight.APIClient() session with the BETFAIR API
    :param str home_team: The home team in the game
    :param str away_team: The away team in the game
    :param str market: Market in Betfair format, e.g. Over/Under 2.5 Goals
    :param str outcome: Outcome in Betfair format, e.g. Under 2.5 Goals
    :param str bet_type: QB/FB/RFB, must be in the list ["Qualifying bet", "Freebet", "Risk-free bet"]
    :param int stake: Stake bet on the outcome
    :param float odds: Odds on the given outcome
    :param str date: The date for the game, today by default "YYYY-MM-DD"
    :param bool continuous_output: If True -> prints all the relevant information throughout the bet process
    :param bool verification: If True -> requires verification from the user to place order after printing the order book, False by default

    :return: Returns a dictionary with information about the order. If verification was set to True and the user chose not
             to place the bet, returns None.
    :rtype: dict with keys "Status", "Order status", "BetID", "Average price matched", "Size matched", "Error codes"
    """
    assert home_team in betfair_teams, f"{home_team} is not in Betfair format, please check Betfair documentation or betfair_lists.betfair_teams"
    assert away_team in betfair_teams, f"{away_team} is not in Betfair format, please check Betfair documentation or betfair_lists.betfair_teams"
    assert market in betfair_market_types, f"{market} is not in Betfair format, please check Betfair documentation or betfair_lists.betfair_markets"
    assert outcome in betfair_outcome_types, f"{outcome} is not in Betfair format, please check Betfair documentation or betfair_lists.betfair_outcomes"
    assert bet_type in ["Qualifying bet", "Freebet",
                        "Risk-free bet"], f'{bet_type} must be either "Qualifying bet", "Freebet" or "Risk-free bet"'

    """
    DOCUMENTATION THROUGHOUT THE FUNCTION CODE
    """

    """
    LOCATES THE CORRECT MARKET ID
    """
    game = f"{home_team} v {away_team}"
    market_catalogues = betfair_client.betting.list_market_catalogue(
        filter=market_filter(text_query=game, market_start_time={"from": date, "to": datetime.strftime(
            datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1), "%Y-%m-%d")}),
        max_results=1000,
    )
    market_id = None
    for obj in market_catalogues:
        if obj.market_name == market:
            market_id = obj.market_id
            break

    try:
        market_book = betfair_client.betting.list_market_book(
            market_ids=[market_id])[0]
        market_catalogue = betfair_client.betting.list_market_catalogue(
            filter=market_filter(market_ids=[market_id]),
            market_projection=["RUNNER_DESCRIPTION", "RUNNER_METADATA"])[0]
    except:
        raise Exception('Requested market is not available at Betfair')

    """
    SETS UP A DICTIONARY WITH THE DIFFERENT OUTCOMES,
    SELECTION_IDS, LAST MATCHED PRICE
    &
    PRINTS OUTCOMES AND LAST MATCHED PRICE IF continuous_output = True
    """
    runner_catalogues = market_catalogue.runners
    runner_books = market_book.runners

    outcome_dict = {}
    for i in range(len(runner_catalogues)):
        outcome_name = runner_catalogues[i].runner_name
        outcome_last_price_traded = runner_books[i].last_price_traded
        outcome_selection_id = runner_catalogues[i].selection_id
        outcome_dict[outcome_name] = {
            "selectionId": outcome_selection_id, "lastPriceTraded": outcome_last_price_traded}

    if continuous_output:
        print(f"Outcomes for the market {market} and last traded prices:")
        for result, result_dict in outcome_dict.items():
            print(result, result_dict["lastPriceTraded"])
        print("---------------------------------------------------")

    """
    PRINTS BACK AND LAY PRICES AS WELL AS AVAILABLE SIZE FOR THE GIVEN OUTCOME AND IF VERIFIED BY THE USER,
    PLACES A MARKET ORDER TO LAY THE BET.
    SHOULD BE OPTIMIZED BY BETTER UTILIZATION OF LIMIT ORDERS + LOOPS + TIME CONDITIONALS
    """

    """
    STORES SELECTION ID FOR THE OUTCOME IN sel_id
    """
    sel_id = None
    for key, val in outcome_dict.items():
        if outcome == key:
            sel_id = val['selectionId']
            break

    if sel_id is None:
        raise Exception(
            f'The parameter "outcome" must be in the list {list(outcome_dict.keys())}')

    """
    REQUESTS PRICES AND PRINTS THE [3, 3] BOOK TO THE CONSOLE IF continuous_output = True
    """
    price_filter = betfairlightweight.filters.price_projection(
        price_data=['EX_BEST_OFFERS'])

    runner_book_ex = betfair_client.betting.list_runner_book(
        market_id=market_id,
        selection_id=sel_id,
        price_projection=price_filter)[0].runners[0].ex

    back_prices = runner_book_ex.available_to_back
    lay_prices = runner_book_ex.available_to_lay

    if continuous_output:
        print(f"Current book for your selection {outcome}:")
        print("BACK PRICES")
        for i in range(1, len(back_prices) + 1):
            print(back_prices[-i])
        print("")
        print("LAY PRICES")
        for lay_price in lay_prices:
            print(lay_price)
        print("---------------------------------------------------")

    lay_price = lay_prices[0].price
    # FIX
    # FIX
    # fix this lay stake such that it takes a weighted average depending on available volume
    # FIX
    # FIX
    lay_stake = lay_bet_calculator(
        stake=stake, odds=odds, lay_odds_betting_exchange=lay_price, bet_type=bet_type)
    # FIX
    # FIX
    # fix this lay stake such that it takes a weighted average depending on available volume
    # FIX
    # FIX

    if continuous_output:
        print(
            f"To neutralize your position you will have to lay {lay_stake} SEK at odds {lay_price}.")
        print("---------------------------------------------------")

    """
    ORDER PLACING
    orderbook-workflow - https://betfair-datascientists.github.io/api/apiPythontutorial/

    allowed_deviations DEFINED BELOW MUST BE MULTIPLES OF ENTRIES IN price_increments
    TO SATISFY BETFAIR ODDS / TICK SIZE REQUIREMENTS
    """
    price_increments = {"1.01-1.99": 0.01, "2.00-2.98": 0.02,
                        "3.00-3.95": 0.05, "4.00-5.90": 0.1, "6.00-9.80": 0.2, "10.00-19.50": 0.5}
    allowed_deviations = {"1.01-1.98": 0.02, "2.00-2.96": 0.04,
                          "3.00-3.95": 0.05, "4.00-5.90": 0.1, "6.00-9.80": 0.2, "10.00-19.50": 0.5}

    """
    SPLITS INTO CASES, DEFINES OUR LIMIT PRICE FOR EACH CASE
    """
    if lay_price < 2:
        if lay_price == 1.99:
            limit_price = 2.02
        else:
            limit_price = lay_price + allowed_deviations["1.01-1.98"]
    elif lay_price >= 2 and lay_price < 3:
        if lay_price == 2.98:
            limit_price = 3.05
        else:
            limit_price = round(
                lay_price + allowed_deviations["2.00-2.96"], 2)
    elif lay_price >= 3 and lay_price < 4:
        limit_price = round(
            lay_price + allowed_deviations["3.00-3.95"], 2)
    elif lay_price >= 4 and lay_price < 6:
        limit_price = round(
            lay_price + allowed_deviations["4.00-5.90"], 2)
    elif lay_price >= 6 and lay_price < 10:
        limit_price = round(
            lay_price + allowed_deviations["6.00-9.80"], 2)
    elif lay_price >= 10 and lay_price < 20:
        limit_price = round(
            lay_price + allowed_deviations["10.00-19.50"], 2)
    else:
        raise Exception(
            "hedge_bet function not compatible with odds >= 20.00, please hedge manually")

    """
    DEFINES ORDER FILTERS
    """
    limit_order_filter = betfairlightweight.filters.limit_order(
        size=lay_stake,
        price=limit_price,
        persistence_type='LAPSE')

    instructions_filter = betfairlightweight.filters.place_instruction(
        selection_id=str(sel_id),
        order_type="LIMIT",
        side="LAY",
        limit_order=limit_order_filter)

    """
    IF verification == True, THIS SIMPLE VERIFICATION PROCESS ASSERTS
    THE USER WANTS TO SEND THE ORDER TO THE EXCHANGE
    """
    if verification:
        verification_input = input(
            "Do you want to hedge your bet by placing an order? y/n ",)
        print("---------------------------------------------------")
        if verification_input == 'y':
            """
            EXECUTION, PLACES THE LIMIT ORDER AND RETURNS CONFIRMATION DICT
            """
            order = betfair_client.betting.place_orders(
                market_id=market_id,
                instructions=[instructions_filter])

            report = order.place_instruction_reports[0]

            report_dict = {"Status": report.status, "Order status": report.order_status, "BetID": report.bet_id,
                           "Average price matched": report.average_price_matched, "Size matched": report.size_matched,
                           "Error codes": {order.error_code, report.error_code}}
            return report_dict
        else:
            print("No order was placed.")
            print("---------------------------------------------------")
            return None
    else:
        """
        IMMEDIATE EXECUTION, SENDS THE LIMIT ORDER AND RETURNS CONFIRMATION DICTIONARY
        """
        order = betfair_client.betting.place_orders(
            market_id=market_id,
            instructions=[instructions_filter])

        report = order.place_instruction_reports[0]

        report_dict = {"Status": report.status, "Order status": report.order_status, "BetID": report.bet_id,
                       "Average price matched": report.average_price_matched, "Size matched": report.size_matched,
                       "Error codes": {order.error_code, report.error_code}}
        return report_dict


def process_runner_books(runner_books):
    '''
    This function processes the runner books and returns a DataFrame with the best back/lay prices + vol for each runner
    :param runner_books:
    :return:
    '''
    best_back_prices = [runner_book.ex.available_to_back[0].price
                        if runner_book.ex.available_to_back.price
                        else 1.01
                        for runner_book
                        in runner_books]
    best_back_sizes = [runner_book.ex.available_to_back[0].size
                       if runner_book.ex.available_to_back.size
                       else 1.01
                       for runner_book
                       in runner_books]

    best_lay_prices = [runner_book.ex.available_to_lay[0].price
                       if runner_book.ex.available_to_lay.price
                       else 1000.0
                       for runner_book
                       in runner_books]
    best_lay_sizes = [runner_book.ex.available_to_lay[0].size
                      if runner_book.ex.available_to_lay.size
                      else 1.01
                      for runner_book
                      in runner_books]

    selection_ids = [runner_book.selection_id for runner_book in runner_books]
    last_prices_traded = [
        runner_book.last_price_traded for runner_book in runner_books]
    total_matched = [runner_book.total_matched for runner_book in runner_books]
    statuses = [runner_book.status for runner_book in runner_books]
    scratching_datetimes = [
        runner_book.removal_date for runner_book in runner_books]
    adjustment_factors = [
        runner_book.adjustment_factor for runner_book in runner_books]

    df = pd.DataFrame({
        'Selection ID': selection_ids,
        'Best Back Price': best_back_prices,
        'Best Back Size': best_back_sizes,
        'Best Lay Price': best_lay_prices,
        'Best Lay Size': best_lay_sizes,
        'Last Price Traded': last_prices_traded,
        'Total Matched': total_matched,
        'Status': statuses,
        'Removal Date': scratching_datetimes,
        'Adjustment Factor': adjustment_factors
    })
    return df
