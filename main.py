import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from collections import defaultdict

url = 'https://www.flashscore.com/football/england/premier-league-2023-2024/results/'

class FScraper:
    def __init__(self):
        self.browser = None
        self.page = None

    async def click_through(self):
        for _ in range(3):
            element = await self.page.query_selector('#live-table > div.event.event--results > div > div > a')
            if element:
                await element.click()
                await asyncio.sleep(1)
            else:
                print("Element not found for clicking.")

    async def get_scores(self):
        async with async_playwright() as p:

            self.browser = await p.chromium.launch(headless=True)  # headless=False for debugging
            self.page = await self.browser.new_page()

            await self.page.goto(url, timeout=90000)

            await self.click_through()

            await self.page.wait_for_selector("div.event__match")

            # Debug: page content
            # print(await page.content())

            times = await self.page.locator("div.event__time").all_text_contents()
            home_teams = await self.page.locator("div.event__homeParticipant").all_text_contents()
            score_home = await self.page.locator("span.event__score--home").all_text_contents()
            score_away = await self.page.locator("span.event__score--away").all_text_contents()
            away_teams = await self.page.locator("div.event__awayParticipant").all_text_contents()

            # Ensure all length is the same
            max_len = max(len(times), len(home_teams), len(score_home), len(score_away), len(away_teams))

            # Ensure equal length
            def pad_list(lst, length, filler="N/A"):
                return lst + [filler] * (length - len(lst))

            times = pad_list(times, max_len)
            home_teams = pad_list(home_teams, max_len)
            score_home = pad_list(score_home, max_len)
            score_away = pad_list(score_away, max_len)
            away_teams = pad_list(away_teams, max_len)

            # Structured data
            dict_res = defaultdict(list)
            for ind in range(max_len):
                dict_res['times'].append(times[ind])
                dict_res['home_teams'].append(home_teams[ind])
                dict_res['score_home'].append(score_home[ind])
                dict_res['score_away'].append(score_away[ind])
                dict_res['away_teams'].append(away_teams[ind])

            df_res = pd.DataFrame(dict_res)

            print(df_res.head())
            df_res.to_csv('flashscore_results.csv', index=False)

            await self.browser.close()

if __name__ == '__main__':
    scraper = FScraper()
    asyncio.run(scraper.get_scores())
