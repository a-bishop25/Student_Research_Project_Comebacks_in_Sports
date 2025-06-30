from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

def create_driver():
    print("🚀 Creating new Selenium driver instance...")
    options = Options()
    options.add_argument("--headless")  # Optional: uncomment for headless scraping
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    try:
        driver = webdriver.Chrome(service=Service(), options=options)
        driver.set_page_load_timeout(30)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)
        print("✅ Driver successfully created.")
        return driver
    except Exception as e:
        print(f"❌ Failed to create driver: {e}")
        raise

def get_team_season_totals(url, max_retries=3):
    for attempt in range(1, max_retries + 1):
        print(f"\n🔍 Fetching URL: {url} (Attempt {attempt})")
        driver = None
        try:
            driver = create_driver()

            print("🌐 Opening the page...")
            driver.get(url)
            print("⏳ Waiting for batting table to appear...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "players_standard_batting"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            print("📋 Available tables on page:")
            found_tables = soup.find_all("table")
            if not found_tables:
                print("⚠️ No tables found at all on this page!")
            for table in found_tables:
                print(f" - {table.get('id')}")

            print("🔎 Looking for batting table...")
            table = soup.find('table', {'id': 'players_standard_batting'})
            if not table:
                print(f"❌ Batting table not found in {url}")
                return {"error": "Batting table not found"}

            print("🔎 Looking for <tfoot>...")
            tfoot = table.find('tfoot')
            if not tfoot:
                print(f"❌ No <tfoot> found in batting table at {url}")
                return {"error": "No tfoot in batting table"}

            print("🔎 Looking for totals row...")
            totals_row = tfoot.find('tr')
            if not totals_row:
                print(f"❌ No totals row found in <tfoot> at {url}")
                return {"error": "No totals row in tfoot"}

            print("✅ Found totals row. Extracting stats...")

            data = {}
            for td in totals_row.find_all('td'):
                stat_name = td.get('data-stat')
                value = td.text.strip()
                print(f"   - {stat_name}: {value}")
                if not stat_name:
                    continue
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                data[stat_name] = value

            return data

        except TimeoutException:
            print(f"⏰ Timeout while loading {url} on attempt {attempt}")
            if attempt == max_retries:
                return {"error": "Timeout loading page after retries"}
            else:
                print("🔁 Retrying after delay...")
                time.sleep(5)

        except WebDriverException as we:
            print(f"🧨 WebDriver exception occurred: {we}")
            if attempt == max_retries:
                return {"error": str(we)}
            else:
                print("🔁 Retrying after delay...")
                time.sleep(5)

        except Exception as e:
            print(f"❌ General exception on attempt {attempt}: {e}")
            if attempt == max_retries:
                return {"error": str(e)}
            else:
                print("🔁 Retrying after delay...")
                time.sleep(5)

        finally:
            if driver:
                print("🧹 Quitting driver...")
                driver.quit()

# Read team URLs from file
with open("../Text Files/SHORT_team_urls.txt", "r") as f:
    team_urls = [line.strip() for line in f if line.strip()]

output_path = "../Text Files/SHORT_team_totals.txt"
# Clear/create the output file before starting
with open(output_path, "w") as f:
    pass

# Process each team URL and save results incrementally
for url in team_urls:
    team_id = url.split("/")[-2]            # e.g., "LAA"
    year = url.split("/")[-1].split(".")[0] # e.g., "2025"
    key = f"{team_id} {year}"

    print(f"\n📦 Processing {key}")
    totals = get_team_season_totals(url)

    with open(output_path, "a") as f:  # append mode
        f.write(f"{key} Totals:\n")
        if "error" in totals:
            f.write(f"  ERROR: {totals['error']}\n")
        else:
            for stat, value in totals.items():
                f.write(f"  {stat}: {value}\n")
        f.write("\n")

    print(f"💾 {key} totals saved (or error recorded).")

print(f"\n✅ All results saved incrementally to '{output_path}'")
