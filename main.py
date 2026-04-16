import argparse
from pathlib import Path


SBOX_1 = [
    "101", "010", "001", "110", "011", "100", "111", "000",
    "001", "100", "110", "010", "000", "111", "101", "011"
]
SBOX_2 = [
    "100", "000", "110", "101", "111", "001", "011", "010",
    "101", "011", "000", "111", "110", "010", "001", "100"
]
PERMUTACJA = "01323245"
ROZMIAR_BLOKU = 12
LICZBA_RUND = 8


def xor_bity(a, b):
    # tutaj licze xor dwoch ciagow bitow o tej samej dlugosci
    wynik = []
    for i in range(len(a)):
        wynik.append("0" if a[i] == b[i] else "1")
    return "".join(wynik)


def przesun_w_lewo(bity, o_ile):
    # tutaj przesuwam cyklicznie klucz w lewo
    o_ile = o_ile % len(bity)
    return bity[o_ile:] + bity[:o_ile]


def przesun_w_prawo(bity, o_ile):
    # tutaj przesuwam cyklicznie klucz w prawo
    o_ile = o_ile % len(bity)
    return bity[-o_ile:] + bity[:-o_ile]


def funkcja_f(klucz_rundy, prawa_6):
    # tutaj licze funkcje f dla mini des
    rozszerzone_8 = "".join(prawa_6[int(indeks)] for indeks in PERMUTACJA)
    po_xor = xor_bity(rozszerzone_8, klucz_rundy)
    lewa_4 = po_xor[:4]
    prawa_4 = po_xor[4:]
    return SBOX_1[int(lewa_4, 2)] + SBOX_2[int(prawa_4, 2)]


def szyfruj_blok(blok_12, klucz_8):
    # tutaj szyfruje pojedynczy blok 12 bitow
    lewa = blok_12[:6]
    prawa = blok_12[6:]

    for numer_rundy in range(1, LICZBA_RUND):
        klucz_rundy = przesun_w_lewo(klucz_8, numer_rundy)
        nowa_lewa = prawa
        nowa_prawa = xor_bity(lewa, funkcja_f(klucz_rundy, prawa))
        lewa = nowa_lewa
        prawa = nowa_prawa

    return prawa + lewa


def deszyfruj_blok(blok_12, klucz_8):
    # tutaj deszyfruje pojedynczy blok 12 bitow
    lewa = blok_12[:6]
    prawa = blok_12[6:]

    for numer_rundy in range(1, LICZBA_RUND):
        klucz_rundy = przesun_w_prawo(klucz_8, numer_rundy)
        nowa_lewa = prawa
        nowa_prawa = xor_bity(lewa, funkcja_f(klucz_rundy, prawa))
        lewa = nowa_lewa
        prawa = nowa_prawa

    return prawa + lewa


