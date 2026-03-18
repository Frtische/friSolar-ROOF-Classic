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
anz_breite=None
cp60_anz=None
cp72_anz=None

def listeneintrag_cp60(glas, t:int, b:int):
    if glas is "6mm": m=1
    elif glas is "4mm": m=0
    else: return
    nr_cp60.append(partnr[0][m])
    stk_cp60.append(t * b)
    nr_cp60.append(partnr[1][m])
    stk_cp60.append(t * (b + 1))
    nr_cp60.append(partnr[2][1])  # Pressleiste
    stk_cp60.append(b + 1)
    if t != 1:
        nr_cp60.append(partnr[2][0])  # Pressleiste
        stk_cp60.append((t - 1) * (b + 1))
def listeneintrag_cp72(glas, t:int, b:int):
    if glas is "6mm": m=3
    elif glas is "4mm": m=2
    else: return
    nr_cp72.append(partnr[0][m])
    stk_cp72.append(t * b)
    nr_cp72.append(partnr[1][m])
    stk_cp72.append(t * (b + 1))
    nr_cp72.append(partnr[2][3])  # Pressleiste
    stk_cp72.append(b + 1)
    if t != 1:
        nr_cp72.append(partnr[2][2])  # Pressleiste
        stk_cp72.append((t - 1) * (b + 1))

def abweichung_klein(x: float) -> float:
    return x-int(x)

def abweichung_gross(x: float) -> float:
    return (int(x)+1)-x


def berechnen(b:float, t:float, s:float):
    global partnr, parts2, sk_mod, anz_breite, cp60_anz, cp72_anz

    for l in [nr_cp60, name_cp60, stk_cp60, nr_cp72, name_cp72, stk_cp72]: l.clear()

    anz_breite= int((b - 0.025)/1.041)
    cp60_tiefe = (t - 0.06) / 1.677
    cp72_tiefe = (t - 0.06) / 1.997
    cp60_anz = int(cp60_tiefe)
    cp72_anz = int(cp72_tiefe)

    if anz_breite<1 or cp60_tiefe<1:
        st.error("In dieser Größe ist kein System möglich. \n\nFür ein Sondersystem bitte an einen Berater wenden.")
        return
    if s >= 6.5:
        st.error("Diese Schneelast ist zu hoch für unser System!")
        return

    if abweichung_klein(cp60_tiefe)>abweichung_gross(cp60_tiefe): cp60_anz+=1

    if abweichung_klein(cp72_tiefe)>abweichung_gross(cp72_tiefe): cp72_anz+=1

    if wenig_quer: sk_mod = 1

    match s: #CP60 #Variante
        case n if n < sk_stufen[0][0]: #4mm #PUR
            listeneintrag_cp60("4mm", cp60_anz, anz_breite)

        case n if sk_stufen[0][0] <= n < sk_stufen[0][1]: #4mm #4S
            listeneintrag_cp60("4mm", cp60_anz, anz_breite)
            nr_cp60.append(parts2[0])  # Querstrebe
            stk_cp60.append(anz_breite * (cp60_anz + 1))

        case n if sk_stufen[0][2-sk_mod] <= n < sk_stufen[0][3]:  # 6mm #PUR
            listeneintrag_cp60("6mm", cp60_anz, anz_breite)

        case n if sk_stufen[0][2+sk_mod] <= n < sk_stufen[0][4]:  # 6mm #4S
            listeneintrag_cp60("6mm", cp60_anz, anz_breite)
            nr_cp60.append(parts2[0])  # Querstrebe
            stk_cp60.append(anz_breite * (cp60_anz + 1))

        case n if sk_stufen[0][1] <= n < sk_stufen[0][2]: #4mm #4S+
            listeneintrag_cp60("4mm", cp60_anz, anz_breite)
            nr_cp60.append(parts2[0])  # Querstrebe
            stk_cp60.append(anz_breite * (2 * cp60_anz + 1))

        case n if sk_stufen[0][4] <= n < sk_stufen[0][5]: #6mm #4S+
            listeneintrag_cp60("6mm", cp60_anz, anz_breite)
            nr_cp60.append(parts2[0])  # Querstrebe
            stk_cp60.append(anz_breite * (2 * cp60_anz + 1))

    match s: #CP72 #Variante
        case n if n < sk_stufen[1][0]:  # 4mm #PUR
            listeneintrag_cp72("4mm", cp72_anz, anz_breite)

        case n if sk_stufen[1][0] <= n < sk_stufen[1][1]:  # 4mm #4S
            listeneintrag_cp72("4mm", cp72_anz, anz_breite)
            nr_cp72.append(parts2[0])  # Querstrebe
            stk_cp72.append(anz_breite * (cp72_anz + 1))

        case n if sk_stufen[1][2 - sk_mod] <= n < sk_stufen[1][3]:  # 6mm #PUR
            listeneintrag_cp72("6mm", cp72_anz, anz_breite)

        case n if sk_stufen[1][2 + sk_mod] <= n < sk_stufen[1][4]:  # 6mm #4S
            listeneintrag_cp72("6mm", cp72_anz, anz_breite)
            nr_cp72.append(parts2[0])  # Querstrebe
            stk_cp72.append(anz_breite * (cp72_anz + 1))

        case n if sk_stufen[1][1] <= n < sk_stufen[1][2]:  # 4mm #4S+
            listeneintrag_cp72("4mm", cp72_anz, anz_breite)
            nr_cp72.append(parts2[0])  # Querstrebe
            stk_cp72.append(anz_breite * (2 * cp72_anz + 1))

        case n if sk_stufen[1][4] <= n < sk_stufen[1][5]:  # 6mm #4S+
            listeneintrag_cp72("6mm", cp72_anz, anz_breite)
            nr_cp72.append(parts2[0])  # Querstrebe
            stk_cp72.append(anz_breite * (2 * cp72_anz + 1))

    for number in nr_cp60:
        partname=namedict.get(number)
        if partname:
            name_cp60.append(partname)

    for number in nr_cp72:
        partname=namedict.get(number)
        if partname:
            name_cp72.append(partname)

    st.success("Ergebnisse im nächsten Reiter abrufbar")

