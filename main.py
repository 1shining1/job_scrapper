from flask import Flask, render_template, request, redirect, send_file
from extractors.indeed import extract_indeed_jobs
from extractors.wwr import extract_wwr_jobs
from file import save_to_file

app = Flask("JobScrapper")

@app.route("/")
def home():
  return render_template('home.html', name="Sal")

db ={}

@app.route("/search")
def search():
  keyword = request.args.get("keyword")
  if keyword == None:
    return redirect("/")
  # 페이지 리로드 할때마다 job을 다시 찾는것을 방지(느림..) 하기 위해서 fake 데이터베이스 만들어서 검색결과가 db안에 없을 경우만 새로 extract함
  if keyword in db:
    jobs = db[keyword]
  else:
    indeed = extract_indeed_jobs(keyword)
    wwr = extract_wwr_jobs(keyword)
    jobs = indeed + wwr
    db[keyword] = jobs
  return render_template("search.html", keyword=keyword, jobs=jobs)

@app.route("/export")
def export():
  # user가 keyword없이 export로 이동하면 redirect
  keyword = request.args.get("keyword")
  if keyword == None:
    return redirect("/")
  # user가 db에 없는 keyword로 이동하려고 하면 user가 찾고 있는 keyword와 함께 search 페이지로 user를 보내줌
  if keyword not in db:
    return redirect(f"/search?keyword={keyword}")
  # file_name이랑 jobs로 파일 생성, file.py 에서 funciton import - save_to_file(파일이름, jobs)
  save_to_file(keyword, db[keyword])
  # send_file(flask에서 import)에서 첫번째 argument - 파일이름 / 다운로드가 실행되도록 as_attachment=True)
  return send_file(f"{keyword}.csv", as_attachment=True)

app.run("0.0.0.0")
