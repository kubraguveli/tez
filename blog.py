from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,DateField,TimeField,PasswordField,SelectField,RadioField,validators
from passlib.hash import sha256_crypt
from functools import wraps

import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.metrics import mean_squared_error
from sklearn.tree import DecisionTreeClassifier

# Kullanıcı Giriş Decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("girisyap"))
    return decorated_function

app = Flask(__name__)
app.secret_key = "hastane"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWROD"] = ""
app.config["MYSQL_DB"] = "hastane"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

#Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("Ad-Soyad",validators=[validators.Length(min =4, max =30)])
    tcno = StringField("TC No", validators=[validators.Length(11)])
    phone = StringField("Telefon Numarası", validators=[validators.Length( min = 11 , max = 12 )])
    password = PasswordField("Parola", validators=[
        validators.DataRequired(message = "Bir parola belirleyiniz"),
        validators.EqualTo(fieldname = "confirm", message = "Parolanız uyuşmuyor")
    ])
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    tcno = StringField("TC No")
    password = PasswordField("Parola")

class AppointmentForm(Form):
    unit = StringField("Tıbbi Birim", validators=[validators.Length(min =4, max =30)])
    date = DateField("Tarih",)
    time = TimeField('Saat',)
    
class CovidForm(Form):
    cinsiyet = RadioField(choices = ['Erkek', 'Kadın'])
    yas = StringField()
    hamilelik = RadioField(choices = ['Evet', 'Hayır'])
    diyabet = RadioField(choices = ['Evet', 'Hayır'])
    astim = RadioField(choices = ['Evet', 'Hayır'])
    tansiyon = RadioField(choices = ['Evet', 'Hayır'])
    kardiyolojik_rahatsizlik = RadioField(choices = ['Evet', 'Hayır'])
    obezite = RadioField(choices = ['Evet', 'Hayır'])
    cocuk_rahatsizligi = RadioField(choices = ['Evet', 'Hayır'])
    kronik_rahatsizlik = RadioField(choices = ['Evet', 'Hayır'])
    sigara = RadioField(choices = ['Evet', 'Hayır'])
    temas = RadioField(choices = ['Evet', 'Hayır'])

@app.route('/')
def homepage():
    return render_template("homepage.html")

#Kayıt Olma 
@app.route("/kayitol" ,methods = ["GET","POST"])
def kayitol():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        tcno = form.tcno.data
        phone = form.phone.data
        password = sha256_crypt.encrypt(form.password.data)

        cursor = mysql.connection.cursor()
        
        sorgu = "Insert into users(name,tcno,phone,password) values (%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,tcno,phone,password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("girisyap"))
    else:
        return render_template("kayitol.html", form = form)

#Giriş İşlemi
@app.route("/girisyap",methods = ["GET","POST"])
def girisyap():
    form = LoginForm(request.form)
    
    if request.method == "POST":
        tcno = form.tcno.data
        password_entered = form.password.data

        cursor = mysql.connection.cursor()

        sorgu = "Select * From users where tcno = %s"
        result = cursor.execute(sorgu,(tcno,))

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla Giriş Yaptınız...","success")
                session["logged_in"] = True
                session["tcno"] = tcno
                return redirect(url_for("homepage"))
            else:
                flash("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("girisyap")) 

        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("girisyap"))

    return render_template("girisyap.html", form = form)

