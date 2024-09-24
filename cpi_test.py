import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Initialize the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Define the list of cities and time frames
cities = [
    "Ku-area of Tokyo",
    "Osaka-shi",
    "Yokohama-shi",
    "Sapporo-shi",
    "Yamagata-shi",
    "Tottori-shi",
    "Small cities A",
    "Naha-shi",
]

time_frames = ["Aug. 2024", "Jan. 2024", "2023", "2022", "2021", "2020"]

# Open the webpage
url = "https://www.e-stat.go.jp/en/dbview?sid=0003427113"

# Create a list to store all the data across cities and time frames
all_data = []

for city in cities:
    for time_frame in time_frames:
        driver.get(url)
        time.sleep(8)  # Let the page load fully

        # Select the city dropdown (using XPath for the first dropdown)
        try:
            city_dropdown = driver.find_element(
                By.XPATH, "(//select[@class='js-top_area-matter_items_select'])[1]"
            )
            print("City dropdown found successfully.")
            city_select = Select(city_dropdown)
            city_select.select_by_visible_text(city)
            print(f"City '{city}' selected successfully.")
            time.sleep(5)  # Allow time for the city selection to take effect
        except Exception as e:
            print(f"Failed to locate/select the city dropdown: {e}")
            continue  # Skip to the next iteration if city selection fails

        # Select the time period dropdown (using XPath for the second dropdown)
        try:
            time_dropdown = driver.find_element(
                By.XPATH, "(//select[@class='js-top_area-matter_items_select'])[2]"
            )
            print("Time period dropdown found successfully.")
            time_select = Select(time_dropdown)
            time_select.select_by_visible_text(time_frame)
            print(f"Time period '{time_frame}' selected successfully.")
        except Exception as e:
            print(f"Failed to locate/select the time dropdown: {e}")
            continue  # Skip to the next iteration if time selection fails

        # Click the Apply button
        try:
            apply_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Apply')]"
            )
            apply_button.click()
            print("Apply button clicked successfully.")
        except Exception as e:
            print(f"Failed to click Apply button: {e}")
            continue  # Skip to the next iteration if the apply button fails

        # Wait for the data to load (8 seconds)
        time.sleep(8)

        # Scrape the table data
        try:
            rows = driver.find_elements(
                By.CSS_SELECTOR, "table.stat-dbview-display-table-view tbody tr"
            )
            print(
                f"Found {len(rows)} rows of data for city: {city}, time frame: {time_frame}."
            )
        except Exception as e:
            print(f"Failed to retrieve table data: {e}")
            continue  # Skip to the next iteration if scraping fails

        # Iterate over each row to extract data
        for row in rows:
            category = row.find_element(
                By.TAG_NAME, "th"
            ).text  # Category (e.g., Food, Housing)
            index = row.find_elements(By.TAG_NAME, "td")[0].text  # CPI index value
            change = row.find_elements(By.TAG_NAME, "td")[
                1
            ].text  # Change from previous period

            # Check if the row has a third column (Change over the year)
            if len(row.find_elements(By.TAG_NAME, "td")) > 2:
                change_over_year = row.find_elements(By.TAG_NAME, "td")[
                    2
                ].text  # Change over the year
            else:
                change_over_year = "N/A"  # If no data, mark as "N/A"

            # Append data to the list for this city and time frame
            all_data.append(
                {
                    "City": city,
                    "Time Period": time_frame,
                    "Category": category,
                    "Index": index,
                    "Change (%)": change,
                    "Change Over Year (%)": change_over_year,
                }
            )

# Convert the collected data to a pandas DataFrame
df = pd.DataFrame(all_data)

# Save the DataFrame to a CSV file (append mode)
df.to_csv("japan_cpi_data_multiple.csv", index=False, mode="a")

print("Data scraping complete for all cities and time frames.")
