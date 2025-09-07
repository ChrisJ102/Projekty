from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.transakcja import transakcja_bp
from Apteka_app.models import transakcja, produkty, TransakcjaForm, pracownicy, klienci

@transakcja_bp.route('/transakcja', methods=['GET'])
def get_transakcja():
    transakcja_obj = transakcja.query.order_by(transakcja.ID_Zakupu)
    return render_template("transakcja.html", transakcja=transakcja_obj)

@transakcja_bp.route('/transakcja/<int:transakcja_id>', methods=['GET'])
def get_transakcja_id(transakcja_id):
    transakcja_obj = transakcja.query.get_or_404(transakcja_id)
    return render_template("transakcjacred.html", transakcja=transakcja_obj)

@transakcja_bp.route('/transakcja/dodanie', methods=['GET', 'POST'])
def add_transakcja():
    form = TransakcjaForm()
    form.ID_Produktu.choices = [(p.ID_Produktu) for p in produkty.query.all()]
    form.ID_Pracownika.choices = [(p.ID_Pracownika) for p in pracownicy.query.all()]
    form.ID_Klienta.choices = [(p.ID_Klienta) for p in klienci.query.all()]
    if form.validate_on_submit():
        Transakcja =transakcja(
            Data_transakcji = form.Data_transakcji.data,
            ID_Produktu=form.ID_Produktu.data,
            ID_Pracownika=form.ID_Pracownika.data,
            ID_Klienta=form.ID_Klienta.data

        )
        db.session.add(Transakcja)
        db.session.commit()

        form.Data_transakcji.data = ""
        form.ID_Produktu.data=""
        form.ID_Pracownika.data = ""
        form.ID_Klienta.data = ""

        flash("Transakcje dodano pomyślnie")

    transakcja_obj = transakcja.query.order_by(transakcja.ID_Zakupu)
    return render_template("add_transakcja.html", form=form)

@transakcja_bp.route('/transakcja/usuwanie/<int:transakcja_id>')
def usuwanie_transakcja(transakcja_id:int):
    transakcja_obj = transakcja.query.get_or_404(transakcja_id)
    try:
        db.session.delete(transakcja_obj)
        db.session.commit()
        flash("Usunięto transakcje")
        transakcja_obj = transakcja.query.order_by(transakcja.ID_Zakupu)
        return render_template("transakcja.html", transakcja=transakcja_obj)
    except:
        transakcja_obj = transakcja.query.order_by(transakcja.ID_Pracownika)
        return render_template("transakcja.html", transakcja=transakcja_obj)

@transakcja_bp.route('/transakcja/modyfikacja/<int:transakcja_id>', methods=['GET', 'POST'])
def modyfikacja_transakcja(transakcja_id):
    transakcja_obj = transakcja.query.get_or_404(transakcja_id)
    form = TransakcjaForm()
    form.ID_Produktu.choices = [(p.ID_Produktu) for p in produkty.query.all()]
    form.ID_Pracownika.choices = [(p.ID_Pracownika) for p in pracownicy.query.all()]
    form.ID_Klienta.choices = [(p.ID_Klienta) for p in klienci.query.all()]
    if request.method == "POST":
        transakcja_obj.Data_transakcji = form.Data_transakcji.data
        transakcja_obj.ID_Produktu = form.ID_Produktu.data
        transakcja_obj.ID_Pracownika = form.ID_Pracownika.data
        transakcja_obj.ID_Klienta = form.ID_Klienta.data


        db.session.commit()
        flash("Zmieniono dane transakcji")
        return render_template("transakcjacred.html", transakcja=transakcja_obj)
    else:
        return render_template("modyfikacja_transakcja.html", form=form, transakcja=transakcja_obj)