#Form Bilgi Girişi
@app.route('/form',methods = ["GET","POST"])
def form():
    form = CovidForm(request.form)

    if request.method == 'POST'and form.validate():
        cinsiyet = form.cinsiyet.data
        yas = form.yas.data
        hamilelik = form.hamilelik.data
        diyabet = form.diyabet.data
        astim = form.astim.data
        tansiyon = form.tansiyon.data
        kardiyolojik_rahatsizlik = form.kardiyolojik_rahatsizlik.data
        obezite = form.obezite.data
        cocuk_rahatsizligi = form.cocuk_rahatsizligi.data
        kronik_rahatsizlik = form.kronik_rahatsizlik.data
        sigara = form.sigara.data
        temas = form.temas.data
        cursor = mysql.connection.cursor()

        sorgu = "Insert into covidform(cinsiyet,yas,hamilelik,diyabet,astim,tansiyon,kardiyolojik_rahatsizlik,obezite,cocuk_rahatsizligi,kronik_rahatsizlik,sigara,temas) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sorgu,(cinsiyet,yas,hamilelik,diyabet,astim,tansiyon,kardiyolojik_rahatsizlik,obezite,cocuk_rahatsizligi,kronik_rahatsizlik,sigara,temas))
        mysql.connection.commit()

        if cinsiyet == 'Kadın':
            cinsiyet = 1
        else:
            cinsiyet = 2
        
        if hamilelik == 'Evet':
            hamilelik = 1
        else:
            hamilelik = 2

        if diyabet == 'Evet':
            diyabet = 1
        else:
            diyabet = 2

        if astim == 'Evet':
            astim = 1
        else:
            astim = 2

        if tansiyon == 'Evet':
            tansiyon = 1
        else:
            tansiyon = 2

        if kardiyolojik_rahatsizlik == 'Evet':
            kardiyolojik_rahatsizlik = 1
        else:
            kardiyolojik_rahatsizlik = 2

        if obezite == 'Evet':
            obezite = 1
        else:
            obezite = 2

        if cocuk_rahatsizligi == 'Evet':
            cocuk_rahatsizligi = 1
        else:
            cocuk_rahatsizligi = 2

        if kronik_rahatsizlik == 'Evet':
            kronik_rahatsizlik = 1
        else:
            kronik_rahatsizlik = 2

        if sigara == 'Evet':
            sigara = 1
        else:
            sigara = 2

        if temas == 'Evet':
            temas = 1
        else:
            temas = 2
            

        liste = [[cinsiyet,yas,hamilelik,diyabet,astim,tansiyon,kronik_rahatsizlik,kardiyolojik_rahatsizlik,obezite,cocuk_rahatsizligi,sigara,temas]]

        form_verileri = pd.DataFrame(liste)

        ml_model(form_verileri)

        cursor.close()
        flash("Bilgileriniz Alındı...","success")
        return redirect(url_for("homepage"))
    else:
        return render_template("form.html", form = form )


#Makine öğrenmesi
def ml_model(form_verileri):
    features = ['sex','age','pregnant','diabetes','asthma','hypertension','other_diseases','cardiovascular','obesity','chronic_kidney_failure','smoker','another_case','outcome']
    data = pd.read_csv('patient.csv')
    data = data[features]

    for i in range(0,95839):
        if data['pregnant'][i] == 97:
            data['pregnant'][i] = 2

    columns = data.columns
    columns_list = list()
    for i in columns:
        columns_list.append(i)
    
    columns_list.remove('age')

    for col in columns_list:
        data = data[data[col] < 3]
            
    y = data.outcome
    data = data.drop('outcome', axis=1)   
        
    X = data
  

    model = DecisionTreeClassifier(max_depth=500)
    model.fit(X,y)

    tahmin = model.predict(form_verileri)
    
    print('Decision Tree:',tahmin)
    

 

#Çıkış İşlemi
@app.route('/cikisyap')
def cikisyap():
    session.clear()
    flash("Çıkış İşleminiz Gerçekleşti...","success")
    return redirect(url_for("homepage"))
    
#Randevu Kayıt Etme
@app.route("/randevual" ,methods = ["GET","POST"])
def randevual():
    form = AppointmentForm(request.form)
    

    if request.method == "POST" and form.validate():
        unit = form.unit.data
        date = form.date.data
        time = form.time.data

        cursor = mysql.connection.cursor()
        
        sorgu = "Select * from appointment where unit = %s and date = %s and time = %s"
        result = cursor.execute(sorgu,(unit,date,time))
        if result > 0:
            flash("Bu tarihte bu birimden randevu alamazsınız...","danger")
            return redirect(url_for("randevual")) 
        else:
            sorgu1 = "Insert into appointment(tcno,unit,date,time) values (%s,%s,%s,%s)"

            cursor.execute(sorgu1,(session["tcno"],unit,date,time))
            mysql.connection.commit()

            cursor.close()
            flash("Randevu İşleminiz Gerçekleşti...","success")
            return redirect(url_for("homepage"))
    else:
        units = ["Radyoloji","Patoloji","Mikrobiyoloji","Kardiyoloji","Psikiyatri","Göz Hastalıkları","Ortopedi","Kadın Hastalıkları","Nöroloji","Göğüs Hastalıları","Beslenme Ve Diyet","Çocuk Psikiyatrisi","Cildiye","Genel Cerrahi","Üroloji","Kulak Burun Boğaz Hastalıkları"]
        times = ['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00']
        return render_template("randevual.html", form = form, units = units, times = times)

