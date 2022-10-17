from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import requests


def atg_api_scraper(
    datum: str,
    bankod: str,
    spelform: str,
    start_avd: int,
    slut_avd: int,
    spelform_start_lopp: int = None,
) -> list:
    """
    Skrapar hästnamn, streckspelsprocent (om streckspel), vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.

    :param: str datum: Tävlingsdatum, t.ex. "2022-05-31"
    :param: str bankod: Bankod, observera att detta ska vara en *string*
    :param: str spelform: Valfri spelform ur listan ['V75', 'V86', 'GS75', 'V64', 'V65', 'V5', 'V4', 'V&P']
    :param: int start_avd: Vilken avdelning/vilket lopp ska scrapern inleda med
    :param: int slut_avd: Vilken avdelning/vilket lopp ska scrapern avsluta med
    :param: int spelform_start_lopp: Givet att streckspelsinformation efterfrågas, vilket lopp börjar spelformen i?

    :return: Returnerar en lista av (antal hästar x 4) alternativt (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Streckspelsprocent, Vinnarodds, Platsodds] alternativt [Hästnamn, Vinnarodds, Platsodds]
    :rtype: list of pd.DataFrames
    """
    assert spelform in ['V75', 'V86', 'GS75', 'V64', 'V65', 'V5', 'V4',
                        'V&P'], f"{spelform} är ej en giltig spelform, alternativt är inte scrapern kompatibel med denna spelform"

    if spelform == 'V&P':
        # DETTA FALL HANTERAR ENLOPPSSPEL [VINNARE, PLATS]

        # Initierar en lista som ska innehålla dataframes för samtliga lopp
        pd_lista = []

        for loppnr in range(start_avd, slut_avd + 1):
            try:
                # Skapar en tom dataframe för loppet
                lopp_df = pd.DataFrame(columns=["Häst", "VOdds", "POdds"])

                # Requestar all data från ATG's API, loopar igenom och extraherar relevant information
                url = f"https://www.atg.se/services/racinginfo/v1/api/games/vinnare_{datum}_{bankod}_{loppnr}"
                response = requests.get(url)
                response_json = response.json()
                startande_hästar = response_json['races'][0]['starts']
                for häst in startande_hästar:
                    hästnamn = häst['horse']['name']
                    vodds = häst['pools']['vinnare']['odds'] / 100
                    podds = häst['pools']['plats']['minOdds'] / 100

                    # Lägger denna data till dataframen för loppet
                    dummy_df = lopp_df
                    ny_rad = pd.DataFrame(
                        [[hästnamn, vodds, podds]], columns=lopp_df.columns)
                    lopp_df = pd.concat([dummy_df, ny_rad], ignore_index=True)
            except:
                print(
                    f"Det uppstod ett problem i samband med inhämtningen av data för lopp {loppnr}")

            # Slutligen läggs dataframen för det nu färdiga loppet till pd_lista
            pd_lista.append(lopp_df)

        return pd_lista

    else:
        # DETTA FALL HANTERAR STRECKSPEL

        # Initierar en lista som ska innehålla dataframes för samtliga lopp
        pd_lista = []

        # Requestar all data från ATG's API, loopar igenom och extraherar relevant information
        url = f"https://www.atg.se/services/racinginfo/v1/api/games/{spelform}_{datum}_{bankod}_{spelform_start_lopp}"
        response = requests.get(url)
        response_json = response.json()

        for avd_nr in range(start_avd, slut_avd + 1):
            try:
                # Skapar en tom dataframe för loppet
                lopp_df = pd.DataFrame(
                    columns=["Häst", f"{spelform}-procent", "VOdds", "POdds"])
                startande_hästar = response_json['races'][avd_nr - 1]['starts']
                for häst in startande_hästar:
                    hästnamn = häst['horse']['name']
                    spelform_procent = häst['pools'][spelform]['betDistribution'] / 100
                    vodds = häst['pools']['vinnare']['odds'] / 100
                    podds = häst['pools']['plats']['minOdds'] / 100

                    # Lägger denna data till dataframen för loppet
                    dummy_df = lopp_df
                    ny_rad = pd.DataFrame(
                        [[hästnamn, spelform_procent, vodds, podds]], columns=lopp_df.columns)
                    lopp_df = pd.concat([dummy_df, ny_rad], ignore_index=True)
            except:
                print(
                    f"Det uppstod ett problem i samband med inhämtningen av data för avdelning {avd_nr}")

            # Slutligen läggs dataframen för det nu färdiga loppet till pd_lista
            pd_lista.append(lopp_df)

        return pd_lista


