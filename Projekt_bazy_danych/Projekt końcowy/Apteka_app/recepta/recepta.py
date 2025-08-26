from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.recepta import recepta_bp
from Apteka_app.models import recepta, ReceptaForm

@recepta_bp.route('/recepta', methods=['GET'])
def get_recepta():
    recepty = recepta.query.order_by(recepta.ID_posiadanej_recepty)
    return render_template("recepta.html", recepta=recepty)

@recepta_bp.route('/recepta/<int:recepta_id>', methods=['GET'])
def get_recepta_id(recepta_id):
    recepty = recepta.query.get_or_404(recepta_id)
    return render_template("receptacred.html", recepta=recepty)

@recepta_bp.route('/recepta/dodanie', methods=['GET', 'POST'])
def add_recepta():
    form = ReceptaForm()
    if form.validate_on_submit():
        Recepta = recepta(
            Data_waznosci_recepty=form.Data_waznosci_recepty.data,
        )
        db.session.add(Recepta)
        db.session.commit()

        form.Data_waznosci_recepty.data=""

        flash("Recepte dodano pomyślnie")

    recepty = recepta.query.order_by(recepta.ID_posiadanej_recepty)
    return render_template("add_recepta.html", form=form)

@recepta_bp.route('/recepta/usuwanie/<int:recepta_id>')
def usuwanie_recepty(recepta_id:int):
    recepty = recepta.query.get_or_404(recepta_id)
    try:
        db.session.delete(recepty)
        db.session.commit()
        flash("Usunięto recepte")
        recepty = recepta.query.order_by(recepta.ID_posiadanej_recepty)
        return render_template("recepta.html", recepta=recepty)
    except:
        recepty = recepta.query.order_by(recepta.ID_posiadanej_recepty)
        return render_template("recepta.html", recepta=recepty)

@recepta_bp.route('/recepta/modyfikacja/<int:recepta_id>', methods=['GET', 'POST'])
def modyfikacja_recepty(recepta_id):
    recepty = recepta.query.get_or_404(recepta_id)
    form = ReceptaForm()
    if request.method == "POST":
        recepty.Data_waznosci_recepty = form.Data_waznosci_recepty.data

        db.session.commit()
        flash("Zmieniono date ważnosci recepty")
        return render_template("receptacred.html", recepta=recepty)
    else:
        return render_template("modyfikacja_recepta.html", form=form, recepta=recepty)