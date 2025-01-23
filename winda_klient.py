import threading
import time
import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
import json
import requests

# Initialize statystyki with default values
statystyki = {
    "pokonane_pietra": 0,
    "przebyta_odleglosc": 0.0,
    "zaliczone_przystanki": 0,
    "przewiezieni_pasazerowie": {
        "typ1": 0,
        "typ2": 0,
        "typ3": 0
    },
    "liczba_otworzen_drzwi": 0,
    "liczba_oczekujacych_pasazerow": 0
}
#from init_db import init_db, zapiszLog, wczytajLogi, pobierznajnowszyRekordZTabeliLogs  # type: ignore # Importowanie funkcji init_db z nowego pliku

wielkośćSzybu = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
kolejkaPasażerów = None #lista
polecenia = [] #lista
kierunekJazdy = 0  # gdzie: 0 to postój, 1 - to dół, 2 to góra
#wielkośćSzybu = None #lista
#pietraIPasazerowie = [(pietro, 0) for pietro in wielkośćSzybu]
poleceniaDrzwi = [] #lista: 0 - zamknij, 1 - otwórz
lokalizacjaWindy = 0
wybrane_przyciski = {}
etykietyPieter = [] # Lista do przechowywania referencji do etykiet ikon pięter
etykietyStanuWyboruPietra = [] # Lista do przechowywania referencji do etykiet ikon wyboru piętra w windzie
etykietyStanuPrzywołaniaPiętraDoGóry = [] # Lista do przechowywania referencji do etykiet ikon przywołania windy do góry
etykietyStanuPrzywołaniaPiętraDoDołu = [] # Lista do przechowywania referencji do etykiet ikon przywołania windy do dołu
statusPracyDrzwi = 2 # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
logOkno = None # Referencja do okna logów
logWidżet = None  # Referencja do widżetu tekstowego
dbFilePath = "logi_windy.db"
przebytaOdległość = 0.0
statusSymulacji = None
zmiennaCzęstotliwościGenerowaniaPasażerów = None


# Adres URL serwera Flask
BASE_URL = 'https://winda.onrender.com'
URL_GET_WIELKOSC_SZYBU = f'{BASE_URL}/get_wielkosc_szybu'
URL_GET_WINDA_STATUS = f'{BASE_URL}/get_winda_status'
URL_GET_POLECENIA_DRZWI = f'{BASE_URL}/get_polecenia_drzwi'
URL_GET_STATYSTYKI = f'{BASE_URL}/get_statystyki'
URL_POST_WLACZ_WYLACZ_SYMULACJE = f'{BASE_URL}/wlacz_wylacz_symulacje'
URL_GET_STATUS_SYMULACJI = f'{BASE_URL}/get_status_symulacji'
URL_POST_ZMIEN_CZESTOTLIWOSC = f'{BASE_URL}/zmien_czestotliwosc'