def atg_selenium_scraper_VP(
    datum: str,
    bana: str,
    från_lopp: int,
    till_lopp: int,
    wait_time: float = 0.5,
) -> list:
    """
    Skrapar hästnamn, vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.

    :param: str datum: Tävlingsdatum, t.ex. "2022-05-31"
    :param: str bana: Bana, t.ex. "jagersro"
    :param: från_lopp: Första lopp som ska skrapas
    :param: till_lopp: Sista lopp som ska skrapas
    :param: float wait_time: Antal sekunder programmet ska vänta efter varje klick/sidinladdning etc, 0.5 sekund som standard

    :rtype: list of pd.DataFrames: Returnerar en lista av (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Vinnarodds, Platsodds]

    """
    # Initierar sessionen, se till att ha chromedriver i "Program"
    path = "/Applications/chromedriver"
    driver = webdriver.Chrome(path)

    # Lista som längre fram kommer spara samtliga lopp
    pd_lista = []

    for loppnr in range(från_lopp, till_lopp + 1):
        # Använder platslänken då denna innehåller både plats och vinnarodds som standard
        driver.get(
            f"https://www.atg.se/spel/{datum}/plats/{bana}/lopp{loppnr}")

        # Väntar {wait_time} sekunder mellan loppen för att datan ska hinna laddas in ordentligt
        time.sleep(wait_time)

        hastnamn_element = driver.find_elements(By.CLASS_NAME, "horse-col")
        vinnarodds_element = driver.find_elements(By.CLASS_NAME, "vOdds-col")
        platsodds_element = driver.find_elements(By.CLASS_NAME, "pOdds-col")

        # Skapar en tom dataframe för loppet
        lopp_df = pd.DataFrame(columns=["Häst", "VOdds", "POdds"])

        for hästnr in range(1, len(hastnamn_element)):
            # Notera att listorna innehåller rubriker, därav börjar loopen på 1
            # samtidigt som len(hastnamn_element) = antal hästar + 1.

            # Skalar bort startnummer då det kommer med i början av varje string
            if hästnr < 10:
                hästnamn = hastnamn_element[hästnr].text[1:]
            else:
                hästnamn = hastnamn_element[hästnr].text[2:]

            # Kontrollerar om häst är STRUKEN.
            if not vinnarodds_element[hästnr].text == "EJ":
                vodds = float(
                    vinnarodds_element[hästnr].text.replace(",", "."))
                podds = float(
                    platsodds_element[hästnr].text.replace(",", "."))

            # Om häst är STRUKEN sätts vinnarodds och platsodds till 999.
            else:
                vodds = 999
                podds = 999

            # Lägger denna data till dataframen för loppet
            dummy_df = lopp_df
            ny_rad = pd.DataFrame(
                [[hästnamn, vodds, podds]], columns=lopp_df.columns)
            lopp_df = pd.concat([dummy_df, ny_rad], ignore_index=True)

        # Slutligen läggs dataframen för det nu färdiga loppet till pd_lista
        pd_lista.append(lopp_df)

    driver.quit()

    return pd_lista


