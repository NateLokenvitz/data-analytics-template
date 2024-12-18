#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import time


def parse_runtime(runtime_str):
    """
    Converts IMDb's runtime format to minutes.
    """
    if not runtime_str:
        return None
    import re
    hours = re.search(r'(\d+)h', runtime_str)
    minutes = re.search(r'(\d+)min', runtime_str)
    total_minutes = 0
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if minutes:
        total_minutes += int(minutes.group(1))
    return total_minutes


def scrape_imdb_top_100(base_url):
    """
    Scrapes IMDb "Top 100 Movies" from the specified webpage.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    all_movies = []

    try:
        for page_start in [1, 51]:  # Adjust this for more pages if needed
            url = f"{base_url}&start={page_start}&ref_=adv_nxt"
            print(f"Scraping page: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            movie_items = soup.select('.lister-item-content')

            for movie in movie_items:
                try:
                    title_tag = movie.select_one('.lister-item-header a')
                    title = title_tag.text.strip() if title_tag else None
                    link = f"https://www.imdb.com{title_tag['href']}" if title_tag else None

                    year_tag = movie.select_one('.lister-item-year')
                    year = year_tag.text.strip("()") if year_tag else None

                    runtime_tag = movie.select_one('.runtime')
                    runtime = parse_runtime(runtime_tag.text.strip()) if runtime_tag else None

                    rating_tag = movie.select_one('.ratings-bar strong')
                    rating = float(rating_tag.text.strip()) if rating_tag else None

                    metascore_tag = movie.select_one('.metascore')
                    metascore = int(metascore_tag.text.strip()) if metascore_tag else None

                    content_rating_tag = movie.select_one('.certificate')
                    content_rating = content_rating_tag.text.strip() if content_rating_tag else None

                    all_movies.append({
                        'Title': title,
                        'Year': year,
                        'Runtime (mins)': runtime,
                        'Content Rating': content_rating,
                        'Rating (out of 10)': rating,
                        'Metascore (out of 100)': metascore,
                        'URL': link
                    })
                except Exception as e:
                    print(f"Error parsing a movie entry: {e}")

            time.sleep(2)  # Avoid overwhelming the server

        print("Scraping complete.")
        return pd.DataFrame(all_movies)

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


# Main script
if __name__ == "__main__":
    base_url = "https://www.imdb.com/search/title/?groups=top_100&sort=user_rating,desc"

    print("Scraping IMDb Top 100 Movies...")
    movies_df = scrape_imdb_top_100(base_url)

    if movies_df is not None:
        print("\nFirst few movies:")
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(movies_df.head())
        print(f"\nTotal movies scraped: {len(movies_df)}")

        # Save to CSV
        csv_filename = 'IMDb_Top_100_Movies.csv'
        movies_df.to_csv(csv_filename, index=False)
        print(f"Data saved to {csv_filename}")         

