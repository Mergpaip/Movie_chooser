from pandas.core.arrays import integer
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
import tkinter as tk

###########################################################################################################################

root = tk.Tk()
root.title("Movie chooser")

###########################################################################################################################

canvas = tk.Canvas(root, height=690, width=400, bg="#E50914")
canvas.grid(rowspan=15, columnspan=6)

###########################################################################################################################

logo_text = tk.Label(root, text="Movie Chooser", bg="dark red", font = ("Bebas Neue", 30, "bold"), fg="white", relief="raised", borderwidth="10")
logo_text.grid(row=0, column=0, rowspan=2, columnspan=6)

###########################################################################################################################

login_entry = tk.Entry(root, bg="#f0f0f0", borderwidth=5, relief="sunken")
login_entry.grid(row=1, column=0, rowspan=3, columnspan=3)

login_text = tk.Label(root, width=20, text="Login", bg="#E50914", font = ("Bebas Neue", 10, "bold"), fg="white")
login_text.grid(row=1, column=0, rowspan=2, columnspan=3)

password_entry = tk.Entry(root, show="*", bg="#f0f0f0", borderwidth=5, relief="sunken")
password_entry.grid(row=1, column=3, rowspan=3, columnspan=3)

password_text = tk.Label(root, width=20, text="Password", bg="#E50914", font = ("Bebas Neue", 10, "bold"), fg="white")
password_text.grid(row=1, column=3, rowspan=2, columnspan=3)

###########################################################################################################################

movie_results = tk.Label(root, text="Fill in and rate! Loading may take a minute...", bg="dark red", font = ("Bebas Neue", 10, "bold"), fg="white", height=30, width=48)
movie_results.grid(row=4, column=1, rowspan=14, columnspan=4)

###########################################################################################################################
    
def open_selenium():

    global driver

    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome('C:/Users/Sam/AppData/Local/Programs/Python/Python39/Scripts/chromedriver.exe', options=chrome_options)
    driver.set_window_position(-10000,0)

    driver.get("https://www.netflix.com/nl-en/login")
    
    username = driver.find_element_by_id("id_userLoginId")
    password = driver.find_element_by_id("id_password")
    
    netflix_login = login_entry.get()
    netflix_password = password_entry.get()
    
    username.send_keys(netflix_login)
    password.send_keys(netflix_password)
    
    log_in = driver.find_element_by_xpath("//*[@id='appMountPoint']/div/div[3]/div/div/div[1]/form/button")
    log_in.click()
    
    driver.implicitly_wait(5)
    
    select_profile = driver.find_element_by_xpath('//*[@id="appMountPoint"]/div/div/div[1]/div[1]/div[1]/div/div/a')
    select_profile.click()
    
    driver.implicitly_wait(5)
    
    driver.get("https://www.netflix.com/browse/genre/34399")

def send_request_netflix(url):
    #pull raw HTML
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    return(soup)

def parse_netflix():
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # Wait to load page
        time.sleep(1)
    
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    #url from which the HTML needs to be pulled without the page number specified
    url = "https://www.netflix.com/browse/genre/34399"

    #initiate a list of lists with all needed information
    results = []

    #retrieve HTML from URL and transform it into bs4 format
    soup = send_request_netflix(url)

    #search for all cards that have movie information
    sliders = soup.find_all('div', attrs={'class': 'ptrack-container'})
    
    for items in sliders:
        titles = items.find_all('div', attrs={'class': 'fallback-text-container'})

        for title in titles:
            
            #get the needed information from elements within the offer
            title_netflix = title.find('p', attrs={'class': 'fallback-text'}).text
                
            #add the found information to the results
            results.append([title_netflix])

    # return the list of found results as a list of lists
    return results

###########################################################################################################################

def send_request_IMDB(url):
    #pull raw HTML
    r = requests.get(url)

    #convert in to bs4 'soup'
    soup = BeautifulSoup(r.content, 'html.parser')

    return(soup)

def parse_IMDB():
    #url from which the HTML needs to be pulled without the page number specified
    url = "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start=1&ref_=adv_prv"

    #initiate a list of lists with all needed information
    results = []

    #loop over all available pages
    for i in range(0, 10):

        #retrieve HTML from URL and transform it into bs4 format
        soup = send_request_IMDB('https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start='+str(i)+'01&ref_=adv_prv')

        #search for all cards that have house information
        offers = soup.find_all('div', attrs={'class': 'lister-item-content'})

        #loop over all gound houses and extract their information
        for offer in offers:
            
            #get the needed information from elements within the offer
            titles = offer.find('h3', attrs={'class': 'lister-item-header'})
            
            for title in titles:
                title = offer.find('a').text.strip()
                
            score = offer.find('div', attrs={'class': 'inline-block ratings-imdb-rating'}).text.strip()
            
            #add the found information to the results
            results.append([title, score])

    # return the list of found results as a list of lists
    return results

###########################################################################################################################

def create_df(scraped_IMDB, scraped_netflix):
    #create an empty df with columns that represent the retrieved information
    IMDB_df = pd.DataFrame(columns= ['title', 'score'], data=scraped_IMDB)
    netflix_df = pd.DataFrame(columns= ['title'], data=scraped_netflix)
    
    total_df = pd.merge(IMDB_df, netflix_df, on=['title'], how='inner')
    df_clean = total_df.drop_duplicates(subset ="title")

    movie_results['text'] = df_clean.to_string(index=False, header=False)

###########################################################################################################################

def rate_movies():

    if __name__ == '__main__':
        
        open_selenium()
        
        scraped_netflix = parse_netflix()
        
        scraped_IMDB = parse_IMDB()
        
        create_df(scraped_IMDB, scraped_netflix)
        
        driver.close()

###########################################################################################################################

button_rate = tk.Button(root, text="Rate movies", relief="raised", borderwidth=5, bg="dark red", font = ("Bebas Neue", 10, "bold"), fg="white", command = lambda:rate_movies())
button_rate.grid(row=2, column=1, rowspan=3, columnspan=4)

###########################################################################################################################

root.mainloop()
