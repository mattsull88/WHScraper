from send_telegram_message import *
from extract_html import *
from time import sleep
from random import randint

sleep(randint(1,200))

# Fixed Variables
today = date.today().strftime("%d/%m/%Y")


# Games Workshop
games_workshop_urls = ['https://www.warhammer.com/en-AU/shop/warhammer-40000/xenos-armies/aeldari']
games_workshop_database = "database.db"

try:
    games_workshop_data = scrape_website(games_workshop_urls, games_workshop_database,
                                      "Stock", "Name", "URL", extract_gamesworkshop_data, True)

    if not send_update_message(games_workshop_data, games_workshop_database, "Stock", "Name", "URL", "New Aeldari",
                           "https://www.warhammer.com"):
        print("No stock changes found")
except:
    send_telegram("Games Workshop Script broken")

# Gap Games
gap_games_urls = ["https://www.gapgames.com.au/collections/craftworlds?page=" + str(page) for page in range(1, 6)]
gap_games_database = "database2.db"
gap_games_item_avail_key = 'available'
gap_games_item_name_key = 'title'
gap_games_item_url_key = 'handle'

try:
    gap_games_data = scrape_website(gap_games_urls, gap_games_database, gap_games_item_avail_key,
                                gap_games_item_name_key, gap_games_item_url_key, extract_gapgames_data, False)

    if not send_update_message(gap_games_data, gap_games_database, gap_games_item_avail_key,
                           gap_games_item_name_key, gap_games_item_url_key, "New Aeldari",
                           "https://www.gapgames.com.au/collections/craftworlds/products/"):
        print("No stock changes found")
except Exception as e:
    send_telegram("Gap Games Scraper broken")
    print(e)

# Combat Company
combat_company_urls = ['https://thecombatcompany.com/collections/aeldari-1?offset=24']
combat_company_database = "database3.db"
combat_company_item_avail_key = 'Stock'
combat_company_item_name_key = 'Name'
combat_company_item_url_key = 'Name'

try:
    combat_company_data = scrape_website(combat_company_urls, combat_company_database, combat_company_item_avail_key,
                                     combat_company_item_name_key, combat_company_item_url_key,
                                     extract_combatcompany_data, False)

    if not send_update_message(combat_company_data, combat_company_database, combat_company_item_avail_key,
                           combat_company_item_name_key, combat_company_item_url_key, "New Aeldari",
                           "https://thecombatcompany.com/collections/aeldari-1/"):
        print("No stock changes found")
except Exception as e:
    send_telegram("Combat Company Scraper broken")
    print(e)