def bet365_scraper(
    bana: str,
    från_lopp: int,
    till_lopp: int,
    veckodag: str,
    land: str = "Sverige",
    H2H: bool = False,
    H3H: bool = False,
    wait_time: float = 1,
    initial_wait: float = 2,
) -> list:
    """
    Skrapar som standard hästnamn, vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.
    Kan också skrapa H2H samt H3H odds.

    :param: str bana: Bana, t.ex. "Jägersro"
    :param: int från_lopp: Första lopp som ska skrapas
    :param: int till_lopp: Sista lopp som ska skrapas
    :param: str veckodag: Vilken veckodag är det tävlingarna körs på? T.ex. "Torsdag"
    :param: str land: Land, "Sverige" som standard
    :param: bool H2H: Om H2H sätts till True skrapas aktuella H2H-odds från Bet365
    :param: bool H3H: Om H3H sätts till True skrapas aktuella H3H-odds från Bet365
    :param: float wait_time: Antal sekunder programmet ska vänta efter varje klick/sidinladdning etc, 1 sekund som standard
    :param: float initial_wait_site: Antal sekunder programmet ska vänta efter att get(bet365) callats för att sidan ska hinna laddas in ordentligt
            2 sekunder som standard

    :rtype: list of pd.DataFrames: Returnerar en lista av (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Vinnarodds, Platsodds]

            Om H2H == True består dataframen istället av fyra kolumner,
            [Hästnamn A, Häst A odds, Hästnamn B, Häst B odds]

            På samma sätt skapas sex kolumner i H3H-fallet.
    """
    # Initierar sessionen, se till att ha chromedriver i "Program"
    path = "/Applications/chromedriver"
    driver = webdriver.Chrome(path)

    # Går till bet365's hemsida
    driver.get(
        "https://www.bet365.com/")

    # Väntar {initial_wait} sekunder för sidan ska laddas in och att HTML-koden ska laddas in ordentligt
    time.sleep(initial_wait)

    # Accepterar cookies
    driver.find_element(
        By.CLASS_NAME, "ccm-CookieConsentPopup_Accept").click()
    time.sleep(wait_time)

    # Identifierar rubrikerna för samtliga sporter i listan ute till vänster hos bet365
    sporter = driver.find_elements(By.CLASS_NAME, "wn-PreMatchItem")

    # Går igenom listan tills "Trav" hittats och klickar vidare in till travet
    for sport in sporter:
        if sport.text == "Trav":
            sport.click()
            break
        elif sport.text != "Trav" and sporter.index(sport) == len(sporter) - 1:
            print("Det verkar som att Trav inte finns tillgängligt hos Bet365 just nu")
            driver.quit()
            return
    time.sleep(wait_time)

    # Identifierar veckodagar för de olika tävlingsdagar Bet365 erbjuder spel till
    veckodagar = driver.find_elements(By.CLASS_NAME, "rsm-ButtonBarButton")

    # Går igenom alla dagar som ligger uppe tills rätt dag hittats och klickar vidare
    for dag in veckodagar:
        if dag.text == veckodag:
            dag.click()
            break
        elif dag.text != veckodag and veckodagar.index(dag) == len(veckodagar) - 1:
            print(f"Lopp till {veckodag} saknas hos Bet365 just nu")
            driver.quit()
            return
    time.sleep(wait_time)

    if H2H == False and H3H == False:
        # Detta scenario innebär att vinnarodds och platsodds ska scrapeas
        # för dem olika loppen

        # Sätter upp listan som kommer innehålla dataframes för samtliga lopp
        pd_lista = []

        # Identifierar aktuella travtävlingar och sparar rubrikerna för dessa
        tävlingar = driver.find_elements(
            By.CLASS_NAME, "rsm-AusMeetingHeader_MeetingName")

        # Loopar igenom listan "tävlingar" tills land och bana matchar, avslutar med att klicka på
        # dessa tävlingar
        for tävling in tävlingar:
            if tävling.text == f"{land} - {bana}":
                tävling.click()
                break

        # Kontrollerar vilka lopp som ska scrapeas, och börjar gå igenom dessa
        # ett lopp i taget
        for loppnr in range(från_lopp, till_lopp + 1):
            lopp_df = pd.DataFrame(
                columns=["Häst", "VOdds", "POdds"])
            time.sleep(wait_time)

            # Lista innehållande samtliga lopp för den aktuella tävlingsdagen
            alla_lopp = driver.find_elements(
                By.CLASS_NAME, "srl-ParticipantRacingRaceTab-number")

            try:
                # Hittar loppets position på sidan och klickar in, påbörjar därefter skrapningen
                for lopp in alla_lopp:
                    if float(lopp.text) == loppnr:
                        lopp.click()
                        time.sleep(wait_time)

                        # Samlar in elementen innehållande all information för varje startande ekipage
                        samtliga_startande = driver.find_elements(
                            By.CLASS_NAME, "srt-ParticipantTrottingINT")

                        for ekipage in samtliga_startande:
                            # Sparar för varje ekipage hästnamn, vinnarodds och platsodds
                            hästnamn = ekipage.find_element(
                                By.CLASS_NAME, "srt-ParticipantDetailsRacingINT_RunnerName").text
                            odds = ekipage.find_elements(
                                By.CLASS_NAME, "srt-ParticipantTrottingOddsINT")
                            vodds = float(odds[0].text)
                            podds = float(odds[1].text)

                            # Lägger denna data till dataframen för loppet
                            dummy_df = lopp_df
                            ny_rad = pd.DataFrame(
                                [[hästnamn, vodds, podds]], columns=lopp_df.columns)
                            lopp_df = pd.concat(
                                [dummy_df, ny_rad], ignore_index=True)
                        break
            except:
                print(
                    f"Ett problem uppstod i inhämtningen av hästnamn och odds för lopp {loppnr}, kontrollera så att odds faktiskt ligger uppe för loppet")
                pass

            # När loppet är färdigt läggs dataframen för loppet till pd_lista
            pd_lista.append(lopp_df)

        driver.quit()

        return pd_lista

    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H

    elif H2H == True and H3H == False:
        # Detta scenario innebär att H2H-odds ska skrapas
        print("För närvarande ej kompatibel med skrapning av H2H-odds")
        driver.quit()

    elif H2H == False and H3H == True:
        # Detta scenario innebär att H3H-odds ska skrapas
        print("För närvarande ej kompatibel med skrapning av H3H-odds")
        driver.quit()

    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H
    # GÖR KLART H2H OCH H3H

    else:
        print("Om du vill skrapa både H2H odds och H3H odds, gör detta genom att calla funktionen två gånger.")
        driver.quit()