def getWielkośćSzybu():
    global wielkośćSzybu
    try:
        response = requests.get(URL_GET_WIELKOSC_SZYBU)
        if response.status_code == 200:
            data = response.json()
            print(f'Otrzymane dane szybu: {data}')
            # Aktualizacja zmiennych
            if isinstance(data, list):
                # Aktualizacja zmiennych
                wielkośćSzybu = data
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def getPoleceniaDrzwi():
    global poleceniaDrzwi, statusPracyDrzwi
    try:
        response = requests.get(URL_GET_POLECENIA_DRZWI)
        if response.status_code == 200:
            data = response.json()
            print(f'Otrzymane dane drzwi windy: {data}')
            # Aktualizacja zmiennych
            if isinstance(data, dict):
                poleceniaDrzwi = data.get('polecenia_drzwi')
                statusPracyDrzwi = data.get('statusPracyDrzwi')
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def aktualizujStanWindy():
    global lokalizacjaWindy, kierunekJazdy, polecenia, wybrane_przyciski, statusSymulacji, zmiennaCzęstotliwościGenerowaniaPasażerów
    try:
        response = requests.get(URL_GET_WINDA_STATUS)
        if response.status_code == 200:
            data = response.json()
            print(f'Otrzymane dane windy: {data}')
            # Aktualizacja zmiennych
            windy_data = data.get('windy_data', {})
            dane_symulacji = data.get('dane_symulacji', {})
            wybrane_przyciski = data.get('wybrane_przyciski')
            lokalizacjaWindy = windy_data.get('lokalizacjaWindy')
            kierunekJazdy = windy_data.get('kierunekJazdy')
            wybrane_przyciski = wybrane_przyciski['słownik']
            polecenia = windy_data.get('polecenia')
            statusSymulacji = dane_symulacji.get('status_symulacji')
            zmiennaCzęstotliwościGenerowaniaPasażerów = dane_symulacji.get('zmienna_częstotliwości_generowania_pasażerów')
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def aktualizujStatystyki():
    global liczbaPokonanychPięter, przebytaOdległość, liczbaPrzystanków, przewiezieniPasażerowieTyp1, przewiezieniPasażerowieTyp2, przewiezieniPasażerowieTyp3, liczbaOczekującychPasażerów
    try:
        response = requests.get(URL_GET_STATYSTYKI)
        if response.status_code == 200:
            data = response.json()
            print(f'Otrzymane dane statystyki: {data}')
            liczbaPokonanychPięter = data["pokonane_pietra"]
            przebytaOdległość = data["przebyta_odleglosc"]
            liczbaPrzystanków = data["zaliczone_przystanki"]
            przewiezieniPasażerowieTyp1 = data["przewiezieni_pasazerowie"]["typ1"]
            przewiezieniPasażerowieTyp2 = data["przewiezieni_pasazerowie"]["typ2"]
            przewiezieniPasażerowieTyp3 = data["przewiezieni_pasazerowie"]["typ3"]
            liczbaOczekującychPasażerów = data["liczba_oczekujacych_pasazerow"]
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def getStatusSymulacji():
    global statusSymulacji, zmiennaCzęstotliwościGenerowaniaPasażerów
    try:
        response = requests.get(URL_GET_STATUS_SYMULACJI)
        if response.status_code == 200:
            data = response.json()
            print(f'Status symulacji: {data}')
            statusSymulacji = data.get('statusSymulacji')
            zmiennaCzęstotliwościGenerowaniaPasażerów = data.get('zmienna_częstotliwości_generowania_pasażerów')
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def postWlaczWylaczSymulacje(status):
    try:
        response = requests.post(URL_POST_WLACZ_WYLACZ_SYMULACJE, json={'statusSymulacji': status})
        if response.status_code == 200:
            print(f'Status symulacji: {response.json()["statusSymulacji"]}')
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def postZmienCzestotliwosc(czestotliwosc):
    try:
        response = requests.post(URL_POST_ZMIEN_CZESTOTLIWOSC, json={'zmiennaCzęstotliwościGenerowaniaPasażerów': czestotliwosc})
        if response.status_code == 200:
            print(f'Częstotliwość generowania pasażerów: {response.json()["zmiennaCzęstotliwościGenerowaniaPasażerów"]}')
        else:
            print(f'Błąd: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Błąd połączenia: {e}')


def aktualizujWyświetlanieGui():
    aktualizujKoloryPieter()
    aktualizujStrzałkęKierunkuJazdy()
    aktualizujWyświetlaczPiętra()
    aktualizujStanPrzyciskówDodawaniaPoleceń()
    aktualizujPracęDrzwi()
    aktualizujStanStatusuSymulacji()
    aktualizujStanSuwakaCzestotliwosci()

def cyklicznaAktualizacja():
    aktualizujStanWindy()
    getPoleceniaDrzwi()
    aktualizujWyświetlanieGui()
    root.after(1000, cyklicznaAktualizacja)


def aktualizujWyświetlaneStatystykiSymulacji():
    aktualizujStatystyki()
    statystykaPokonanePiętra.config(text=f"{liczbaPokonanychPięter}")
    statystykaPrzebytaOdległość.config(text=f"{przebytaOdległość:.2f} km")
    statystykaPrzystanki.config(text=f"{liczbaPrzystanków}")
    statystykaPrzewiezieniPasażerowie.config(text=f"{przewiezieniPasażerowieTyp1}")    
    statystykaPrzewiezieniPasażerowieUnikalni.config(text=f"{przewiezieniPasażerowieTyp2}")
    statystykaPrzewiezieniPasażerowieUtraceni.config(text=f"{przewiezieniPasażerowieTyp3}")
    statystykaPrzewiezieniPasażerowieOczekujący.config(text=f"{liczbaOczekującychPasażerów}")
    root.after(5000, aktualizujWyświetlaneStatystykiSymulacji)


def aktualizujPracęDrzwi():
    aktualizujWyświetlaczPracyDrzwi()
    aktualizujIkonyDrzwi()


def aktualizujKoloryPieter():
    for i, etykieta in enumerate(etykietyPieter):
        if i == lokalizacjaWindy:
            etykieta.config(bg="white", bd=1, relief="solid")
        else:
            etykieta.config(width=3, height=2, bg="lightgrey", bd=0, relief="flat")

#
def aktualizujStanPrzyciskówDodawaniaPoleceń(): # do poprawienia sposóbwyświtlania wybranych przycisków
    if wybrane_przyciski and any(wybrane_przyciski.values()):
        for klucz, wartość in wybrane_przyciski.items():
            lokalizacja = int(klucz)
            źródłoPolecenia = int(wartość)
            if źródłoPolecenia == 1: #panel windy
                aktualizujStanPrzyciskuWyboruPiętra(lokalizacja, 1)
            elif źródłoPolecenia == 2: #do góry w panelu dla piętra
                aktualizujStanPrzywołaniaPiętraDoGóry(lokalizacja, 1)
            elif źródłoPolecenia == 3: #do dołu w panelu dla piętra
                aktualizujStanPrzywołaniaPiętraDoDołu(lokalizacja, 1)
    else:
        pass


