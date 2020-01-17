from flask import Flask, render_template,request,redirect,url_for,session
from pymongo import MongoClient
from flask_uploads import UploadSet,IMAGES,configure_uploads
import hashlib, uuid
from datetime import datetime
from bson import ObjectId
app = Flask(__name__)

app.secret_key = "neki obican string"
photos = UploadSet('photos',IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = 'static'
configure_uploads(app,photos)

client = MongoClient("mongodb+srv://admin:admin@cluster0-tepjj.mongodb.net/test?retryWrites=true&w=majority")

db = client.get_database("Projekat")

users = db["Korisnik"]
proizvodi = db["Proizvod"]
transakcije = db["Transakcija"]

@app.route('/')

@app.route('/register', methods = ["POST", "GET"])
def register():
	if request.method == "GET":
		return render_template('register.html')
	username = request.form["username"]
	email = request.form["email"]
	password = request.form["password"].encode('utf-8')
	confirm = request.form["confirm"].encode('utf-8')
	godinaRodjenja = request.form["datum"]
	pol = request.form["pol"]
	ime = request.form["ime"]
	prezime = request.form["prezime"]
	adresa = request.form["adresa"]
	brojTelefona = request.form["broj"]
	datumKreacije = datetime.now().strftime("%Y-%m-%d %H:%M")
	if password != confirm:
		return "Sifre se ne poklapaju!"
	if 'slika' in request.files:
		photos.save(request.files['slika'],'img',request.form['username'] + '.png')
	x = users.find_one({"username":username})
	if x != None:
		return "Korisnik sa tim imenom vec postoji"
	putanja = "/static/img/" + username + ".png"
	hashpass = hashlib.sha256(password).hexdigest()
	tipKorisnika = "Korisnik"
	balans = 0
	k = {
		"username":username,
		"password":hashpass,
		"email":email,
		"picture_url": putanja,
		"godinaRodjenja": godinaRodjenja,
		"pol":pol,
		"datumKreacije": datumKreacije,
		"tipKorisnika": tipKorisnika,
		"balans": balans,
		"ime": ime,
		"prezime": prezime,
		"adresa": adresa,
		"brojTelefona": brojTelefona,
		"korpa":[]
	}
	users.insert_one(k)
	return redirect(url_for('index'))
	

@app.route('/login', methods = ["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template('login.html')
	username = request.form["username"]
	password = request.form["password"].encode('utf-8')
	hashpass = hashlib.sha256(password).hexdigest()
	k = users.find_one({"username":username,"password":hashpass})
	if k == None:
		return "Korisnik sa tim imenom ne postoji ili se sifre ne poklapaju"
		
	session['_id'] = str(k['_id'])
	session ['username'] = username
	return redirect(url_for('user'))


@app.route('/logout', methods = ["POST", "GET"])
def logout():
	session.pop("username",None)
	session["_id"] = None
	session["tipKorisnika"] = None
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	return redirect(url_for('index'))
	

@app.route('/user')
def user():
	lista = users.find()
	if 'username' in session:
		username = session["username"]
		k = users.find_one({"username":username})
		session['tipKorisnika'] = k['tipKorisnika']
		return render_template('user.html',korisnik = k, lista = lista)
	return "Da biste pristupili ovoj stranici morate biti ulogovani."


@app.route('/dodajProizvod', methods = ["GET", "POST"])
def dodajProizvod():
	if session["tipKorisnika"] != "Prodavac" or session["tipKorisnika"] == None:
		return render_template("nisiProdavac.html")
	if request.method == "GET":
		return render_template("dodajProizvod.html")
	naziv = request.form["naziv"]
	cena = request.form["cena"]
	kolicina = request.form["kolicina"]
	tipProizvoda = request.form["tipProizvoda"]
	if 'slika' in request.files:
			photos.save(request.files['slika'], 'img', request.form['naziv'] + '.png')
	
	naziv_slike = request.form["naziv"] + ".png"
	p = {
		'cena':cena,
		"naziv":naziv,
		"kolicina": kolicina,
		"prodavac": str(session['_id']),
		'slika': "/static/img/" + naziv_slike,
		'tipProizvoda':tipProizvoda
		
	}
	proizvodi.insert_one(p)
	return redirect(url_for('index'))

@app.route('/update/<_id>', methods = ["POST", "GET"])
def update(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('update.html', proizvodi = p,_id = _id, x = x)
	naziv = request.form["naziv"]
	cena = request.form["cena"]
	kolicina = request.form["kolicina"]
	
	if 'slika' in request.files:
			photos.save(request.files['slika'], 'img', request.form['naziv'] + '.png')
	naziv_slike = request.form["naziv"] + ".png"
	p = {
		'cena':cena,
		"naziv":naziv,
		"kolicina": kolicina,
		'slika': "/static/img/" + naziv_slike
		
	}
	
	proizvodi.update_one({"_id":x},{'$set':p})
	
	return redirect(url_for('index'))	

@app.route('/updateKR/<_id>', methods = ["POST", "GET"])
def updateKR(_id):
	k = users.find()
	x = ObjectId(_id)
	korisnik = {}
	korisnik['type'] = "test"
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	if request.method == "GET":
		return render_template('update.html', korisnici = k,_id = _id, x = x, korisnik = korisnik)
	password = request.form["password"]
	godinaRodjenja = request.form["datum"]
	tipKorisnika = request.form["tip"]
	balans = request.form["balans"]
	email = request.form["email"]
	username = request.form ["username"]
	
	k = {
		'password':password,
		"godinaRodjenja":godinaRodjenja,
		"tipKorisnika": tipKorisnika,
		"godinaRodjenja": godinaRodjenja,
		"email": email,
		"balans":balans

	}
	users.update_one({"_id":x},{'$set':k})
	return redirect(url_for('index'))

@app.route('/sveGraficke')
def sveGraficke():
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	p = proizvodi.find()
	if request.method == "GET":
		return render_template('sveGraficke.html', proizvodi = p, k = korisnik)
	return render_template('sveGraficke.html')
	
@app.route('/sviProcesori')
def sviProcesori():
	p = proizvodi.find()
	if request.method == "GET":
		return render_template('sviProcesori.html', proizvodi = p)
	return render_template('sviProcesori.html')

@app.route('/sveMaticne')
def sveMaticne():
	p = proizvodi.find()
	if request.method == "GET":
		return render_template('sveMaticne.html', proizvodi = p)
	return render_template('sveMaticne.html')	

@app.route('/sviRacunari')
def sviRacunari():
	p = proizvodi.find()
	if request.method == "GET":
		return render_template('sviRacunari.html', proizvodi = p)
	return render_template('sviRacunari.html')	

@app.route('/grafickeKartice/<_id>')
def grafickeKartice(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('grafickeKartice.html', proizvodi = p, _id = _id, x = x)
	return render_template('grafickeKartice.html')

@app.route('/maticnePloce/<_id>')
def maticnePloce(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('maticnePloce.html', proizvodi = p, _id = _id, x = x)
	return render_template('maticnePloce.html')


@app.route('/procesori/<_id>')
def procesori(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('procesori.html', proizvodi = p, _id = _id, x = x)
	return render_template('procesori.html')
	return render_template('procesori.html')

@app.route('/gotoviRacunari/<_id>')
def gotoviRacunari(_id):
	p = proizvodi.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('gotoviRacunari.html', proizvodi = p, _id = _id, x = x)
	return render_template('gotoviRacunari.html')

@app.route('/korisnici/<_id>')
def korisnici(_id):
	k = users.find()
	x = ObjectId(_id)
	if request.method == "GET":
		return render_template('korisnici.html', korisnici = k, _id = _id, x = x)
	return render_template('korisnici.html')
	return render_template('korisnici.html')

@app.route('/delete/<_id>', methods = ["POST", "GET"])
def delete(_id):
	k = users.find()
	x = ObjectId(_id)
	korisnik = {}
	korisnik['type'] = "test"
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
	if request.method == "GET":
		return render_template('delete.html', korisnici = k,_id = _id, x = x, korisnik = korisnik)
	users.delete_one({"_id":x})
	return redirect(url_for('index'))

@app.route('/index')
def index():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('index.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('index.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())
	return render_template('index.html')

@app.route('/indexProcesori')
def indexProcesori():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('indexProcesori.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('indexProcesori.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())

@app.route('/indexGraficke')
def indexGraficke():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('indexGraficke.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('indexGraficke.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())	

@app.route('/indexMaticne')
def indexMaticne():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('indexMaticne.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('indexMaticne.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())


@app.route('/indexRacunari')
def indexRacunari():
	p = list(proizvodi.find())
	korisnik = {}
	korisnik['type'] = "test"
	
	if '_id' in session:
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		return render_template('indexRacunari.html', proizvodi = p,korisnik = korisnik,korisnici = users.find())
	return render_template('indexRacunari.html',proizvodi=p,korisnik = korisnik,korisnici = users.find())	

@app.route('/kontakt')
def kontakt():
	return render_template('kontakt.html')

@app.route('/oNama')
def oNama():
	return render_template('oNama.html')

@app.route('/dodajUKorpu',methods = ["POST"])
def dodajUKorpu():
	p = proizvodi.find_one({'_id': ObjectId(request.form['prodavac'])})
	korisnik = users.find_one({'_id':ObjectId(session['_id'])})
	korpa = korisnik["korpa"]
	korpa.append(p['_id'])
	users.update_one({'_id':ObjectId(session['_id'])},{"$set":{"korpa":korpa}})
	return redirect(url_for('index'))

@app.route('/brisiIzKorpe',methods = ["POST"])
def brisiIzKorpe():
	korisnik = users.find_one({'_id':ObjectId(session['_id'])})
	korpa = korisnik["korpa"]
	korpa = []
	users.update_one({'_id':ObjectId(session['_id'])},{"$set":{"korpa":korpa}})
	return redirect(url_for('index'))	

@app.route('/korpa')
def korpa():
	if '_id' in session and session['tipKorisnika'] == "Korisnik":
		korisnik = users.find_one({"_id": ObjectId(session["_id"])})
		
		korpa = korisnik['korpa']
		lista_proizvoda = []
		suma = 0
		for x in korpa:
			proizvod = proizvodi.find_one({'_id':ObjectId(x)})
			
			lista_proizvoda.append(proizvod)
		lista_proizvoda = [p for p in lista_proizvoda if p!=None]
		for x in lista_proizvoda:
			suma += int(x['cena'])

		return render_template('korpa.html',korisnik = korisnik,korpa = lista_proizvoda,total = suma)

@app.route('/izvrsiKupovinu',methods = ["POST"])
def izvrsiKupovinu():
	korisnik = users.find_one({"_id":ObjectId(session["_id"])})
	suma = 0
	korisnikBalans = int(korisnik['balans'])
	for x in korisnik["korpa"]:
		proizvod = proizvodi.find_one({'_id':ObjectId(x)})
		
		suma += int(proizvod['cena'])
	if korisnikBalans >= suma:
		balans = korisnikBalans - suma
		
		transakcija = {
			'kupac_id':str(session['_id']),
			'proizvodi':korisnik['korpa'],
			'vremeKupovine':datetime.now().strftime("%Y-%m-%d %H:%M")
		}
		transakcije.insert_one(transakcija)
		users.update_one({"_id": ObjectId(session['_id'])},{"$set":{'balans':balans,'korpa':[]}})

		return "Kupovina je uspešno izvršena"
	return "Nemate dovoljno sredstava na računu"


if __name__ == '__main__':
	app.run(debug=True)