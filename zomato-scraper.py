import csv
import json
import requests
import re
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

restaurants = ['warunk-upnormal-tebet', 'warunk-upnormal-cempaka-putih', 'warunk-upnormal-1-beji-depok', 'warunk-upnormal-1-kelapa-gading', 'warunk-upnormal-serpong-utara-tangerang']

def search(api_key, restaurants):
	header = {'Accept': 'application/json', 'user_key': api_key}
	for restaurant in restaurants:
		data = {'q': restaurant}
		r = requests.get('https://developers.zomato.com/api/v2.1/search', headers=header, params=data)
		text = r.json()
		res_id = text['restaurants'][0]['restaurant']['id']
		restaurants[restaurant]['id'] = res_id

	return restaurants 

def getReviews(api_key, restaurants):
	header = {'Accept': 'application/json', 'user_key': api_key}
	for restaurant in restaurants:
		res_id = restaurants[restaurant]['id']
		data = {'res_id': res_id, 'start': 0, 'count': 20}
		r = requests.get('https://developers.zomato.com/api/v2.1/reviews', headers=header, params=data)
		text = r.json()
		f = csv.writer(open(restaurant+'.csv','wb+'), delimiter=';',quotechar='|', quoting=csv.QUOTE_MINIMAL)
		f.writerow(['name', 'review', 'rating'])
		for review in text['user_reviews']:
			f.writerow([review['review']['user']['name'].encode('utf-8'), review['review']['review_text'].encode('utf-8'), review['review']['rating']])
			
def run(restaurant):
	driver = webdriver.Chrome('C:/Users/Norma/Documents/chromedriver/chromedriver.exe')
	driver.get("https://www.zomato.com/jakarta/" + restaurant +"/reviews")
	try:
		tab_all_reviews = driver.find_element_by_xpath('//*[@id="selectors"]/a[@data-sort="reviews-dd"]')
		driver.execute_script("arguments[0].scrollIntoView(true);", tab_all_reviews)
		tab_all_reviews.click()
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='selectors']/a[2] and contains(@class,'selected')")))
	except (NoSuchElementException, TimeoutException):
		print("Selector all reviews not found")

	while (True):
		try:
			load_more = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "res-page-load-more")));
			driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
			load_more = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "res-page-load-more")));
			driver.execute_script('arguments[0].setAttribute("data-limit", 20)', load_more)
			load_more.click()
		except (NoSuchElementException, TimeoutException):
			print "There is no button load more"
			break

	reviews = driver.find_elements_by_class_name('rev-text')
	reviews_expand = driver.find_elements_by_css_selector("div.rev-text.mbot0.hidden");
	ratings = driver.find_elements_by_class_name('zdhl2')
	f = open(restaurant + '.txt','wb+')
	count = 0
	count_expand = 0
	for review in reviews:
		rating = ratings[count].get_attribute('outerHTML')
		attrs = rating.split()
		for attr in attrs:
			if "." in attr:
				label = attr[:3]
				review = review.text
				if (review == ''):
					driver.execute_script('arguments[0].setAttribute("style", "display: block;")', reviews_expand[count_expand])
					review = reviews_expand[count_expand].text
					count_expand+=1
					count+=1
				review = re.sub('RATED', '', review)
				review = re.sub('\t', '', review)
				review = re.sub('\n', ' ', review)
				review = re.sub('^\s*', '', review)
				f.write(label + "<>")
				f.write(review.encode('utf-8') + "\n")
		count+=1
	f.close()

if __name__ == "__main__":
	# restaurants = search(api_key, restaurants)
	restaurant = sys.argv[1]
	run(restaurant)