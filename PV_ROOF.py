import streamlit as st
import pandas as pd
from io import BytesIO

partnr = [["1501816", "1501813", "1501817", "1501814"],
         ["1502360", "1502361", "1502362", "1502363"],
         ["1502364", "1502365", "1502366", "1502367"]]
parts2= ["1502667"]
namedict={
    "1501816":"CP60-4",
    "1501813":"CP60-6",
    "1501817":"CP72-4",
    "1501814":"CP72-6",
    "1502360":"Keilset M8",
    "1502361":"Keilset M12",
    "1502362":"Keilset L8",
    "1502363":"Keilset L12",
    "1502364":"Pressleiste - 1680mm",
    "1502365":"Pressleiste - 1712mm",
    "1502366":"Pressleiste - 2000mm",
    "1502367":"Pressleiste - 2032mm",
    "1502667": "Querstrebe"
}
sk_stufen=[(0.7, 1.6, 3.8, 2.5, 4.2, 6.5), #CP60
           (0.7, 1.35, 3.5, 2.5, 3.7, 6.0)] #CP72
sk_mod = 0

def listeneintrag(m:int, t:int, b:int):
    nr.append(partnr[0][m])
    anz.append(t * b)
    nr.append(partnr[1][m])
    anz.append(t * (b + 1))
    if m<=1:
        pl=0
    else:
        pl=2
    nr.append(partnr[2][pl+1])  # Pressleiste
    anz.append(b + 1)
    if t != 1:
        nr.append(partnr[2][pl])  # Pressleiste
        anz.append((t - 1) * (b + 1))

def abweichung_klein(x: float) -> float:
    return x-int(x)

def abweichung_groß(x: float) -> float:
    return (int(x)+1)-x

def berechnen(b:float, t:float, s:float):
    global partnr
    global parts2
    global sk_mod

    name.clear()
    anz.clear()
    nr.clear()

    anz_breite= int((b - 0.025)/1.041)
    cp60_anz_tiefe = (t - 0.06) / 1.677
    cp72_anz_tiefe = (t - 0.06) / 1.997

    if anz_breite<1 or cp60_anz_tiefe<1:
        st.error("In dieser Größe ist kein System möglich. \n\nFür ein Sondersystem bitte an einen Berater wenden.")
        return

    if abweichung_klein(cp72_anz_tiefe)>=abweichung_klein(cp60_anz_tiefe):
        anz_tiefe=int(cp60_anz_tiefe)
        sk_wahl=0
        pv = 0
        st.success(f"Die fertigen Abmessungen ihres Carports sind: \n\n{round(anz_tiefe * 1.677 + 0.025,3)}m x {round(anz_breite * 1.041 + 0.06,3)}m")

    elif abweichung_klein(cp72_anz_tiefe)<abweichung_klein(cp60_anz_tiefe):
        anz_tiefe = int(cp72_anz_tiefe)
        sk_wahl=1
        pv =2
        st.success(f"Die fertigen Abmessungen ihres Carports sind: \n\n{round(anz_tiefe * 1.997 + 0.025,3)}m x {round(anz_breite * 1.041 + 0.06,3)}m")

    if wenig_quer:
        sk_mod = 1

    match s:
        case n if n < sk_stufen[sk_wahl][0]: #4mm #PUR
            listeneintrag(pv, anz_tiefe, anz_breite)

        case n if sk_stufen[sk_wahl][0] <= n < sk_stufen[sk_wahl][1]: #4mm #4S
            listeneintrag(pv, anz_tiefe, anz_breite)
            nr.append(parts2[0])  # Querstrebe
            anz.append(anz_breite * (anz_tiefe + 1))

        case n if sk_stufen[sk_wahl][2-sk_mod] <= n < sk_stufen[sk_wahl][3]:  # 6mm #PUR
            listeneintrag(pv + 1, anz_tiefe, anz_breite)

        case n if sk_stufen[sk_wahl][2+sk_mod] <= n < sk_stufen[sk_wahl][4]:  # 6mm #4S
            listeneintrag(pv + 1, anz_tiefe, anz_breite)
            nr.append(parts2[0])  # Querstrebe
            anz.append(anz_breite * (anz_tiefe + 1))

        case n if sk_stufen[sk_wahl][1] <= n < sk_stufen[sk_wahl][2]: #4mm #4S+
            listeneintrag(pv, anz_tiefe, anz_breite)
            nr.append(parts2[0])  # Querstrebe
            anz.append(anz_breite * (2 * anz_tiefe + 1))

        case n if sk_stufen[sk_wahl][4] <= n < sk_stufen[sk_wahl][5]: #6mm #4S+
            listeneintrag(pv+1, anz_tiefe, anz_breite)
            nr.append(parts2[0])  # Querstrebe
            anz.append(anz_breite * (2 * anz_tiefe + 1))

        case n if n > 6.5:
            st.error("Diese Schneelast ist zu hoch für unser System!")
            return

        case _:
            anz_tiefe = int(cp60_anz_tiefe)
            listeneintrag(1, anz_tiefe, anz_breite)
            nr.append(parts2[0])  # Querstrebe
            anz.append(anz_breite * (2 * anz_tiefe + 1))

    for number in nr:
        partname=namedict.get(number)
        if partname:
            name.append(partname)

nr = []
name=[]
anz=[]

#Graphisches Interface
st.title("friSolar PV ROOF kalkulator")
ein, aus = st.tabs(["Eingabe","Stückliste"])

#Input
with (ein):
    breite=st.number_input("Breite des Carports eingeben [m]:", min_value=0.0, format="%.2f")
    tiefe = st.number_input("Tiefe des Carports eingeben [m]:", min_value=0.0, format="%.2f")

    skl, skr = st.columns([6,1])
    with skl:
        sk=st.number_input("Schneelast laut E-Hora eingeben [kN/m²]:", min_value=0.0, format="%.1f")
    with skr:
        st.markdown('<div style="padding-top: 28px;"></div>', unsafe_allow_html=True)
        st.link_button("E-Hora","https://hora.gv.at/#/cschneelast/bgrau/a-/@47.72463,13.50823,8z")

    wenig_quer = st.checkbox("möglichst wenige Querstreben verwenden", value=False)

    if st.button("Berechnen"):
        berechnen(breite, tiefe, sk)

with aus:
    df = pd.DataFrame({
        "Artikel-Nr.": nr,
        "Produktname": name,
        "Anzahl": anz
        })

    st.dataframe(df, use_container_width=True)

    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Stückliste')
        return output.getvalue()

    excel_data = to_excel(df)

    st.download_button(
        label="📥 Tabelle als Excel herunterladen",
        data=excel_data,
        file_name='Carport Stückliste.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