def podziel_na_bloki(ciag_bitow):
    # tutaj dziele ciag bitow na pelne bloki i koncowke
    pelna_dlugosc = (len(ciag_bitow) // ROZMIAR_BLOKU) * ROZMIAR_BLOKU
    bloki = []
    for i in range(0, pelna_dlugosc, ROZMIAR_BLOKU):
        bloki.append(ciag_bitow[i:i + ROZMIAR_BLOKU])
    koncowka = ciag_bitow[pelna_dlugosc:]
    return bloki, koncowka


def szyfruj_ecb(ciag_bitow, klucz_8):
    # tutaj szyfruje trybem ecb
    bloki, koncowka = podziel_na_bloki(ciag_bitow)
    wynik = []
    for blok in bloki:
        wynik.append(szyfruj_blok(blok, klucz_8))
    return "".join(wynik) + koncowka


def deszyfruj_ecb(ciag_bitow, klucz_8):
    # tutaj deszyfruje trybem ecb
    bloki, koncowka = podziel_na_bloki(ciag_bitow)
    wynik = []
    for blok in bloki:
        wynik.append(deszyfruj_blok(blok, klucz_8))
    return "".join(wynik) + koncowka


def szyfruj_cbc(ciag_bitow, klucz_8, iv_12):
    # tutaj szyfruje trybem cbc
    bloki, koncowka = podziel_na_bloki(ciag_bitow)
    poprzedni = iv_12
    wynik = []

    for blok in bloki:
        wejscie_rundy = xor_bity(blok, poprzedni)
        szyfrogram = szyfruj_blok(wejscie_rundy, klucz_8)
        wynik.append(szyfrogram)
        poprzedni = szyfrogram

    return "".join(wynik) + koncowka


def deszyfruj_cbc(ciag_bitow, klucz_8, iv_12):
    # tutaj deszyfruje trybem cbc
    bloki, koncowka = podziel_na_bloki(ciag_bitow)
    poprzedni = iv_12
    wynik = []

    for blok in bloki:
        po_des = deszyfruj_blok(blok, klucz_8)
        jawny = xor_bity(po_des, poprzedni)
        wynik.append(jawny)
        poprzedni = blok

    return "".join(wynik) + koncowka


def szyfruj_ctr(ciag_bitow, klucz_8, licznik_start=0):
    # tutaj szyfruje i deszyfruje trybem ctr
    bloki, koncowka = podziel_na_bloki(ciag_bitow)
    wynik = []
    licznik = licznik_start

    for blok in bloki:
        blok_licznika = format(licznik % (2 ** ROZMIAR_BLOKU), "012b")
        strumien_klucza = szyfruj_blok(blok_licznika, klucz_8)
        wynik.append(xor_bity(blok, strumien_klucza))
        licznik += 1

    return "".join(wynik) + koncowka


def zmien_jeden_bit(ciag_bitow, indeks_bitu):
    # tutaj zmieniam jeden wybrany bit
    lista = list(ciag_bitow)
    lista[indeks_bitu] = "1" if lista[indeks_bitu] == "0" else "0"
    return "".join(lista)


def bajty_na_bity(dane):
    # tutaj zamieniam bajty na ciag 0 i 1
    return "".join(format(bajt, "08b") for bajt in dane)


def bity_na_bajty(ciag_bitow):
    # tutaj zamieniam ciag 0 i 1 na bajty
    wynik = bytearray()
    for i in range(0, len(ciag_bitow), 8):
        wynik.append(int(ciag_bitow[i:i + 8], 2))
    return bytes(wynik)


def wczytaj_pnm_binarne(sciezka):
    # tutaj odczytuje p4 p5 p6 i oddzielam naglowek od pikseli
    surowe = Path(sciezka).read_bytes()
    if len(surowe) < 2 or surowe[0:1] != b"P":
        return None

    magic = surowe[0:2]
    if magic not in (b"P4", b"P5", b"P6"):
        return None

    i = 2
    tokeny = []
    ile_tokenow = 2 if magic == b"P4" else 3

    while len(tokeny) < ile_tokenow:
        while i < len(surowe) and surowe[i] in b" \t\r\n":
            i += 1

        if i < len(surowe) and surowe[i] == 35:
            while i < len(surowe) and surowe[i] != 10:
                i += 1
            continue

        start = i
        while i < len(surowe) and surowe[i] not in b" \t\r\n":
            i += 1
        tokeny.append(surowe[start:i])

    while i < len(surowe) and surowe[i] in b" \t\r\n":
        i += 1

    naglowek = surowe[:i]
    piksele = surowe[i:]
    return ("pnm", naglowek, piksele, Path(sciezka).suffix.lower())


def wczytaj_obraz(sciezka):
    # tutaj obsluguję pnm lub png jpg przez pillow
    pnm = wczytaj_pnm_binarne(sciezka)
    if pnm is not None:
        return pnm

    try:
        from PIL import Image
    except ImportError as blad:
        raise RuntimeError("brak PIL. zainstaluj pillow dla swojego pythona") from blad

    obraz = Image.open(sciezka)
    if obraz.mode not in ("L", "RGB"):
        obraz = obraz.convert("RGB")

    piksele = obraz.tobytes()
    return ("pil", obraz.mode, obraz.size, piksele, Path(sciezka).suffix.lower())


def zapisz_obraz(meta, sciezka, nowe_piksele):
    # tutaj zapisuje obraz po podmianie danych pikseli
    if meta[0] == "pnm":
        _, naglowek, _, _ = meta
        Path(sciezka).write_bytes(naglowek + nowe_piksele)
        return

    from PIL import Image
    _, tryb, rozmiar, _, _ = meta
    obraz = Image.frombytes(tryb, rozmiar, nowe_piksele)
    obraz.save(sciezka)


def policz_roznice_bitow(bity_a, bity_b):
    # tutaj licze ile bitow jest roznych miedzy dwoma ciagami
    return sum(1 for a, b in zip(bity_a, bity_b) if a != b)


def sprawdz_format_bitowy(wartosc, dlugosc, nazwa):
    # tutaj sprawdzam czy klucz i iv to poprawne 0 i 1
    if len(wartosc) != dlugosc:
        raise ValueError(f"{nazwa} musi miec dlugosc {dlugosc}")
    if any(znak not in "01" for znak in wartosc):
        raise ValueError(f"{nazwa} musi miec tylko znaki 0 i 1")


def main():
    # tutaj pobieram argumenty i uruchamiam caly eksperyment
    parser = argparse.ArgumentParser(description="MiniDES obrazow w ECB CBC CTR")
    parser.add_argument("--wejscie", "--input", dest="wejscie", required=True, help="sciezka obrazu")
    parser.add_argument("--klucz", "--key", dest="klucz", required=True, help="8 bitow np 10101010")
    parser.add_argument("--iv", dest="iv", default="000000000000", help="12 bitow dla cbc")
    parser.add_argument("--wyjscie", "--outdir", dest="wyjscie", default=".", help="folder wynikowy")
    args = parser.parse_args()

    sprawdz_format_bitowy(args.klucz, 8, "klucz")
    sprawdz_format_bitowy(args.iv, 12, "iv")

    meta = wczytaj_obraz(args.wejscie)
    if meta[0] == "pnm":
        _, _, piksele, rozszerzenie = meta
    else:
        _, _, _, piksele, rozszerzenie = meta

    bity_jawne = bajty_na_bity(piksele)
    katalog_wyj = Path(args.wyjscie)
    katalog_wyj.mkdir(parents=True, exist_ok=True)
    nazwa = Path(args.wejscie).stem

    raport = []
    raport.append("WNIOSKI BIT-FLIPPING")
    raport.append("")
    raport.append("ECB: po zmianie 1 bitu szyfrogramu uszkadza sie tylko jeden blok.")
    raport.append("CBC: po zmianie 1 bitu szyfrogramu blad propaguje sie na dwa bloki.")
    raport.append("CTR: po zmianie 1 bitu szyfrogramu uszkadza sie dokladnie 1 bit danych jawnych.")
    raport.append("")

    for tryb in ("ecb", "cbc", "ctr"):
        if tryb == "ecb":
            bity_szyfru = szyfruj_ecb(bity_jawne, args.klucz)
            bity_po_ataku = zmien_jeden_bit(bity_szyfru, len(bity_szyfru) // 2)
            bity_po_des = deszyfruj_ecb(bity_po_ataku, args.klucz)
        elif tryb == "cbc":
            bity_szyfru = szyfruj_cbc(bity_jawne, args.klucz, args.iv)
            bity_po_ataku = zmien_jeden_bit(bity_szyfru, len(bity_szyfru) // 2)
            bity_po_des = deszyfruj_cbc(bity_po_ataku, args.klucz, args.iv)
        else:
            bity_szyfru = szyfruj_ctr(bity_jawne, args.klucz, 0)
            bity_po_ataku = zmien_jeden_bit(bity_szyfru, len(bity_szyfru) // 2)
            bity_po_des = szyfruj_ctr(bity_po_ataku, args.klucz, 0)

        plik_szyfr = katalog_wyj / f"{nazwa}_{tryb}_zaszyfrowany{rozszerzenie}"
        plik_atak = katalog_wyj / f"{nazwa}_{tryb}_atak_szyfrogram{rozszerzenie}"
        plik_des = katalog_wyj / f"{nazwa}_{tryb}_po_ataku_deszyfrowany{rozszerzenie}"

        zapisz_obraz(meta, plik_szyfr, bity_na_bajty(bity_szyfru))
        zapisz_obraz(meta, plik_atak, bity_na_bajty(bity_po_ataku))
        zapisz_obraz(meta, plik_des, bity_na_bajty(bity_po_des))

        roznica_jawnych = policz_roznice_bitow(bity_jawne, bity_po_des)
        roznica_szyfru = policz_roznice_bitow(bity_szyfru, bity_po_ataku)
        raport.append(f"{tryb.upper()}: roznica bitow szyfrogramu={roznica_szyfru}, roznica bitow po deszyfrowaniu={roznica_jawnych}")

        print(f"[{tryb.upper()}] zapisane:")
        print(f"  {plik_szyfr}")
        print(f"  {plik_atak}")
        print(f"  {plik_des}")

    (katalog_wyj / "raport_bitflipping.txt").write_text("\n".join(raport), encoding="utf-8")
    print(f"\nZapisalem raport: {katalog_wyj / 'raport_bitflipping.txt'}")


if __name__ == "__main__":
    main()
    raise SystemExit(0)
