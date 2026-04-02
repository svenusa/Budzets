from flask import Flask, render_template, request, redirect, url_for
import csv
import os
from datetime import datetime

# Izveido Flask lietotni
app = Flask(__name__)

# CSV fails, kur glabāsim datus
CSV_FAILS = "dati.csv"

# Saraksts, kurā glabāsim visus ierakstus programmā
dati = []


def ieladet_datus():
 
    #Nolasa datus no CSV faila un ieliek tos sarakstā 'dati'.
    #Ja fails neeksistē, programma vienkārši turpina darbu.
    
    global dati
    dati = []

    if not os.path.exists(CSV_FAILS):
        return

    with open(CSV_FAILS, mode="r", newline="", encoding="utf-8") as fails:
        lasitajs = csv.DictReader(fails)
        for rinda in lasitajs:
            # Pārveidojam summu uz skaitli
            rinda["summa"] = float(rinda["summa"])
            dati.append(rinda)


def saglabat_datus():
    
    #Saglabā visus ierakstus CSV failā.
    #Katru reizi pārraksta failu no jauna, lai dati būtu aktuāli.
    
    with open(CSV_FAILS, mode="w", newline="", encoding="utf-8") as fails:
        lauki = ["id", "tips", "summa", "apraksts", "datums"]
        rakstitajs = csv.DictWriter(fails, fieldnames=lauki)
        rakstitajs.writeheader()
        rakstitajs.writerows(dati)


def aprakstit_bilanci():
   
    #Aprēķina:
    #- ienākumu summu
    #- izdevumu summu
    #- bilanci

    #Bilance = ienākumi - izdevumi
    
    ienakumi = sum(ier["summa"] for ier in dati if ier["tips"] == "Ienākums")
    izdevumi = sum(ier["summa"] for ier in dati if ier["tips"] == "Izdevums")
    bilance = ienakumi - izdevumi
    return ienakumi, izdevumi, bilance


# Datus ielādē uzreiz, kad programma startē
ieladet_datus()


@app.route("/")
def index():
    
    #Galvenā lapa.
    #Parāda:
    #- visus ierakstus
    #- bilanci
    #- filtrētu skatu pēc tipa
    
    filtrs = request.args.get("filtrs", "visi")

    # Filtrējam ierakstus pēc izvēles
    if filtrs == "ienakumi":
        paradamie = [ier for ier in dati if ier["tips"] == "Ienākums"]
    elif filtrs == "izdevumi":
        paradamie = [ier for ier in dati if ier["tips"] == "Izdevums"]
    else:
        paradamie = dati

    ienakumi, izdevumi, bilance = aprakstit_bilanci()

    return render_template(
        "index.html",
        dati=paradamie,
        ienakumi=ienakumi,
        izdevumi=izdevumi,
        bilance=bilance,
        filtrs=filtrs
    )


@app.route("/pievienot", methods=["POST"])
def pievienot():
    
    #Pievieno jaunu ierakstu.
    #No formas saņem:
    #- tips
    #- summa
    #- apraksts
   
    tips = request.form.get("tips", "").strip()
    summa = request.form.get("summa", "").strip()
    apraksts = request.form.get("apraksts", "").strip()

    # Vienkārša validācija
    if not tips or not summa or not apraksts:
        return redirect(url_for("index"))

    try:
        summa = float(summa)
    except ValueError:
        # Ja lietotājs ievada tekstu nevis skaitli
        return redirect(url_for("index"))

    # Izveidojam unikālu ID, lai varētu dzēst ierakstus
    jauns_id = 1
    if dati:
        jauns_id = max(int(ier["id"]) for ier in dati) + 1

    # Datums šodienas formātā
    datums = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Pievienojam jaunu ierakstu sarakstam
    ieraksts = {
        "id": str(jauns_id),
        "tips": tips,
        "summa": summa,
        "apraksts": apraksts,
        "datums": datums
    }
    dati.append(ieraksts)

    # Saglabājam failā
    saglabat_datus()

    return redirect(url_for("index"))


@app.route("/dzest/<id>", methods=["POST"])
def dzest(id):
    
    #Dzēš ierakstu pēc ID.
    
    global dati
    dati = [ier for ier in dati if ier["id"] != id]
    saglabat_datus()
    return redirect(url_for("index"))


@app.route("/bilance")
def bilance_lapa():
    
    #Papildu lapa bilancei.
    
    ienakumi, izdevumi, bilance = aprakstit_bilanci()
    return render_template(
        "bilance.html",
        ienakumi=ienakumi,
        izdevumi=izdevumi,
        bilance=bilance
    )


if __name__ == "__main__":
    app.run(debug=True)