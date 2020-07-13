import time
from selenium import webdriver
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request

links = []

# iterates through each page and gets the directory link for each company
def get_container_links(browser,no_pages):
    page = 1

    while page <= no_pages:

        html = browser.page_source
        page_soup = soup(html, 'html.parser')

        containers = page_soup.findAll("div", {"class": "sabai-col-xs-9 sabai-directory-main"})

        print("Getting links for page: " + str(page))

        for container in containers:
            link = container.find('a')['href']
            links.append(link)

        try:
            next_page_buttons = browser.find_elements_by_class_name("sabai-btn.sabai-btn-default.sabai-btn-sm")
            next = next_page_buttons[len(next_page_buttons)-1]

            print("Scraped page: " + str(page) + ' / ' + str(no_pages))

            next.click()
        except:
            pass

        containers.clear()

        time.sleep(4)

        page = page + 1

# gets the details from each directory link stored in the list
def get_container_details(link):
        req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read()

        # html parsing
        page_soup = soup(webpage, "html.parser")

        # info containers
        details_block = page_soup.find("article", {"class": "fl-post post-6 page type-page status-publish hentry"})
        fin_cert_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-boolean sabai-field-name-field-fintech-certified sabai-clearfix"})
        uen_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-string sabai-field-name-field-uen sabai-clearfix"})
        tags_block = page_soup.find("div", {"class": "sabai-directory-category"})
        try:
            tags_list = tags_block.findAll("a")
        except:
            pass

        try:
            biz_model_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-choice sabai-field-name-field-business-model sabai-clearfix"})
            biz_model = biz_model_block.find("div", {"class": "sabai-field-value"}).text
            biz_model = biz_model.replace(",",";").strip()
        except:
            biz_model = ''

        try:
            staff_count_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-choice sabai-field-name-field-staff-count sabai-clearfix"})
            staff_count = staff_count_block.find("div", {"class": "sabai-field-value"}).text
            staff_count = staff_count.replace("-"," to ").strip()
        except:
            staff_count = ''

        try:
            incorp_date_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-date-timestamp sabai-field-name-field-incorporation-date sabai-clearfix"})
            incorp_date = incorp_date_block.find("div", {"class": "sabai-field-value"}).text
            incorp_date = incorp_date.replace(",",";").strip()
        except:
            incorp_date = ''

        try:
            street_add_block = page_soup.find("div", {"class": "sabai-directory-field sabai-field-type-string sabai-field-name-field-address sabai-clearfix"})
            street_add = street_add_block.find("div", {"class": "sabai-field-value"}).text
            street_add = street_add.replace(",",";").strip()
        except:
            street_add = ''


        addresses_block = page_soup.find("div", {"class": "sabai-directory-contact"})
        addresses_list = addresses_block.findAll("a")
        description = '' + page_soup.find("p").text
        description = description.replace(',',';').replace("\n",'').strip()


        # detail extraction
        title = details_block.select("h1.fl-post-title")[0].text
        title = title.replace(',','').strip()
        try:
            fintech_certified = fin_cert_block.select("div.sabai-field-value")[0].text
        except:
            fintech_certified = ''
        try:
            uen = uen_block.select("div.sabai-field-value")[0].text
        except:
            uen = ''

        tags = ''
        emails = ''
        websites = ''
        description = description.lower().capitalize()

        # data manipulation for csv
        try:
            for tag in tags_list:
                tags = tags + ' -'+ tag.text

            tags = tags[3:]
        except:
            tags = ''

        for address in addresses_list:
            if address.text.__contains__('@'):
                emails = emails + ' -' + address.text
            else:
                websites = websites + ' -' + address.text

        emails = emails[2:]
        websites = websites[2:]


        return (title,tags,uen,fintech_certified,biz_model,staff_count,incorp_date,emails,websites,street_add,description)


def main():
    # creates a file and writes the headings
    filename = "sg_fintech.csv"
    f = open(filename, "w")
    headers = "Company Name, Tags, UEN, Fintech Certified, Biz. Model, No. Staff, Inc. Date, Email, Website, Address, Description\n"

    f.write(headers)

    # main directory page, starts scraping for links here page by page using selenium
    address = "https://directory.singaporefintech.org/"
    browser = webdriver.Chrome()
    browser.get(address)
    time.sleep(5)


    get_container_links(browser,59)
    browser.quit()

    # gets all details and writes them to the csv
    for iteration, link in enumerate(links):
        deets = get_container_details(link)


        if "aggregated by medici" in str(deets):
            pass
        else:
            csv_string = deets[0] + "," + deets[1] + "," + deets[2] + "," + deets[3] + "," + deets[4] + "," + deets[5] +\
                         "," + deets[6] + "," + deets[7] + "," + deets[8] + "," + deets[9] + "," + deets[10]
            f.write(csv_string + "\n")
            print(str(iteration + 1) + " / " + str(len(links)))
            print(csv_string)

    f.close()


if __name__ == '__main__':
    main()
