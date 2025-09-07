from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.klienci import klienci_bp
from Apteka_app.models import klienci, KlienciForm, recepta

@klienci_bp.route('/klienci', methods=['GET'])
def get_klienci():
    klienci_obj = klienci.query.order_by(klienci.ID_Klienta)
    return render_template("klienci.html", klienci=klienci_obj)

@klienci_bp.route('/klienci/<int:klienci_id>', methods=['GET'])
def get_klienci_id(klienci_id):
    klienci_obj = klienci.query.get_or_404(klienci_id)
    return render_template("kliencicred.html", klienci=klienci_obj)

@klienci_bp.route('/klienci/dodanie', methods=['GET', 'POST'])
def add_klienci():
    form = KlienciForm()
    form.ID_posiadanej_recepty.choices = [(r.ID_posiadanej_recepty) for r in recepta.query.all()]
    if form.validate_on_submit():
        Klienci =klienci(
            Imie = form.Imie.data,
            Nazwisko=form.Nazwisko.data,
            Nr_Telefonu=form.Nr_Telefonu.data,
            ID_posiadanej_recepty=form.ID_posiadanej_recepty.data

        )
        db.session.add(Klienci)
        db.session.commit()

        form.Imie.data=""
        form.Nazwisko.data = ""
        form.Nr_Telefonu.data = ""
        form.ID_posiadanej_recepty.data = ""

        flash("Klienta dodano pomyślnie")

    klienci_obj = klienci.query.order_by(klienci.ID_Klienta)
    return render_template("add_klienci.html", form=form)

@klienci_bp.route('/klienci/usuwanie/<int:klienci_id>')
def usuwanie_klienci(klienci_id:int):
    klienci_obj = klienci.query.get_or_404(klienci_id)
    try:
        db.session.delete(klienci_obj)
        db.session.commit()
        flash("Usunięto klienta")
        klienci_obj = klienci.query.order_by(klienci.ID_Klienta)
        return render_template("klienci.html", klienci=klienci_obj)
    except:
        klienci_obj = klienci.query.order_by(klienci.ID_Klienta)
        return render_template("klienci.html", klienci=klienci_obj)

@klienci_bp.route('/klienci/modyfikacja/<int:klienci_id>', methods=['GET', 'POST'])
def modyfikacja_klienci(klienci_id):
    klienci_obj = klienci.query.get_or_404(klienci_id)
    form = KlienciForm()
    form.ID_posiadanej_recepty.choices = [(r.ID_posiadanej_recepty) for r in recepta.query.all()]
    if request.method == "POST":
        klienci_obj.Imie = form.Imie.data
        klienci_obj.Nazwisko = form.Nazwisko.data
        klienci_obj.Nr_Telefonu = form.Nr_Telefonu.data
        klienci_obj.ID_posiadanej_recepty = form.ID_posiadanej_recepty.data

        db.session.commit()
        flash("Zmieniono dane klienta")
        return render_template("kliencicred.html", klienci=klienci_obj)
    else:
        return render_template("modyfikacja_klienci.html", form=form, klienci=klienci_obj)