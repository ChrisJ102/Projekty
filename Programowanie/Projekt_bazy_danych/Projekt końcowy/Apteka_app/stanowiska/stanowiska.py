from flask import render_template, flash, request

from Apteka_app import db
from Apteka_app.stanowiska import stanowiska_bp
from Apteka_app.models import stanowiska, StanowiskaForm

@stanowiska_bp.route('/stanowiska', methods=['GET'])
def get_stanowiska():
    stanowisko_obj = stanowiska.query.order_by(stanowiska.ID_Stanowiska)
    return render_template("stanowiska.html", stanowiska=stanowisko_obj)

@stanowiska_bp.route('/stanowiska/<int:stanowisko_id>', methods=['GET'])
def get_stanowisko_id(stanowisko_id):
    stanowisko_obj = stanowiska.query.get_or_404(stanowisko_id)
    return render_template("stanowiskacred.html", stanowiska=stanowisko_obj)


@stanowiska_bp.route('/stanowiska/dodanie', methods=['GET', 'POST'])
def add_stanowisko():
    form = StanowiskaForm()
    if form.validate_on_submit():
        Stanowisko = stanowiska(
            Nazwa_stanowiska=form.Nazwa_stanowiska.data,
            Wynagrodzenie=form.Wynagrodzenie.data,
        )
        db.session.add(Stanowisko)
        db.session.commit()

        form.Nazwa_stanowiska.data=""
        form.Wynagrodzenie.data = ""

        flash("Stanowisko dodano pomyślnie")

    stanowisko_obj = stanowiska.query.order_by(stanowiska.ID_Stanowiska)
    return render_template("add_stanowisko.html", form=form)

@stanowiska_bp.route('/stanowiska/usuwanie/<int:stanowisko_id>')
def usuwanie_stanowiska(stanowisko_id:int):
    stanowisko_obj = stanowiska.query.get_or_404(stanowisko_id)
    try:
        db.session.delete(stanowisko_obj)
        db.session.commit()
        flash("Usunięto stanowisko")
        stanowisko_obj = stanowiska.query.order_by(stanowiska.ID_Stanowiska)
        return render_template("stanowiska.html", stanowiska=stanowisko_obj)
    except:
        stanowisko_obj = stanowiska.query.order_by(stanowiska.ID_Stanowiska)
        return render_template("stanowiska.html", stanowiska=stanowisko_obj)

@stanowiska_bp.route('/stanowiska/modyfikacja/<int:stanowisko_id>', methods=['GET', 'POST'])
def modyfikacja_stanowiska(stanowisko_id):
    stanowisko_obj = stanowiska.query.get_or_404(stanowisko_id)
    form = StanowiskaForm()
    if request.method == "POST":
        stanowisko_obj.Nazwa_stanowiska = form.Nazwa_stanowiska.data
        stanowisko_obj.Wynagrodzenie = form.Wynagrodzenie.data

        db.session.commit()
        flash("Zmieniono dane stanowiska")
        return render_template("stanowiskacred.html", stanowiska=stanowisko_obj)
    else:
        return render_template("modyfikacja_stanowiska.html", form=form, stanowiska=stanowisko_obj)