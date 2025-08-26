from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, DateField
from wtforms.validators import DataRequired

from Apteka_app import db

class stanowiska(db.Model):
    __table__name = 'stanowiska'
    ID_Stanowiska = db.Column(db.Integer, primary_key=True)
    Nazwa_stanowiska = db.Column(db.String(50), nullable=False)
    Wynagrodzenie = db.Column(db.Integer, nullable=False)
    Pracownik = db.relationship('pracownicy', back_populates='Stanowisko')

class pracownicy(db.Model):
    __table__name = 'pracownicy'
    ID_Pracownika = db.Column(db.Integer, primary_key=True)
    Imie = db.Column(db.String(50), nullable=False)
    Nazwisko = db.Column(db.String(50), nullable=False)
    Nr_Telefonu = db.Column(db.Integer, nullable=False)
    ID_Stanowiska = db.Column(db.Integer, db.ForeignKey('stanowiska.ID_Stanowiska'), nullable=False)
    Stanowisko = db.relationship('stanowiska', back_populates='Pracownik')
    Transakcja = db.relationship('transakcja', back_populates='Pracownik')

class recepta(db.Model):
    __table__name = 'recepta'
    ID_posiadanej_recepty = db.Column(db.Integer, primary_key=True)
    Data_waznosci_recepty = db.Column(db.Date, nullable=False)
    Klient = db.relationship('klienci', back_populates='Recepta')

class klienci(db.Model):
    __table__name = 'klienci'
    ID_Klienta = db.Column(db.Integer, primary_key=True)
    Imie = db.Column(db.String(50), nullable=False)
    Nazwisko = db.Column(db.String(50), nullable=False)
    Nr_Telefonu = db.Column(db.Integer, nullable=False)
    ID_posiadanej_recepty = db.Column(db.Integer, db.ForeignKey('recepta.ID_posiadanej_recepty'), nullable=False)
    Recepta = db.relationship('recepta', back_populates='Klient')
    Transakcja = db.relationship('transakcja', back_populates='Klient')

class producent(db.Model):
    __table__name = 'producent'
    ID_Producenta = db.Column(db.Integer, primary_key=True)
    Nazwa_producenta = db.Column(db.String(50), nullable=False)
    Produkt = db.relationship('produkty', back_populates='Producent')


class produkty(db.Model):
    __table__name = 'produkty'
    ID_Produktu = db.Column(db.Integer, primary_key=True)
    Nazwa = db.Column(db.String(50), nullable=False)
    Cena = db.Column(db.Integer, nullable=False)
    Data_przydatnosci = db.Column(db.Date, nullable=False)
    Czy_na_recepte = db.Column(db.String(5), nullable=False)
    ID_Producenta = db.Column(db.Integer, db.ForeignKey('producent.ID_Producenta'), nullable=False)
    Producent = db.relationship('producent', back_populates='Produkt')
    Transakcja = db.relationship('transakcja', back_populates='Produkt')

class transakcja(db.Model):
    __table__name = 'transakcja'
    ID_Zakupu = db.Column(db.Integer, primary_key=True)
    Data_transakcji = db.Column(db.Date, nullable=False)
    ID_Produktu = db.Column(db.Integer, db.ForeignKey('produkty.ID_Produktu'), nullable=False)
    Produkt = db.relationship('produkty', back_populates='Transakcja')
    ID_Pracownika = db.Column(db.Integer, db.ForeignKey('pracownicy.ID_Pracownika'), nullable=False)
    Pracownik = db.relationship('pracownicy', back_populates='Transakcja')
    ID_Klienta = db.Column(db.Integer, db.ForeignKey('klienci.ID_Klienta'), nullable=False)
    Klient = db.relationship('klienci', back_populates='Transakcja')


class ReceptaForm(FlaskForm):
    Data_waznosci_recepty = DateField("Data_waznosci_recepty", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class StanowiskaForm(FlaskForm):
    Nazwa_stanowiska = StringField("Nazwa_stanowiska", validators=[DataRequired()])
    Wynagrodzenie = IntegerField("Wynagrodzenie", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class ProducentForm(FlaskForm):
    Nazwa_producenta = StringField("Nazwa_producenta", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class PracownicyForm(FlaskForm):
    Imie = StringField("Imie", validators=[DataRequired()])
    Nazwisko = StringField("Nazwisko", validators=[DataRequired()])
    Nr_Telefonu = IntegerField("Nr_Telefonu", validators=[DataRequired()])
    ID_Stanowiska = SelectField("ID_Stanowiska", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class KlienciForm(FlaskForm):
    Imie = StringField("Imie", validators=[DataRequired()])
    Nazwisko = StringField("Nazwisko", validators=[DataRequired()])
    Nr_Telefonu = IntegerField("Nr_Telefonu", validators=[DataRequired()])
    ID_posiadanej_recepty = SelectField("ID_posiadanej_recepty", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class ProduktyForm(FlaskForm):
    Nazwa = StringField("Nazwa", validators=[DataRequired()])
    Cena = IntegerField("Cena", validators=[DataRequired()])
    Data_przydatnosci = DateField("Data_przydatnosci", validators=[DataRequired()])
    Czy_na_recepte = StringField("Czy_na_recepte", validators=[DataRequired()])
    ID_Producenta = SelectField("ID_Producenta", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")

class TransakcjaForm(FlaskForm):
    Data_transakcji = DateField("Data_transakcji", validators=[DataRequired()])
    ID_Produktu = SelectField("ID_Produktu", validators=[DataRequired()])
    ID_Pracownika = SelectField("ID_Pracownika", validators=[DataRequired()])
    ID_Klienta = SelectField("ID_Klienta", validators=[DataRequired()])
    submit = SubmitField("Potwierdzenie")