def svenskaspel_scraper(
    bana: str,
    från_lopp: int,
    till_lopp: int,
    H2H: bool = False,
    wait_time: float = 1,
    initial_wait: float = 2,
) -> list:
    """
    Skrapar som standard hästnamn, vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.
    Kan också skrapa H2H oods.

    :param: str bana: Bana, t.ex. "solvalla"
    :param: int från_lopp: Första lopp som ska skrapas
    :param: int till_lopp: Sista lopp som ska skrapas
    :param: bool H2H: Om H2H sätts till True skrapas aktuella H2H-odds från Svenska Spel för varje angivet lopp
    :param: float wait_time: Antal sekunder programmet ska vänta efter varje klick/sidinladdning etc, 1 sekund som standard
    :param: float initial_wait_site: Antal sekunder programmet ska vänta efter att get(bet365) callats för att sidan ska hinna laddas in ordentligt
            2 sekunder som standard

    :rtype: list of pd.DataFrames: Returnerar en lista av (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Vinnarodds, Platsodds]
            Om H2H == True består dataframen istället av fyra kolumner,
            [Hästnamn A, Häst A odds, Hästnamn B, Häst B odds]
    """
    # Initierar sessionen, se till att ha chromedriver i "Program"
    path = "/Applications/chromedriver"
    driver = webdriver.Chrome(path)

    # Går in på startsidan för Svenska Spel och accepterar cookies
    driver.get("https://spela.svenskaspel.se/odds")
    time.sleep(initial_wait)

    # Beroende på storlek på skärm kan man behöva scrolla ner för att godkänna cookies
    try:
        driver.find_element(
            By.CLASS_NAME, "js-dialog-button-scrollable").click()
        time.sleep(wait_time)
        cookies_btn_container = driver.find_element(
            By.CLASS_NAME, "dialog-button-container")
        cookies_btn_container.find_element(
            By.CLASS_NAME, "dialog-button-primary").click()
        time.sleep(wait_time)
    except:
        # Ifall man inte behöver scrolla, kommer koden ovan returnera 'error'
        # vilket exekverar nedan kod vilken inte inkluderar scrollning
        cookies_btn_container = driver.find_element(
            By.CLASS_NAME, "dialog-button-container")
        cookies_btn_container.find_element(
            By.CLASS_NAME, "dialog-button-primary").click()
        time.sleep(wait_time)

    if H2H == False:
        # Detta scenario innebär att vinnarodds och platsodds ska scrapeas
        # för dem olika loppen

        # Sätter upp listan som kommer innehålla dataframes för samtliga lopp
        pd_lista = []

        # Håller koll på hur många lopp oddsen ej lagts ut till
        antal_lopp_odds_ej_kunnat_hämtas = 0

        # Loopar igenom varje lopp och hämtar ner vinnarodds och platsodds för varje häst
        for loppnr in range(från_lopp, till_lopp + 1):
            # Sätter upp en dataframe för loppet
            lopp_df = pd.DataFrame(columns=["Häst", "VOdds", "POdds"])

            try:
                driver.get(
                    f"https://spela.svenskaspel.se/odds/sports/travsport/{bana}-lopp-{loppnr}")
                time.sleep(wait_time)

                # Sätter upp tre lokala listor som kommer innehålla hästnamn, vinnarodds
                # och platsodds
                hästnamn_lista = []
                vodds_lista = []
                podds_lista = []

                # Allt innehåll på sidan ligger i en SB_TECH iframe, byter frame till denna
                SB_tech_frame = driver.find_element(
                    By.CSS_SELECTOR, "#main-content > iframe")
                driver.switch_to.frame(SB_tech_frame)

                rubriker = driver.find_elements(
                    By.CLASS_NAME, "rj-carousel-item-market")

                # HÄSTNAMN OCH VINNARODDS
                # Klickar in på "Vinnare" bland rubrikerna
                for obj in rubriker:
                    if obj.text == "Vinnare":
                        obj.click()
                        time.sleep(wait_time)
                        break

                spelformer = driver.find_elements(
                    By.CLASS_NAME, "rj-ev-list__content")

                # Fokuserar på den del av sidan som innehåller vinnaroddsen samt går in och
                # hämtar alla relevanta element (ett per startande häst)
                for spelform in spelformer:
                    if spelform.text[0:7] == "Vinnare":
                        ekipage_lista = spelform.find_elements(
                            By.CLASS_NAME, "rj-ev-list__prelive-outright__button-holder")

                        # Loopar igenom elementen för samtliga ekipage, extraherar hästarnas namn samt vinnarodds och
                        # appendar informationen i korrekt format till namn- och vinnaroddslistorna
                        for ekipage in ekipage_lista:
                            hästnamn_lista.append(ekipage.find_elements(
                                By.CLASS_NAME, "rj-ev-list__bet-btn__content")[0].text)
                            vodds_lista.append(float(ekipage.find_elements(
                                By.CLASS_NAME, "rj-ev-list__bet-btn__content")[1].text.replace(",", ".")))

                rubriker = driver.find_elements(
                    By.CLASS_NAME, "rj-carousel-item-market")

                # PLATSODDS
                # Klickar in på "Placering" bland rubrikerna
                for obj in rubriker:
                    if obj.text == "Placering":
                        obj.click()
                        time.sleep(wait_time)
                        break

                spelformer = driver.find_elements(
                    By.CLASS_NAME, "rj-ev-list__content")

                # Fokuserar på den del av sidan som innehåller platsoddsen samt går in och
                # hämtar alla relevanta element (ett per startande häst)
                for spelform in spelformer:
                    if spelform.text[0:6] == "Topp 3":
                        ekipage_lista = spelform.find_elements(
                            By.CLASS_NAME, "rj-ev-list__prelive-outright__button-holder")

                        # Loopar igenom elementen för samtliga ekipage, extraherar hästarnas platsodds och
                        # appendar informationen i korrekt format till platsoddslistan
                        for ekipage in ekipage_lista:
                            podds_lista.append(float(ekipage.find_elements(
                                By.CLASS_NAME, "rj-ev-list__bet-btn__content")[1].text.replace(",", ".")))

                # Kollar så att datan till loppet faktiskt hämtades, annars exekveras except-blocket
                if len(hästnamn_lista) == 0:
                    raise Exception

                else:
                    # Lägger in all inhämtad information i dataframen
                    for i in range(len(hästnamn_lista)):
                        dummy_df = lopp_df
                        hästnamn = hästnamn_lista[i]
                        vodds = vodds_lista[i]
                        podds = podds_lista[i]
                        ny_rad = pd.DataFrame(
                            [[hästnamn, vodds, podds]], columns=lopp_df.columns)
                        lopp_df = pd.concat(
                            [dummy_df, ny_rad], ignore_index=True)
            except:
                antal_lopp_odds_ej_kunnat_hämtas += 1

            # När allt är färdigt läggs dataframen för loppet till pd_lista
            pd_lista.append(lopp_df)

        driver.quit()

        if antal_lopp_odds_ej_kunnat_hämtas == till_lopp - från_lopp + 1:
            print(
                "Det uppstod ett fel i inhämtningen av oddsen, kontrollera så att de faktiskt ligger uppe")
            return None

        else:
            return pd_lista

        # GÖR KLART H2H
        # GÖR KLART H2H
        # GÖR KLART H2H
        # GÖR KLART H2H

    else:
        # Detta scenario innebär att H2H odds ska scrapeas
        # för dem olika loppen
        print("För närvarande ej kompatibel med H2H, endast V&P fungerar")

        # GÖR KLART H2H
        # GÖR KLART H2H
        # GÖR KLART H2H
        # GÖR KLART H2H


