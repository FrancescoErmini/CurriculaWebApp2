
Setup project
```shell
mkdir curriculaWebApp && cd curriculaWebApp
pip install virtualenv
virtualenv env
source env/bin/activate
git init
git clone https://github.com/FrancescoErmini/CurriculaWebApp2.git
export FLASK_APP=app.py
pip install Flask
pip install -r requirements.txt
```
