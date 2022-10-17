import betfairlightweight
from mb_functions import hedge_bet
from datetime import datetime
from pandas import ExcelFile

"""
USE trading.login() + CERTS INSTEAD OF trading.login.interactive()
"""

"""
INPUT DATA + PARAMETERS
"""
USERNAME = "FILL IN USERNAME/EMAIL LOGIN"
PASSWORD = "FILL IN PASSWORD"
APP_KEY = "FILL IN APP_KEY"
locale = "FILL IN LOCALE"
continuous_output = False
verification = False

"""
FEED THE PATH TO YOUR EXCEL FILE, THEN RUN THE SCRIPT.
IT WILL LOOP THROUGH ALL THE BETS IN YOUR EXCEL_FILE, 
HEDGING THEM ONE AT A TIME.
"""
bet_sheet = ExcelFile("PATH_TO_EXCEL_FILE")
df = bet_sheet.parse(bet_sheet.sheet_names[0])
list_bet_dicts = df.to_dict(orient='records')

if list_bet_dicts:
    trading = betfairlightweight.APIClient(
        username=USERNAME,
        password=PASSWORD,
        app_key=APP_KEY,
        locale=locale)

    trading.login_interactive()
    if not trading.session_expired:
        print("---------------------------------------------------")
        print("YOU ARE NOW LOGGED IN!")
        print("---------------------------------------------------")

    for bet_dict in list_bet_dicts:
        print(f"GAME: {bet_dict['Home']} v {bet_dict['Away']}")
        print("---------------------------------------------------")
        try: 
            hedge = hedge_bet(
                betfair_client=trading,
                home_team=bet_dict['Home'],
                away_team=bet_dict['Away'],
                market=bet_dict['Market'],
                outcome=bet_dict['Outcome'],
                bet_type=bet_dict['Bet type'],
                stake=bet_dict['Stake'],
                odds=bet_dict['Odds'],
                date=datetime.strftime(bet_dict['Date'], "%Y-%m-%d"),
                continuous_output=continuous_output,
                verification=verification)
            if hedge:
                for key, val in hedge.items():
                    print(key + ":", val)
                print("---------------------------------------------------")
        except Exception as e: 
            print("There was a problem hedging the bet for this game, please check manually")
            print(f"Error description: {type(e)} - {e}")
            continue

    trading.logout()
    if trading.session_expired:
        print("YOU ARE NOW LOGGED OUT!")
        print("---------------------------------------------------")

else:
    print("No bets to hedge, the Excel sheet is empty!")
