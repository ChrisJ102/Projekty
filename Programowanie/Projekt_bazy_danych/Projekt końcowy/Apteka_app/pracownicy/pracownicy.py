from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.pracownicy import pracownicy_bp
from Apteka_app.models import pracownicy, PracownicyForm, stanowiska

@pracownicy_bp.route('/pracownicy', methods=['GET'])
def get_pracownicy():
    pracownicy_obj = pracownicy.query.order_by(pracownicy.ID_Pracownika)
    return render_template("pracownicy.html", pracownicy=pracownicy_obj)

@pracownicy_bp.route('/pracownicy/<int:pracownicy_id>', methods=['GET'])
def get_pracownicy_id(pracownicy_id):
    pracownicy_obj = pracownicy.query.get_or_404(pracownicy_id)
    return render_template("pracownicycred.html", pracownicy=pracownicy_obj)

@pracownicy_bp.route('/pracownicy/dodanie', methods=['GET', 'POST'])
def add_pracownicy():
    form = PracownicyForm()
    form.ID_Stanowiska.choices = [(stanowisko.ID_Stanowiska) for stanowisko in stanowiska.query.all()]
    if form.validate_on_submit():
        Pracownicy =pracownicy(
            Imie = form.Imie.data,
            Nazwisko=form.Nazwisko.data,
            Nr_Telefonu=form.Nr_Telefonu.data,
            ID_Stanowiska=form.ID_Stanowiska.data

        )
        db.session.add(Pracownicy)
        db.session.commit()

        form.Imie.data=""
        form.Nazwisko.data = ""
        form.Nr_Telefonu.data = ""
        form.ID_Stanowiska.data = ""

        flash("Pracownika dodano pomyślnie")

    pracownicy_obj = pracownicy.query.order_by(pracownicy.ID_Pracownika)
    return render_template("add_pracownicy.html", form=form)

@pracownicy_bp.route('/pracownicy/usuwanie/<int:pracownicy_id>')
def usuwanie_pracownicy(pracownicy_id:int):
    pracownicy_obj = pracownicy.query.get_or_404(pracownicy_id)
    try:
        db.session.delete(pracownicy_obj)
        db.session.commit()
        flash("Usunięto pracownika")
        pracownicy_obj = pracownicy.query.order_by(pracownicy.ID_Pracownika)
        return render_template("pracownicy.html", pracownicy=pracownicy_obj)
    except:
        pracownicy_obj = pracownicy.query.order_by(pracownicy.ID_Pracownika)
        return render_template("pracownicy.html", pracownicy=pracownicy_obj)

@pracownicy_bp.route('/pracownicy/modyfikacja/<int:pracownicy_id>', methods=['GET', 'POST'])
def modyfikacja_pracownicy(pracownicy_id):
    pracownicy_obj = pracownicy.query.get_or_404(pracownicy_id)
    form = PracownicyForm()
    form.ID_Stanowiska.choices = [(stanowisko.ID_Stanowiska) for stanowisko in stanowiska.query.all()]
    if request.method == "POST":
        pracownicy_obj.Imie = form.Imie.data
        pracownicy_obj.Nazwisko = form.Nazwisko.data
        pracownicy_obj.Nr_Telefonu = form.Nr_Telefonu.data
        pracownicy_obj.ID_Stanowiska = form.ID_Stanowiska.data

        db.session.commit()
        flash("Zmieniono dane pracownika")
        return render_template("pracownicycred.html", pracownicy=pracownicy_obj)
    else:
        return render_template("modyfikacja_pracownicy.html", form=form, pracownicy=pracownicy_obj)