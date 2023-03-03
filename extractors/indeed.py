from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from bs4 import BeautifulSoup

def get_page_count(keyword):
  driver = webdriver.Chrome(service= Service("./chromedriver"))
  base_url = "https://www.indeed.com/jobs?q="
  driver.get(f"{base_url}{keyword}")
  
  soup = BeautifulSoup(driver.page_source, "html.parser")
  pagination = soup.find("nav", attrs={"aria-label": "pagination"})
  # 검색결과pagination없을때 에러 발생 -> 스크래핑할 페이지가 하나밖에 없음 - return 1 
  if pagination == None:
    return 1
  pages = pagination.find_all("div", class_="ecydgvn1")
  count = len(pages)
  # 검색결과가 5페이지 이상일 경우 5페이지에서 중단(계속 서칭하는 방법 있겠지만 이 예제에서는 5까지만), 5페이지 보다 적으면 해당 페이지 숫자 return
  if count >= 5:
    return 5
  else: 
    return count


def extract_indeed_jobs(keyword):
  try:
    # pages = get_page_count에서 받은 페이지 숫자
    pages = get_page_count(keyword)
    print("Found", pages, "pages")
    results = []
    # pages 숫자가 5라면 다섯번 실행됨(page: 0, 1, 2, 3, 4 - 순서대로)
    for page in range(pages):
      driver = webdriver.Chrome(service= Service("./chromedriver"))
      base_url = "https://www.indeed.com/jobs"
      # ex) 2페이지 url: {키워드}&start=10 / 3페이지 url: {키워드}&start=20
      final_url = f"{base_url}?q={keyword}&satrt={page*10}"
      print("Requesing", final_url)    
      driver.get(final_url)

      soup = BeautifulSoup(driver.page_source, "html.parser")
      jobs_list = soup.find("ul", class_="jobsearch-ResultsList")
      # recursive=False - 타켓으로 정한 ul의 li만 가져옴(li안에 속한 다른 ul,li는 무시), 기본적으로 find_all은 recursive=True임
      jobs = jobs_list.find_all('li', recursive=False)
      for job in jobs:
        # li 중에 job 정보가 없는 li(class="mosaic-zone이 있어서 job 내용이 있는 li만 골라내줌")
        zone = job.find("div", class_="mosaic-zone")
        if zone == None:
          # h2안에 있는 a만 select
          anchor = job.select("h2 a")
          title = anchor[0]['aria-label']
          link = anchor[0]['href']
          company = job.find("span", class_="companyName")
          location = job.find("div", class_="companyLocation")
          job_data = {
            'link': f"http://indeed.com{link}",
            'company': company.string,
            'location': location.string,
            'position': title 
          }
          for _ in job_data:
            if job_data[_] != None:
              job_data[_] = job_data[_].replace(",", " ")
              
          results.append(job_data)
      # for result in results:
      #   print(result, "\n//////\n")
    return results
  finally:
    driver.quit()