def betsson_scraper(
    länk: str,
    från_lopp: int,
    till_lopp: int,
    wait_time: float = 1,
    initial_wait: float = 2,
) -> list:
    """
    Skrapar hästnamn, vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.

    :param: str länk: Länk till valfritt lopp under tävlingsdagen, t.ex. "https://www.betsson.com/sv/horse-racing/race/details/id/5156676"
                      OBS! VIKTIGT VARA INNE PÅ ETT LOPP, DVS EJ BARA INNE PÅ SIDAN FÖR TÄVLINGSDAGEN
    :param: int från_lopp: Första lopp som ska skrapas
    :param: int till_lopp: Sista lopp som ska skrapas
    :param: float wait_time: Antal sekunder programmet ska vänta efter varje klick/sidinladdning etc, 1 sekund som standard
    :param: float initial_wait_site: Antal sekunder programmet ska vänta efter att get(betsson...) callats för att sidan ska hinna laddas in ordentligt
            2 sekunder som standard

    :rtype: list of pd.DataFrames: Returnerar en lista av (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Vinnarodds, Platsodds]

    """
    # Initierar sessionen, se till att ha chromedriver i "Program"
    path = "/Applications/chromedriver"
    driver = webdriver.Chrome(path)

    # Går in på tävlingsdagen och väntar {initial_wait} sekunder på att allt ska laddas in
    driver.get(länk)
    time.sleep(initial_wait)

    # Accepterar cookies
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    time.sleep(wait_time)

    # Allt innehåll på sidan ligger i en iframe, byter frame till denna
    iframe = driver.find_element(
        By.CSS_SELECTOR, "body > obg-app-root > div > obg-m-core-layout > div > ng-scrollbar > div > div > div > div > div > obg-horse-racing-lobby-container > div > obg-iframe > iframe")
    driver.switch_to.frame(iframe)

    # Lista som kommer spara dataframes för samtliga lopp
    pd_lista = []

    for loppnr in range(från_lopp, till_lopp + 1):
        # Sätter upp en dataframe för loppet
        lopp_df = pd.DataFrame(columns=["Häst", "VOdds", "POdds"])
        time.sleep(wait_time)

        # Uppe till höger finns alla lopp (klickbara), finner dessa element
        loppelement = driver.find_elements(By.CLASS_NAME, "race-number")

        try:
            # Söker igenom loppelementen tills rätt lopp hittats, klickar in på detta lopp
            for lopp in loppelement:
                if lopp.text == str(loppnr):
                    lopp.click()
                    time.sleep(wait_time)
                    break

            # Samlar in samtliga startande ekipage
            samtliga_startande = driver.find_elements(By.CLASS_NAME, "runner")

            for ekipage in samtliga_startande:
                hästnamn = ekipage.find_element(By.CLASS_NAME, "name").text
                vodds_str = ekipage.find_element(
                    By.CLASS_NAME, "odds.fixed.win").text
                podds_str = ekipage.find_element(
                    By.CLASS_NAME, "odds.fixed.place").text

                # Om häst är STRUKEN sätts vinnarodds och platsodds till 999
                if vodds_str == "STR":
                    vodds = 999
                    podds = 999
                else:
                    vodds = float(vodds_str)
                    podds = float(podds_str)

                # Lägger denna data till dataframen för loppet
                dummy_df = lopp_df
                ny_rad = pd.DataFrame(
                    [[hästnamn, vodds, podds]], columns=lopp_df.columns)
                lopp_df = pd.concat([dummy_df, ny_rad], ignore_index=True)

        except:
            print(
                f"Ett problem uppstod i inhämtningen av hästnamn och odds för lopp {loppnr}, kontrollera så att odds faktiskt ligger uppe för loppet")
            pass

        # När loppet är färdigt läggs dataframen för loppet till pd_lista
        pd_lista.append(lopp_df)

    driver.quit()

    return pd_lista