def aktualizujStanPrzyciskuWyboruPiętra(lokalizacja, stan=None):
    for i, przyciskWyboruPiętra in enumerate(etykietyStanuWyboruPietra):
        if stan == 1 and lokalizacja in polecenia and i == lokalizacja:
            przyciskWyboruPiętra.config(bg="red")
        else:
            przyciskWyboruPiętra.config(bg="SystemButtonFace")


def aktualizujStanPrzywołaniaPiętraDoGóry(lokalizacja, stan=None):
    for i, przyciskPrzywołaniaWindyDoGóry in enumerate(etykietyStanuPrzywołaniaPiętraDoGóry):
        if stan == 1 and lokalizacja in polecenia and i == lokalizacja:
            przyciskPrzywołaniaWindyDoGóry.config(bg="red")
        else:
            przyciskPrzywołaniaWindyDoGóry.config(bg="SystemButtonFace")

#
def aktualizujStanPrzywołaniaPiętraDoDołu(lokalizacja, stan=None):
    for i, przyciskPrzywołaniaWindyDoDołu in enumerate(etykietyStanuPrzywołaniaPiętraDoDołu):
        if stan == 1 and lokalizacja in polecenia and i == (lokalizacja - 1):
            przyciskPrzywołaniaWindyDoDołu.config(bg="red")
        else:
            przyciskPrzywołaniaWindyDoDołu.config(bg="SystemButtonFace")


def aktualizujStrzałkęKierunkuJazdy():
    if kierunekJazdy == 2:
        wyświetlaczKierunkuJazdy.config(text="↑")
        wyświetlaczKierunkuJazdyDlaPiętra.config(text="↑")
    elif kierunekJazdy == 1:
        wyświetlaczKierunkuJazdy.config(text="↓")
        wyświetlaczKierunkuJazdyDlaPiętra.config(text="↓")
    else:
        wyświetlaczKierunkuJazdy.config(text=" ")
        wyświetlaczKierunkuJazdyDlaPiętra.config(text=" ")

def aktualizujWyświetlaczPiętra():
    wyświetlaczPiętra.config(text=f"{lokalizacjaWindy}")
    wyświetlaczPiętraDlaPiętra.config(text=f"{lokalizacjaWindy}")

#
def aktualizujWyświetlaczPracyDrzwi(): # 0 - zamykanie, 1 - otwieranie, 2 - zamknięte, 3 - otwarte
    if statusPracyDrzwi == 0:
        wyświetlaczPracyDrzwi.config(text=">> <<")
        wyświetlaczRuchuDrzwi.config(text=">> <<")
    elif statusPracyDrzwi == 1:
        wyświetlaczPracyDrzwi.config(text="<< >>")
        wyświetlaczRuchuDrzwi.config(text="<< >>")
    else:
        wyświetlaczPracyDrzwi.config(text=" ")
        wyświetlaczRuchuDrzwi.config(text=" ")

#
def aktualizujIkonyDrzwi():
    if statusPracyDrzwi == 1 or statusPracyDrzwi == 3:
        ikonaDrzwi1.config(bg="lightgrey", bd=1, relief="ridge")
        ikonaDrzwi2.config(bg="white", bd=0, relief="flat")
        ikonaDrzwi3.config(bg="white", bd=0, relief="flat")
        ikonaDrzwi4.config(bg="lightgrey", bd=1, relief="ridge")
    if statusPracyDrzwi == 0 or statusPracyDrzwi == 2:
        ikonaDrzwi1.config(bg="white", bd=0, relief="flat")
        ikonaDrzwi2.config(bg="lightgrey", bd=1, relief="ridge")
        ikonaDrzwi3.config(bg="lightgrey", bd=1, relief="ridge")
        ikonaDrzwi4.config(bg="white", bd=0, relief="flat")

def aktualizujStanStatusuSymulacji():
    if statusSymulacji == 0:
        stanSymulacji.config(text="Nieaktywna", fg="Red")
    else:
        stanSymulacji.config(text="Aktywna", fg="Green")


def aktualizujStanSuwakaCzestotliwosci():
    skalaCzęstotliwości.set(zmiennaCzęstotliwościGenerowaniaPasażerów)


