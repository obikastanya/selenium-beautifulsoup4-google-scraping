import re
import json
from threading import Thread
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


globalData=[]

class Crawler():
    def __init__(self):
        self.soup=None
        
    def getDoc(self,page):
        self.soup=BeautifulSoup(page, 'lxml')
        xPage=self.soup.select('div.cXedhc')
        data={}
        listData=[]
        for p in xPage:
            person=self.getPerson(p)    
            det=p.select('span.rllt__details.lqhpac')
            reviews=self.getReviews(det)
            addrss,distance=self.getAddrss(det)
            data={
                'person':person,
                'review':reviews,
                'address':addrss,
                'distance':distance
            }
            listData.append(data)    
        globalData.extend(listData)
            
    def getPerson(self, el):
        result=''
        person=el.select('div.dbg0pd div')
        adtText=person[0].select('wbr')
        if len(adtText)>0:
            person[0].wbr.unwrap()
            result=person[0].text
        return result

    def getReviews(self, el):
        result=''
        rev=el[0].select('div:nth-child(1)')
        isRevExist=el[0].select('g-review-stars span')
        if len(isRevExist)>0: 
            result=isRevExist[0]['aria-label'].replace(',','')
        else:
            result=rev[0].text
            result=result.split(' · ')[0]
        return result
    
    def getAddrss(self, el):
        newAdrs=''
        distance=''
        addrs=el[0].findAll(text=re.compile('km'))
        tempAdrs=[]
        if len(addrs)>0:
            tempAdrs=addrs[0].split(' · ')
            if len(tempAdrs)>1:
                newAdrs=tempAdrs[1].replace(',','')
            distance=tempAdrs[0]
        return newAdrs,distance


class Browser():
    def __init__(self):
        self.option=webdriver.ChromeOptions()
        self.option.add_experimental_option('detach',True)
        #Fix Selenium Problem, Auto close selenium by adding detach option.
        self.driver=webdriver.Chrome(r'C:\data\selenium\chromedriver.exe', chrome_options=self.option)
        

    def getInit(self,link):
        self.driver.get(link)
        WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'MXl0lf')))
            

    def clickMore(self):
        # find and click view more
        el=self.driver.find_element_by_css_selector('.MXl0lf.mtqGb')
        el.click()
        # find pagination and open new tab
        WebDriverWait(self.driver,30).until(EC.presence_of_element_located((By.CLASS_NAME,'cXedhc')))
        next=self.driver.find_elements_by_xpath("//a[@class='fl']")
        for i in next:
            i.send_keys(Keys.CONTROL+Keys.ENTER);

    def getListPage(self):
        listPage=[]
        for i in range(len(self.driver.window_handles)-1,0, -1):
            self.driver.switch_to.window(self.driver.window_handles[i])
            listPage.append(self.driver.page_source)
        return listPage

    def execute(self, link):
        self.getInit(link)
        self.clickMore()
        listPage=self.getListPage()
        return listPage

class Writter():
    def writeJson(self, listJson):
        jsonString=json.dumps(listJson)
        jsonFile=open('result.json','w')
        jsonFile.write(jsonString)
        jsonFile.close()




if __name__=='__main__':
    link="https://www.google.com/search?q=dokter"
    page=Browser().execute(link)
    c=Crawler()
    threads=[]
    
    # put thread inside list
    for p in page:
        t=Thread(target=c.getDoc, args=(p,))
        threads.append(t)
    
    # start thread
    for t in threads:
        t.start()

    # wait for all thread to finish
    for t in threads:
        t.join()

    Writter().writeJson(globalData)
    

# flow program
# Search doctor -> view more at doctor list -> open new page in new tab -> parse html -> create multi threading-> parse data -> write json. 