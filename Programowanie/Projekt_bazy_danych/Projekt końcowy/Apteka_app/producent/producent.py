from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.producent import producent_bp
from Apteka_app.models import producent, ProducentForm

@producent_bp.route('/producent', methods=['GET'])
def get_producent():
    producent_obj = producent.query.order_by(producent.ID_Producenta)
    return render_template("producenci.html", producent=producent_obj)

@producent_bp.route('/producent/<int:producent_id>', methods=['GET'])
def get_producent_id(producent_id):
    producent_obj = producent.query.get_or_404(producent_id)
    return render_template("producencicred.html", producent=producent_obj)

@producent_bp.route('/producent/dodanie', methods=['GET', 'POST'])
def add_producenta():
    form = ProducentForm()
    if form.validate_on_submit():
        Producent = producent(
            Nazwa_producenta=form.Nazwa_producenta.data,
        )
        db.session.add(Producent)
        db.session.commit()

        form.Nazwa_producenta.data=""

        flash("Producenta dodano pomyślnie")

    producent_obj = producent.query.order_by(producent.ID_Producenta)
    return render_template("add_producenta.html", form=form)

@producent_bp.route('/producent/usuwanie/<int:producent_id>')
def usuwanie_producenta(producent_id:int):
    producent_obj = producent.query.get_or_404(producent_id)
    try:
        db.session.delete(producent_obj)
        db.session.commit()
        flash("Usunięto producenta")
        producent_obj = producent.query.order_by(producent.ID_Producenta)
        return render_template("producent.html", producent=producent_obj)
    except:
        producent_obj = producent.query.order_by(producent.ID_Producenta)
        return render_template("producent.html", producent=producent_obj)

@producent_bp.route('/producent/modyfikacja/<int:producent_id>', methods=['GET', 'POST'])
def modyfikacja_producenta(producent_id):
    producent_obj= producent.query.get_or_404(producent_id)
    form = ProducentForm()
    if request.method == "POST":
        producent_obj.Nazwa_producenta = form.Nazwa_producenta.data

        db.session.commit()
        flash("Zmieniono nazwę producenta")
        return render_template("producencicred.html", producent=producent_obj)
    else:
        return render_template("modyfikacja_producenta.html", form=form, producent=producent_obj)