def otwórzZamknijOknoLogów():
    global logOkno, logWidżet
    if logOkno is None or not logOkno.winfo_exists():
        logOkno = tk.Toplevel(root)
        logOkno.title("Logi Windy")
        logOkno.geometry("1300x400")
        logOkno.attributes("-topmost", True)
        logWidżet = tk.Text(logOkno, wrap=tk.WORD, height=20, width=80, bg="black", fg="white")
        logWidżet.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbarOknoLogówFrame = tk.Frame(logOkno)
        scrollbarOknoLogówFrame.pack(expand=True, fill=tk.BOTH)
        scrollbarOknoLogów = tk.Scrollbar(scrollbarOknoLogówFrame, command=logWidżet.yview)
        scrollbarOknoLogów.pack(side=tk.RIGHT, fill=tk.Y)
        logWidżet.config(yscrollcommand=scrollbarOknoLogów.set)
        #wczytajLogiDoWidżetu()
    else:
        logOkno.destroy()
        logOkno = None


def włączWyłączSymulacje():
    global statusSymulacji
    if statusSymulacji == 0:
        statusSymulacji = 1
    else:
        statusSymulacji = 0
    postWlaczWylaczSymulacje(statusSymulacji)


"""def wyświetlLogWWidżecie():
    last_row = pobierznajnowszyRekordZTabeliLogs()
    prefixes = ["ID: ", "Data: ", "User: ", "Zdarzenie: ", "Cel: ", "Źródło: ", "Kierunek: ", "Polecenia: ", "Praca drzwi: "]
    if logWidżet and last_row and logWidżet.winfo_exists():
        log_entry = " | ".join([f"{prefixes[i]}{str(col)}" for i, col in enumerate(last_row) if col is not None])
        logWidżet.insert(tk.END, f"{log_entry}\n")
        logWidżet.see(tk.END)


def wczytajLogiDoWidżetu():
    global logWidżet
    if logWidżet:
        rows = wczytajLogi() 
        prefixes = ["ID: ", "Data: ", "User: ", "Zdarzenie: ", "Cel: ", "Źródło: ", "Kierunek: ", "Polecenia: ", "Praca drzwi: "]
        for row in rows:
            log_entry = " | ".join([f"{prefixes[i]}{str(col)}" for i, col in enumerate(row) if col is not None])
            logWidżet.insert(tk.END, f"{log_entry}\n")
            logWidżet.see(tk.END)"""





root = tk.Tk()
root.title("Symulator Windy")
root.geometry("1300x700") 
root.attributes("-fullscreen", True)


#główny podział okna
poziom1 = tk.Label(root)
poziom1.grid(row=0, column=0, padx=10, pady=0, sticky="w")
poziom2 = tk.Label(root)
poziom2.grid(row=1, column=0, padx=10, pady=0, sticky="w")

# Ramka - Panel ze statusem Windy
panelStatusuWindyFrame = tk.LabelFrame(poziom1, text="Status Windy", bd=2, relief="groove", width=335, height=450, labelanchor="n")
panelStatusuWindyFrame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
panelStatusuWindyFrame.grid_propagate(False)

etykietaSzybuFrame = tk.LabelFrame(panelStatusuWindyFrame, text="Pozycja Windy", bd=2, relief="groove", width=150, height=350, labelanchor="n")
etykietaSzybuFrame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

etykietaDrzwiWindyFrame = tk.LabelFrame(panelStatusuWindyFrame, text="Status Drzwi", bd=2, relief="groove", width=150, height=250, labelanchor="n")
etykietaDrzwiWindyFrame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

