from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.produkty import produkty_bp
from Apteka_app.models import produkty, producent, ProduktyForm

@produkty_bp.route('/produkty', methods=['GET'])
def get_produkty():
    produkty_obj = produkty.query.order_by(produkty.ID_Produktu)
    return render_template("produkty.html", produkty=produkty_obj)

@produkty_bp.route('/produkty/<int:produkty_id>', methods=['GET'])
def get_produkty_id(produkty_id):
    produkty_obj = produkty.query.get_or_404(produkty_id)
    return render_template("produktycred.html", produkty=produkty_obj)

@produkty_bp.route('/produkty/dodanie', methods=['GET', 'POST'])
def add_produkty():
    form = ProduktyForm()
    form.ID_Producenta.choices = [(p.ID_Producenta) for p in producent.query.all()]
    if form.validate_on_submit():
        Produkty =produkty(
            Nazwa = form.Nazwa.data,
            Cena=form.Cena.data,
            Data_przydatnosci=form.Data_przydatnosci.data,
            Czy_na_recepte=form.Czy_na_recepte.data,
            ID_Producenta=form.ID_Producenta.data,

        )
        db.session.add(Produkty)
        db.session.commit()

        form.Nazwa.data=""
        form.Cena.data = ""
        form.Data_przydatnosci.data = ""
        form.Czy_na_recepte.data = ""
        form.ID_Producenta.data = ""

        flash("Produkt dodano pomyślnie")

    produkty_obj = produkty.query.order_by(produkty.ID_Produktu)
    return render_template("add_produkty.html", form=form)

@produkty_bp.route('/produkty/usuwanie/<int:produkty_id>')
def usuwanie_produkty(produkty_id:int):
    produkty_obj = produkty.query.get_or_404(produkty_id)
    try:
        db.session.delete(produkty_obj)
        db.session.commit()
        flash("Usunięto produkt")
        produkty_obj = produkty.query.order_by(produkty.ID_Produktu)
        return render_template("produkty.html", produkty=produkty_obj)
    except:
        produkty_obj = produkty.query.order_by(produkty.ID_Produktu)
        return render_template("produkty.html", produkty=produkty_obj)

@produkty_bp.route('/produkty/modyfikacja/<int:produkty_id>', methods=['GET', 'POST'])
def modyfikacja_produkty(produkty_id):
    produkty_obj = produkty.query.get_or_404(produkty_id)
    form = ProduktyForm()
    form.ID_Producenta.choices = [(p.ID_Producenta) for p in producent.query.all()]
    if request.method == "POST":
        produkty_obj.Nazwa = form.Nazwa.data
        produkty_obj.Cena = form.Cena.data
        produkty_obj.Data_przydatnosci = form.Data_przydatnosci.data
        produkty_obj.Czy_na_recepte = form.Czy_na_recepte.data
        produkty_obj.ID_Producenta = form.ID_Producenta.data

        db.session.commit()
        flash("Zmieniono dane produktu")
        return render_template("produktycred.html", produkty=produkty_obj)
    else:
        return render_template("modyfikacja_produkty.html", form=form, produkty=produkty_obj)