def unibet_scraper(
    bana: str,
    från_lopp: int,
    till_lopp: int,
    land: str = "Sverige",
    wait_time: float = 0.5,
) -> list:
    """
    Skrapar hästnamn, vinnarodds och platsodds till en valfri uppsättning lopp från en tävlingsdag.

    :param: str bana: Bana, t.ex. "jagersro"
    :param: från_lopp: Första lopp som ska skrapas
    :param: till_lopp: Sista lopp som ska skrapas
    :param: str land: Land, "Sverige" som standard
    :param: float wait_time: Antal sekunder programmet ska vänta efter varje klick/sidinladdning etc, 0.5 sekund som standard

    :rtype: list of pd.DataFrames: Returnerar en lista av (antal hästar x 3) dataframes (en för varje lopp) med kolumner
            [Hästnamn, Vinnarodds, Platsodds]
    """

    # Initierar sessionen, se till att ha chromedriver i "Program"
    path = "/Applications/chromedriver"
    driver = webdriver.Chrome(path)

    # Lista som längre fram kommer spara samtliga lopp
    pd_lista = []

    # Går in på Unibets travavdelning
    driver.get(
        "https://www.unibet.se/betting/sports/filter/trotting/all/allGroups")

    time.sleep(wait_time)

    # Accepterar cookies
    driver.find_element(
        By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()

    # Ibland ligger tävlingarna för relevant bana tillgängliga, ibland krävs
    # ett klick på rätt land först. Ifall det är klickbart kommer try-blocket lyckas,
    # annars exekveras istället except-blocket vilket då innehåller det extra klicket.
    try:
        tävlingsbanor = driver.find_elements(By.CLASS_NAME, "_48455")

        for tävlingsbana in tävlingsbanor:
            if tävlingsbana.text == bana:
                tävlingsbana.click()
                break
            if tävlingsbana.text != bana and tävlingsbana == tävlingsbanor[-1]:
                raise Exception

    except:
        länder = driver.find_elements(By.CLASS_NAME, "_677af")
        for obj in länder:
            if obj.text == land:
                obj.click()
                break

        time.sleep(wait_time)

        tävlingsbanor = driver.find_elements(By.CLASS_NAME, "_48455")

        for tävlingsbana in tävlingsbanor:
            if tävlingsbana.text == bana:
                tävlingsbana.click()
                break

    # Av någon anledning krävs lite extra tid för detta steg
    time.sleep(wait_time + 0.5)

    # Letar upp första "Se hela spelutbudet" för banan och klickar in så att hela
    # tävlingsdagen öppnas
    try:
        driver.find_element(By.CLASS_NAME, "_2a5f5").click()
    except:
        driver.quit()
        return None

    time.sleep(wait_time)

    for loppnr in range(från_lopp, till_lopp + 1):
        # Sätter upp en dataframe för loppet
        lopp_df = pd.DataFrame(columns=["Häst", "VOdds", "POdds"])

        # Går in till loppet
        driver.find_element(By.CLASS_NAME, "_95a36").click()

        alla_lopp = driver.find_elements(By.CLASS_NAME, "_9c8c3")
        for lopp in alla_lopp:
            if loppnr < 10:
                if int(lopp.text[-1]) == loppnr:
                    lopp.click()
                    time.sleep(wait_time)
                    break
            else:
                if int(lopp.text[-2:]) == loppnr:
                    lopp.click()
                    time.sleep(wait_time)
                    break

        done = False
        while not done:
            try:
                # Hämtar in tre kolumner från Unibet, en för hästnamn, en för vinnarodds
                # samt en för platsodds
                objekt = driver.find_elements(
                    By.CLASS_NAME, "KambiBC-outcomes-list__column")
                hästnamn_obj = objekt[0]
                vodds_obj = objekt[1]
                podds_obj = objekt[2]

                # Sparar ner alla startande hästar i en lista, rensar bort strukna hästar
                hästnamn_lista = [element.text for element in hästnamn_obj.find_elements(
                    By.CLASS_NAME, "KambiBC-outcomes-list__label")[1:]]
                strukna = [element.text for element in hästnamn_obj.find_elements(
                    By.CLASS_NAME, "KambiBC-outcomes-list__label.KambiBC-outcomes-list__label--scratched")]

                # Gör samma sak för vinnarodds samt platsodds. Då raderna är tomma ifall ekipage är struket
                # behövs ingen information rensas i detta fall
                vodds_lista = [float(element.text) for element in vodds_obj.find_elements(
                    By.CLASS_NAME, "Button__StyledButton-sc-lvu29a-0")]
                podds_lista = [float(element.text) for element in podds_obj.find_elements(
                    By.CLASS_NAME, "Button__StyledButton-sc-lvu29a-0")]
                done = True

            except:
                pass

        # Rensar hästnamn_lista så att endast startande ekipage i rätt ordning återstår
        for häst in hästnamn_lista:
            if häst == "2160v" or häst == "2180v" or häst == "2200v" or häst == "2220v" or häst == "1660v" or häst == "1680v" or häst == "1700v" or häst == "3160v" or häst == "3180v" or häst == "3200v" or häst == "2640v" or häst == "2660v" or häst == "2680v":
                hästnamn_lista.remove(häst)
            for struken in strukna:
                if struken == häst:
                    hästnamn_lista.remove(häst)

        # Lägger in all inhämtad information i dataframen
        for i in range(len(hästnamn_lista)):
            dummy_df = lopp_df
            hästnamn = hästnamn_lista[i]
            vodds = vodds_lista[i]
            podds = podds_lista[i]
            ny_rad = pd.DataFrame(
                [[hästnamn, vodds, podds]], columns=lopp_df.columns)
            lopp_df = pd.concat([dummy_df, ny_rad], ignore_index=True)

        # När allt är färdigt läggs dataframen för loppet till pd_lista
        pd_lista.append(lopp_df)

    driver.quit()

    return pd_lista