#Randevulari Listeleme
@app.route('/randevular')
def randevulistele():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From appointment where tcno = %s"

    result = cursor.execute(sorgu,(session["tcno"],))

    if result > 0:
        appointments = cursor.fetchall()
        return render_template("randevular.html", appointments = appointments)
    else:
        return render_template("randevular.html")

#Randevu Güncelleme
@app.route("/randevuguncelle/<string:id>", methods=["GET","POST"])
@login_required
def randevuguncelle(id):
    if request.method == "GET":
        cursor = mysql.connection.cursor()

        sorgu = "Select * from appointment where id = %s and tcno = %s"
        result = cursor.execute(sorgu,(id,session["tcno"]))

        if result == 0:
            flash("Böyle bir randevu yok veya bu işleme yetkiniz yok","danger")
            return redirect(url_for("homepage"))
        else:
            appointment = cursor.fetchone()
            form = AppointmentForm()

            form.unit.data = appointment["unit"]
            form.date.data = appointment["date"]
            form.time.data = appointment["time"]
            units = ["Radyoloji","Patoloji","Mikrobiyoloji","Kardiyoloji","Psikiyatri","Göz Hastalıkları","Ortopedi","Kadın Hastalıkları","Nöroloji","Göğüs Hastalıları","Beslenme Ve Diyet","Çocuk Psikiyatrisi","Cildiye","Genel Cerrahi","Üroloji","Kulak Burun Boğaz Hastalıkları"]
            times = ['09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00']
            return render_template("randevuguncelle.html",form = form, units = units, times = times)
    else:
       # POST REQUEST
        form = AppointmentForm(request.form)

        newunit = form.unit.data
        newdate = form.date.data
        newtime = form.time.data

        sorgu2 = "Update appointment Set unit = %s, date = %s, time = %s where id = %s "

        cursor = mysql.connection.cursor()

        cursor.execute(sorgu2,(newunit,newdate,newtime,id))

        mysql.connection.commit()

        flash("Randevu başarıyla güncellendi","success")

        return redirect(url_for("homepage"))

#Randevu Silme
@app.route("/randevusilme/<string:id>")
@login_required
def randevusilme(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from appointment where tcno = %s and id = %s"

    result = cursor.execute(sorgu,(session["tcno"],id))

    if result > 0:
        sorgu2 = "Delete from appointment where id = %s"

        cursor.execute(sorgu2,(id,))

        mysql.connection.commit()

        return redirect(url_for("homepage"))
    else:
        flash("Böyle bir randevu yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("homepage"))


@app.route("/homepage")
def anasayfa():
    return render_template("homepage.html")

@app.route('/birimlerimiz')
def bizeulasin():
    return render_template("birimlerimiz.html")

@app.route('/bizeulasin')
def birimlerimiz():
    return render_template("bizeulasin.html")

@app.route('/doktorlarimiz')
def doktorlarimiz():
    return render_template("doktorlarimiz.html")

@app.route('/hakkimizda')
def hakkimizda():
    return render_template("hakkimizda.html")

@app.route('/hastahaklari')
def hastahaklari():
    return render_template("hastahaklari.html")

@app.route('/hastasorumluluklari')
def hastasorumluluklari():
    return render_template("hastasorumluluklari.html")

@app.route('/refakatcikurallari')
def refakatcikurallari():
    return render_template("refakatcikurallari.html")

@app.route('/ziyaretcikurallari')
def ziyaretcikurallari():
    return render_template("ziyaretcikurallari.html")




if __name__ == "__main__":
    app.run(debug=True)




