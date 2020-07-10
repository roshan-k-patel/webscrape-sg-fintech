import time
from selenium import webdriver
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen, Request

links = []

# iterates through each page and gets the directory link for each company
def get_container_links(containers,browser,no_pages):
    page = 1

    while page <= no_pages:

        print("Getting links for page: " + str(page))

        for container in containers:
            link = container.find('a')['href']
            links.append(link)

        # presses next page button
        try:
            next_page_buttons = browser.find_elements_by_class_name("sabai-btn.sabai-btn-default.sabai-btn-sm")
            next = next_page_buttons[len(next_page_buttons)-1]

            print("Scraped page: " + str(page) + ' / ' + str(no_pages))

            next.click()
        except:
            pass

        time.sleep(5)

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
        tags_list = tags_block.findAll("a")
        addresses_block = page_soup.find("div", {"class": "sabai-directory-contact"})
        addresses_list = addresses_block.findAll("a")
        description = '' + page_soup.find("p").text
        description = description.replace(',','')

        # detail extraction
        title = details_block.select("h1.fl-post-title")[0].text
        fintech_certified = fin_cert_block.select("div.sabai-field-value")[0].text
        uen = uen_block.select("div.sabai-field-value")[0].text
        tags = ''
        emails = ''
        websites = ''
        description = description.lower().capitalize()

        # data manipulation for csv
        for tag in tags_list:
            tags = tags + ' -'+ tag.text

        tags = tags[3:]

        for address in addresses_list:
            if address.text.__contains__('@'):
                emails = emails + ' -' + address.text
            else:
                websites = websites + ' -' + address.text

        emails = emails[2:]
        websites = websites[2:]

        return (title,tags,uen,fintech_certified,emails,websites,description)


def main():
    # creates a file and writes the headings
    filename = "sg_fintech.csv"
    f = open(filename, "w")
    headers = "Company Name, Tags, UEN, Fintech Certified, Email, Website, Description\n"

    f.write(headers)

    # main directory page, starts scraping for links here page by page using selenium
    address = "https://directory.singaporefintech.org/"
    browser = webdriver.Chrome()
    browser.get(address)
    time.sleep(5)

    html = browser.page_source
    page_soup = soup(html, 'html.parser')
    containers = page_soup.findAll("div", {"class": "sabai-col-xs-9 sabai-directory-main"})

    # gets all container links from each page
    get_container_links(containers,browser,59)

    browser.quit()

    get_container_details(links[0])

    # gets all details and writes them to the csv
    for iteration, link in enumerate(links):
        deets = get_container_details(link)
        csv_string = deets[0] + "," + deets[1] + "," + deets[2] + "," + deets[3] + "," + deets[4] + "," + deets[5] + "," + deets[6]
        f.write(csv_string + "\n")

        print(str(iteration+1) + " / " + str(len(links)))
        print(csv_string)

    f.close()


if __name__ == '__main__':
    main()
