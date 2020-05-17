# DiceUp [[View Live]](https://zyv1k.eu.pythonanywhere.com/diceup)
Django app that recreates provided picture using images of 6 sided dice.

* Programming language: Python 3
* Web framework: Django
* Image processing: Pillow library for python
* Front-end: bootstrap 4

original:
![org](https://github.com/Zyvik/DiceUp---JavaScript/blob/master/Eevee.jpg)

result:
![result](https://github.com/Zyvik/DiceUp---JavaScript/blob/master/wynik.png)

## Features:
* Recreates uploaded picture using images of 6 sided dice
* Creates simple .txt instruction (for people mad enough to actually try creating this)
* Maximum size of user's image is set to 1MB
* Maximum dimensions of provided image is set to 1920x1080


## Installation:
### Requirements (requirements.txt included):
* Python 3.7+
* Django 3.0.5+
* Pillow 5.3.0

1. Clone repository
2. Navigate to folder containing *manage.py* in your console
2. Run `pip install requirements.txt` if your environment doesn't meet requirements
2. Run `python manage.py migrate`
2. Run `python manage.py runserver`
3. open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser
10. If for some reason you want to deploy it (why?) - change SECRET_KEY in secrets.py (now it contains trash)