nr_cp60 = []
name_cp60=[]
stk_cp60=[]
nr_cp72 = []
name_cp72=[]
stk_cp72=[]

#Graphisches Interface
st.set_page_config(layout="wide")
st.title("friSolar PV ROOF kalkulator")
ein, aus = st.tabs(["Eingabe","Stückliste"])

#Input
with ein:
    breite=st.number_input("Breite des Carports eingeben [m]:", min_value=0.0, format="%.2f")
    tiefe = st.number_input("Tiefe des Carports eingeben [m]:", min_value=0.0, format="%.2f")

    skl, skr = st.columns([6,1])
    with skl:
        sk=st.number_input("Schneelast 'sk' laut E-Hora eingeben [kN/m²]:", min_value=0.0, format="%.1f")
    with skr:
        st.markdown('<div style="padding-top: 28px;"></div>', unsafe_allow_html=True)
        st.link_button("E-Hora","https://hora.gv.at/#/cschneelast/bgrau/a-/@47.72463,13.50823,8z")

    wenig_quer = st.checkbox("möglichst wenige Querstreben verwenden", value=False)

    if st.button("Berechnen"):
        berechnen(breite, tiefe, sk)

with aus:
    col_cp60, col_cp72 = st.columns(2, gap="large", border=True)
    with col_cp60:
        st.subheader("Stückliste für CP60 Variante")
        df_cp60 = pd.DataFrame({
            "Artikel-Nr.": nr_cp60,
            "Produktname": name_cp60,
            "Anzahl": stk_cp60
            })

        st.dataframe(df_cp60, use_container_width=True)
        if cp60_anz: st.success(f"Die fertigen Abmessungen mit den CP60 Modulen sind: \n\n{round(cp60_anz * 1.677 + 0.025, 3)}m x {round(anz_breite * 1.041 + 0.06, 3)}m")


    with col_cp72:
        st.subheader("Stückliste für CP72 Variante")
        df_cp72 = pd.DataFrame({
            "Artikel-Nr.": nr_cp72,
            "Produktname": name_cp72,
            "Anzahl": stk_cp72
            })

        st.dataframe(df_cp72, use_container_width=True)
        if cp72_anz: st.success(f"Die fertigen Abmessungen mit den CP72 Modulen sind: \n\n{round(cp72_anz * 1.997 + 0.025, 3)}m x {round(anz_breite * 1.041 + 0.06, 3)}m")

    def to_excel(df1, df2):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df1.to_excel(writer, index=False, sheet_name="Variante mit CP60")
            df2.to_excel(writer, index=False, sheet_name="Variante mit CP72")
        return output.getvalue()

    excel_data = to_excel(df_cp60, df_cp72)

    st.download_button(
        label="📥 Tabellen als Excel herunterladen",
        data=excel_data,
        file_name='Carport Stückliste.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        on_click="ignore"
    )