wyświetlaczRuchuDrzwi = tk.Label(etykietaDrzwiWindyFrame, width=7, height=1, font=("Helvetica", 12), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczRuchuDrzwi.grid(row=0,column=0, padx=10, sticky="e")

etykietaIkonyDrzwi = tk.LabelFrame(etykietaDrzwiWindyFrame, width=8, height=1,bd=1, relief="flat", highlightbackground="black", highlightcolor="black", highlightthickness=1)
etykietaIkonyDrzwi.grid(row=1, column=0, padx=10, pady=10)

ikonaDrzwi1 = tk.Label(etykietaIkonyDrzwi, width=1, height=3, bg="white", bd=1, relief="ridge")
ikonaDrzwi1.grid(row=0,column=0, padx=1, pady=1, sticky="ne")
ikonaDrzwi2 = tk.Label(etykietaIkonyDrzwi, width=2, height=3, bg="lightgrey", bd=1, relief="ridge")
ikonaDrzwi2.grid(row=0,column=1, pady=1, sticky="nw")
ikonaDrzwi3 = tk.Label(etykietaIkonyDrzwi, width=2, height=3, bg="lightgrey", bd=1, relief="ridge")
ikonaDrzwi3.grid(row=0,column=2, pady=1, sticky="nw")
ikonaDrzwi4 = tk.Label(etykietaIkonyDrzwi, width=1, height=3, bg="white", bd=1, relief="ridge")
ikonaDrzwi4.grid(row=0,column=3, padx=1, pady=1, sticky="nw")

etykietaStatusówFrame = tk.LabelFrame(panelStatusuWindyFrame, text="Statusy", bd=2, relief="groove", width=50, height=100, labelanchor="n")
etykietaStatusówFrame.grid(row=0, column=1, padx=10, pady=135, sticky="n")

etykietaStatusWindy = tk.Label(etykietaStatusówFrame, text="Status windy:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatusWindy.grid(row=0,column=0, padx=10, pady=10, sticky="w")
statusWindy = tk.Label(etykietaStatusówFrame, text="Aktywna", font=("Helvetica", 8), fg="Green", justify="left", bd=0, relief="flat", highlightthickness=0)
statusWindy.grid(row=0,column=1, padx=10, pady=10, sticky="w")
etykietaStatusDrzwi = tk.Label(etykietaStatusówFrame, text="Status drzwi:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatusDrzwi.grid(row=1,column=0, padx=10, pady=10, sticky="w")
statusDrzwi = tk.Label(etykietaStatusówFrame, text="Aktywne", font=("Helvetica", 8), fg="Green", justify="left", bd=0, relief="flat", highlightthickness=0)
statusDrzwi.grid(row=1,column=1, padx=10, pady=10, sticky="w")
etykietaTrybPracy = tk.Label(etykietaStatusówFrame, text="Tryb pracy:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaTrybPracy.grid(row=2,column=0, padx=10, pady=10, sticky="w")
trybPracy = tk.Label(etykietaStatusówFrame, text="Standardowy", font=("Helvetica", 8), fg="Green", justify="left", bd=0, relief="flat", highlightthickness=0)
trybPracy.grid(row=2,column=1, padx=10, pady=10, sticky="w")
etykietaObciążenia = tk.Label(etykietaStatusówFrame, text="Obciążenie:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaObciążenia.grid(row=3,column=0, padx=10, pady=10, sticky="w")
obciążenie = tk.Label(etykietaStatusówFrame, text="50 % (400/800)", font=("Helvetica", 8), fg="Orange", justify="left", bd=0, relief="flat", highlightthickness=0)
obciążenie.grid(row=3,column=1, padx=10, pady=10, sticky="w")
etykietaWspółczynnikZużycia = tk.Label(etykietaStatusówFrame, text="Indeks zużycia", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaWspółczynnikZużycia.grid(row=4,column=0, padx=10, pady=10, sticky="w")
współczynnikZużycia = tk.Label(etykietaStatusówFrame, text="0,74", font=("Helvetica", 8), fg="Red", justify="left", bd=0, relief="flat", highlightthickness=0)
współczynnikZużycia.grid(row=4,column=1, padx=10, pady=10, sticky="w")
etykietaPrędkościJazdy = tk.Label(etykietaStatusówFrame, text="Prędkość windy", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaPrędkościJazdy.grid(row=5,column=0, padx=10, pady=10, sticky="w")
prędkośćJazdy = tk.Label(etykietaStatusówFrame, text="2 m/s", font=("Helvetica", 8), fg="Green", justify="left", bd=0, relief="flat", highlightthickness=0)
prędkośćJazdy.grid(row=5,column=1, padx=10, pady=10, sticky="w")
etykietaDatySerwisu = tk.Label(etykietaStatusówFrame, text="Ostatni Serwis", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaDatySerwisu.grid(row=6,column=0, padx=10, pady=10, sticky="w")
dataSerwisu = tk.Label(etykietaStatusówFrame, text="01-01-2025", font=("Helvetica", 8), fg="Green", justify="left", bd=0, relief="flat", highlightthickness=0)
dataSerwisu.grid(row=6,column=1, padx=10, pady=10, sticky="w")

NumeracjaSzybuWindyFrame = tk.LabelFrame(etykietaSzybuFrame, bd=0, relief="flat", highlightthickness=0)
NumeracjaSzybuWindyFrame.grid(row=0, column=0, padx=2, pady=10)
SzybWindyFrame = tk.LabelFrame(etykietaSzybuFrame, bd=1, relief="ridge", highlightbackground="black", highlightcolor="black", highlightthickness=1)
SzybWindyFrame.grid(row=0, column=1, padx=0, pady=10)

for piętro in wielkośćSzybu: # Tworzenie etykiet dla każdego piętra 
    numerPiętraLabel = tk.Label(NumeracjaSzybuWindyFrame, text=f"{piętro}", width=3, height=2, bd=0, relief="flat", highlightthickness=0)
    numerPiętraLabel.grid(row=(wielkośćSzybu[-1] - wielkośćSzybu[piętro]), column=0)
    etykietaPiętra = tk.Label(SzybWindyFrame, width=3, height=2, bg="lightgrey")
    etykietaPiętra.grid(row=(wielkośćSzybu[-1] - wielkośćSzybu[piętro]), column=0)
    etykietaPiętra.config(width=3, height=2, bg="lightgrey", bd=0, relief="flat")
    etykietyPieter.append(etykietaPiętra)

#ramka dla panelu windy
panelWindyFrame = tk.LabelFrame(poziom1, text="Panel Windy", bd=2, relief="groove", width=220, height=450, labelanchor="n")
panelWindyFrame.grid(row=0, column=1, padx=10, pady=10, sticky="w")
panelWindyFrame.grid_propagate(False)

#ramka dla przycisków windy
panelprzyciskówWindyFrame = tk.LabelFrame(panelWindyFrame, text="Przyciski", bd=2, relief="groove", labelanchor="n")
panelprzyciskówWindyFrame.grid(row=0, column=0, padx=10, pady=10)

#ramka dla ekranu windy
panelwyświetlaczaWindyFrame = tk.LabelFrame(panelWindyFrame, text="Ekran Windy", bd=2, relief="groove", labelanchor="n")
panelwyświetlaczaWindyFrame.grid(row=0, column=1, padx=10, pady=10)

for piętro in wielkośćSzybu: # Tworzenie przycisków dla każdego piętra
    if (wielkośćSzybu[piętro] + 1) % 2 !=0: # Podział przycisków na dwie kolumny
        numerKolumny = 0
    else:
        numerKolumny = 1
    numerWiersza = (wielkośćSzybu[-1] - wielkośćSzybu[piętro])  // 2
    przyciskWyboruPiętra = tk.Button(panelprzyciskówWindyFrame, text=f"{piętro}", width=3, height=1) # command=lambda p=piętro: wskażPiętro(p, 1, 2))
    przyciskWyboruPiętra.grid(row=numerWiersza, column=numerKolumny, padx=5, pady=5)  # Użycie siatki do rozmieszczenia przycisków
    etykietyStanuWyboruPietra.append(przyciskWyboruPiętra)

przyciskOtwórzDrzwi = tk.Button(panelprzyciskówWindyFrame, text="<|>", width=3, height=1, justify="center")# command=lambda p=1: dodajPolecenieDrzwi(p))
przyciskOtwórzDrzwi.grid(row=6, column=0, padx=5, pady=30)
przyciskZamknijDrzwi = tk.Button(panelprzyciskówWindyFrame, text=">|<", width=3, height=1, justify="center")# command=lambda p=0: dodajPolecenieDrzwi(p))
przyciskZamknijDrzwi.grid(row=6, column=1, padx=5, pady=30)

#wyświetlacze ekranu windy
wyświetlaczKierunkuJazdy = tk.Label(panelwyświetlaczaWindyFrame, width=3, font=("Helvetica", 24), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczKierunkuJazdy.grid(row=0,column=0, padx=10)

wyświetlaczPiętra = tk.Label(panelwyświetlaczaWindyFrame, width=3, font=("Helvetica", 24), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczPiętra.grid(row=1,column=0, padx=10)

wyświetlaczPracyDrzwi = tk.Label(panelwyświetlaczaWindyFrame, width=5, font=("Helvetica", 16), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczPracyDrzwi.grid(row=2,column=0, padx=10)

#ramka dla panelu pięter
panelSterowaniaPiętraFrame = tk.LabelFrame(poziom1, text="Panel pięter", bd=2, relief="groove", width=300, height=450, labelanchor="n")
panelSterowaniaPiętraFrame.grid(row=0, column=2, padx=10, pady=10, sticky="w")
panelSterowaniaPiętraFrame.grid_propagate(False)

#ramka dla wyświetlaczy pięter
wyświetlaczPiętraFrame = tk.LabelFrame(panelSterowaniaPiętraFrame, text="Ekran piętra", bd=2, relief="groove", labelanchor="n")
wyświetlaczPiętraFrame.grid(row=0, column=0, padx=10, pady=10)

wyświetlaczPiętraDlaPiętra = tk.Label(wyświetlaczPiętraFrame, width=3, font=("Helvetica", 24), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczPiętraDlaPiętra.grid(row=0,column=0)

wyświetlaczKierunkuJazdyDlaPiętra = tk.Label(wyświetlaczPiętraFrame, width=3, font=("Helvetica", 24), bg="#8B0000", fg="#FF0000", justify="center", relief="sunken")
wyświetlaczKierunkuJazdyDlaPiętra.grid(row=0,column=1)

#ramka dla przycisków pięter
panelprzyciskówPiętraFrame = tk.LabelFrame(panelSterowaniaPiętraFrame, text="Przyciski dla pięter", bd=2, relief="groove", labelanchor="n")
panelprzyciskówPiętraFrame.grid(row=1, column=0, padx=10, pady=10)

for piętro in wielkośćSzybu: # Tworzenie przycisków dla każdego piętra
    przyciskPiętraFrame = tk.LabelFrame(panelprzyciskówPiętraFrame, text=f"{piętro}",width=45, height=90, bd=2, relief="groove", labelanchor="n")
    przyciskPiętraFrame.grid(row=numerWiersza, column=numerKolumny, padx=5, pady=5)
    przyciskPiętraFrame.grid_propagate(False)
    if wielkośćSzybu[piętro] < len(wielkośćSzybu) - 1:
        przyciskPrzywołaniaWindyDoGóry = tk.Button(przyciskPiętraFrame, text="↑", width=3, height=1) #command=lambda p=piętro: wskażPiętro(p, 2, 2))
        przyciskPrzywołaniaWindyDoGóry.grid(row=numerWiersza, column=numerKolumny, padx=5, pady=5, sticky="n")
        etykietyStanuPrzywołaniaPiętraDoGóry.append(przyciskPrzywołaniaWindyDoGóry)
    else:
        pass
    if wielkośćSzybu[piętro] != 0:
        przyciskPrzywołaniaWindyDoDołu = tk.Button(przyciskPiętraFrame, text="↓", width=3, height=1) #, command=lambda p=piętro: wskażPiętro(p, 3, 2)""")
        przyciskPrzywołaniaWindyDoDołu.grid(row=(numerWiersza + 1), column=numerKolumny, padx=5, pady=5, sticky="s")
        etykietyStanuPrzywołaniaPiętraDoDołu.append(przyciskPrzywołaniaWindyDoDołu)
    else:
        pass
    numerKolumny += 1
    if numerKolumny >= 5:
        numerKolumny = 0
        numerWiersza += 2

#ramka dla panelu menu
panelMenuFrame = tk.LabelFrame(poziom1, text="Menu", bd=2, relief="groove", width=300, height=450, labelanchor="n")
panelMenuFrame.grid(row=0, column=3, padx=10, pady=10, sticky="e")
panelMenuFrame.grid_propagate(False)

logi = tk.Button(panelMenuFrame, text="Logi", command=otwórzZamknijOknoLogów)
logi.grid(row=0,column=0, padx=10, pady=10, sticky="w")

#panelsymulacji podaży pasażerów
panelSymulacjiPodażyPasażerówFrame = tk.LabelFrame(poziom2, text="Panel symulacji ruchu", bd=2, relief="groove", width=1300, height=250, labelanchor="n")
panelSymulacjiPodażyPasażerówFrame.grid(row=1, column=0, padx=10, pady=0)
panelSymulacjiPodażyPasażerówFrame.grid_propagate(False)

panelKonfiguracjiSymulacji = tk.LabelFrame(panelSymulacjiPodażyPasażerówFrame, text="Konfiguracja", height=225, bd=2, relief="groove", labelanchor="n")
panelKonfiguracjiSymulacji.grid(row=0, column=0, padx=10, pady=0, sticky="n")

etykietaWłącznikaSymulacji = tk.Label(panelKonfiguracjiSymulacji, text="Włącznik:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaWłącznikaSymulacji.grid(row=0,column=0, padx=10, pady=10, sticky="w")
włącznikSymulacji = tk.Button(panelKonfiguracjiSymulacji, text="Włącz/Wyłącz", command=włączWyłączSymulacje)
włącznikSymulacji.grid(row=0,column=1, padx=10, pady=10, sticky="w")

etykietaSkaliCzęstotliwości = tk.Label(panelKonfiguracjiSymulacji, text="Częstotliwość poleceń:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaSkaliCzęstotliwości.grid(row=1,column=0, padx=10, pady=10, sticky="w")
skalaCzęstotliwości = tk.Scale(panelKonfiguracjiSymulacji, orient="horizontal", from_= 1, to=10, length=200, width=20, command=lambda q: postZmienCzestotliwosc(q))
skalaCzęstotliwości.grid(row=1,column=1, padx=10, pady=10, sticky="w")

panelStatusówSymulacji = tk.LabelFrame(panelSymulacjiPodażyPasażerówFrame, text="Status", width=225, height=225, bd=2, relief="groove", labelanchor="n")
panelStatusówSymulacji.grid(row=0, column=1, padx=10, pady=0, sticky="n")
panelStatusówSymulacji.grid_propagate(False)

etykietaStanuSymulacji = tk.Label(panelStatusówSymulacji, text="Status Symulacji:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStanuSymulacji.grid(row=0,column=0, padx=10, pady=10, sticky="w")
stanSymulacji = tk.Label(panelStatusówSymulacji, text="Nieaktywna", font=("Helvetica", 8), fg="Red", justify="left", bd=0, relief="flat", highlightthickness=0)
stanSymulacji.grid(row=0,column=1, padx=10, pady=10, sticky="w")

panelStatystykSymulacjiWindy = tk.LabelFrame(panelSymulacjiPodażyPasażerówFrame, text="Statystyki windy", width=225, height=225, bd=2, relief="groove", labelanchor="n")
panelStatystykSymulacjiWindy.grid(row=0, column=2, padx=10, pady=0, sticky='n')
panelStatystykSymulacjiWindy.grid_propagate(False)

etykietaStatystykykiPokonanePiętra = tk.Label(panelStatystykSymulacjiWindy, text="Pokonane piętra:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPokonanePiętra.grid(row=0,column=0, padx=10, pady=10, sticky="w")
statystykaPokonanePiętra = tk.Label(panelStatystykSymulacjiWindy, text=f"{statystyki['pokonane_pietra']}", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPokonanePiętra.grid(row=0,column=1, padx=10, pady=10, sticky="w")
etykietaStatystykykiPrzebytaOdległość = tk.Label(panelStatystykSymulacjiWindy, text="Przebyta odległość:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPrzebytaOdległość.grid(row=1,column=0, padx=10, pady=10, sticky="w")
statystykaPrzebytaOdległość = tk.Label(panelStatystykSymulacjiWindy, text=f"{statystyki['przebyta_odleglosc']:.2f} km", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzebytaOdległość.grid(row=1,column=1, padx=10, pady=10, sticky="w")
etykietaStatystykykiPrzystanki = tk.Label(panelStatystykSymulacjiWindy, text="Przystanki:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPrzystanki.grid(row=2,column=0, padx=10, pady=10, sticky="w")
statystykaPrzystanki = tk.Label(panelStatystykSymulacjiWindy, text=f"{statystyki['zaliczone_przystanki']}", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzystanki.grid(row=2,column=1, padx=10, pady=10, sticky="w")

panelStatystykSymulacjiPasażerów = tk.LabelFrame(panelSymulacjiPodażyPasażerówFrame, text="Statystyki pasażerów", width=225, height=225, bd=2, relief="groove", labelanchor="n")
panelStatystykSymulacjiPasażerów.grid(row=0, column=3, padx=10, pady=0)
panelStatystykSymulacjiPasażerów.grid_propagate(False)

etykietaStatystykykiPrzewiezieniPasżerowie = tk.Label(panelStatystykSymulacjiPasażerów, text="Przewiezieni pasażerowie:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPrzewiezieniPasżerowie.grid(row=0,column=0, padx=10, pady=10, sticky="w")
statystykaPrzewiezieniPasażerowie = tk.Label(panelStatystykSymulacjiPasażerów, text=f"{statystyki['przewiezieni_pasazerowie']['typ1']}", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzewiezieniPasażerowie.grid(row=0,column=1, padx=10, pady=10, sticky="w")
etykietaStatystykykiPasażerowieUnikalni = tk.Label(panelStatystykSymulacjiPasażerów, text="Unikalni pasażerowie:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPasażerowieUnikalni.grid(row=1,column=0, padx=10, pady=10, sticky="w")
statystykaPrzewiezieniPasażerowieUnikalni = tk.Label(panelStatystykSymulacjiPasażerów, text=f"{statystyki['przewiezieni_pasazerowie']['typ2']}", font=("Helvetica", 8), fg="Black", bg="Gold", justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzewiezieniPasażerowieUnikalni.grid(row=1,column=1, padx=10, pady=10, sticky="w")
etykietaStatystykykiPasażerowieUtraceni = tk.Label(panelStatystykSymulacjiPasażerów, text="Nieobsłużeni pasażerowie:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPasażerowieUtraceni.grid(row=2,column=0, padx=10, pady=10, sticky="w")
statystykaPrzewiezieniPasażerowieUtraceni = tk.Label(panelStatystykSymulacjiPasażerów, text=f"{statystyki['przewiezieni_pasazerowie']['typ3']}", font=("Helvetica", 8), fg="Black", bg="Red", justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzewiezieniPasażerowieUtraceni.grid(row=2,column=1, padx=10, pady=10, sticky="w")
etykietaStatystykykiPasażerowieOczekujący = tk.Label(panelStatystykSymulacjiPasażerów, text="Oczekujący pasażerowie:", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
etykietaStatystykykiPasażerowieOczekujący.grid(row=3,column=0, padx=10, pady=10, sticky="w")
statystykaPrzewiezieniPasażerowieOczekujący = tk.Label(panelStatystykSymulacjiPasażerów, text=f"{statystyki['liczba_oczekujacych_pasazerow']}", font=("Helvetica", 8), justify="left", bd=0, relief="flat", highlightthickness=0)
statystykaPrzewiezieniPasażerowieOczekujący.grid(row=3,column=1, padx=10, pady=10, sticky="w")

# Inicjalizacja bazy danych i wczytanie logów

#threading.Thread(target=zapiszStatystykiOkresowo, daemon=True).start()
# Uruchomienie głównej pętli aplikacji
getWielkośćSzybu()
cyklicznaAktualizacja()
aktualizujWyświetlaneStatystykiSymulacji()

root.mainloop()
