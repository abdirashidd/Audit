"""
ALSHAMS SOLAR — Energo-Audit Streamlit Web Ilovasi
Barcha 338 shablon o'zgaruvchisini to'liq qamrab oladi.
Streamlit Cloud uchun optimizlangan.
"""

import io
import json
import zlib
import base64
import datetime
import os
import traceback
import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from PIL import Image

# Matplotlib — xavfsiz import
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

# ═══════════════════════════════════════════════════════════════════════════════
#                             KONSTANTALAR
# ═══════════════════════════════════════════════════════════════════════════════

MONTHS_UZ = [
    "Yanvar","Fevral","Mart","Aprel","May","Iyun",
    "Iyul","Avgust","Sentabr","Oktabr","Noyabr","Dekabr",
]

ELEKTR_TARIF   = 450
GAZ_TARIF      = 650
GAZ_KVT        = 9.3
CO2_PER_KVT    = 0.0006

NARX_DEVOR     = 320_000
NARX_OYNA      = 1_400_000
NARX_SHIFT     = 160_000
NARX_POL       = 130_000

SOLAR_PANEL_MLN  = 1.80
SOLAR_INVERT_MLN = 0.90
SOLAR_METAL_MLN  = 0.40
SOLAR_KABEL_MLN  = 0.30
SOLAR_ORNAT_MLN  = 0.50
SUN_HOURS        = 5.2
SOLAR_EFF        = 0.80

DEVICES = {
    "lampa":  ("Lampalar",                   10,    6),
    "kond":   ("Konditsionerlar",          1500,    8),
    "boyler": ("Elektr boylerlar",         2000,    2),
    "muzlat": ("Muzlatgichlar",             180,   24),
    "tv":     ("Televizorlar",               80,    5),
    "dazmol": ("Dazmollar",               2200,    1),
    "kir":    ("Kir yuvish mashinalari",  2000,    1),
    "pech":   ("Elektr pechlari",         1500,    2),
    "nasos":  ("Nasoslar",                 750,    2),
}

ROOM_SLOTS = {1:4, 2:4, 3:1, 4:4, 5:5, 6:5, 7:5, 8:8, 9:5, 10:8}

def _f(val): return str(round(float(val), 2)).replace(".", ",")
def _get_arr(d, key, default):
    v = d.get(key, default)
    if not isinstance(v, list) or len(v) != 12: return list(default)
    return [int(x) for x in v]

# ═══════════════════════════════════════════════════════════════════════════════
#                          SAHIFA SOZLAMALARI
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="ALSHAMS SOLAR | Energo-Audit", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #002060 0%, #004080 100%);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .stButton > button {
        background-color: #004080;
        color: white;
        border-radius: 8px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

parsed_data = {}
if "audit_data" in st.query_params:
    try:
        compressed   = base64.urlsafe_b64decode(st.query_params["audit_data"].encode())
        parsed_data  = json.loads(zlib.decompress(compressed).decode("utf-8"))
        st.success("✅ Telegram botdan ma'lumotlar yuklandi!")
    except Exception as e:
        st.error(f"❌ Ma'lumotlarni ochishda xato: {e}")

st.markdown("<div class='main-header'><h1 style='margin:0'>⚡ ALSHAMS SOLAR — Energo-Audit</h1></div>", unsafe_allow_html=True)

with st.form(key="audit_form", border=False):
    st.markdown("### 📋 I. Umumiy ma'lumotlar")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Mijoz va obyekt**")
        mijoz_ismi = st.text_input("Xo'jayin (F.I.O):", value=parsed_data.get("mijoz_ismi", "Esemuratov Aralbay"))
        manzil     = st.text_input("Manzil:", value=parsed_data.get("manzil", "Nukus shahri"))
        qurilgan_yili    = st.text_input("Qurilgan yili:", value=str(parsed_data.get("qurilgan_yili", "1990")))
        oxirgi_remont    = st.text_input("Oxirgi remont yili:", value=str(parsed_data.get("oxirgi_remont", "2015")))
    with c2:
        st.markdown("**Shartnoma**")
        shartnoma_raqami = st.text_input("Xulosa raqami (№):", value=parsed_data.get("shartnoma_raqami", "12-A"))
        lot_raqami       = st.text_input("Lot raqami:", value=parsed_data.get("lot_raqami", "2026"))
        kenglik          = st.text_input("Kenglik:", value=str(parsed_data.get("kenglik", "42.46")))
        uzunlik          = st.text_input("Uzunlik:", value=str(parsed_data.get("uzunlik", "59.60")))
    with c3:
        st.markdown("**Hisob raqamlari**")
        kadastr_raqami = st.text_input("Kadastr:", value=parsed_data.get("kadastr_raqami", ""))
        elektr_raqami  = st.text_input("Elektr:", value=parsed_data.get("elektr_raqami", ""))
        gaz_raqami     = st.text_input("Gaz:", value=parsed_data.get("gaz_raqami", ""))
        solar_kw_opt   = st.selectbox("QES (kW):", options=[3.0,5.0,10.0,15.0,20.0], index=1)

    st.markdown("---")
    st.markdown("### 🏗️ II. Binoning parametrlari")
    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("**O'lchamlar**")
        umumiy_m    = st.number_input("Maydon (m²):", value=float(parsed_data.get("umumiy_m", 120.0)), min_value=1.0, step=0.5)
        qavat_soni  = st.number_input("Qavatlar:", value=int(parsed_data.get("qavat_soni", 1)), min_value=1, step=1)
        bolimlar    = st.number_input("Xonalar:", value=int(parsed_data.get("bolimlar_soni", 3)), min_value=1, step=1)
        odam_soni   = st.number_input("Odam:", value=int(parsed_data.get("odam_soni", 4)), min_value=1, step=1)
    with c5:
        st.markdown("**Konstruksiya**")
        oyna_soni   = st.number_input("Oynalar:", value=int(parsed_data.get("oyna_soni", 5)), min_value=0, step=1)
        eshik_soni  = st.number_input("Eshiklar:", value=int(parsed_data.get("eshik_soni", 1)), min_value=0, step=1)
        lampa_soni  = st.number_input("Lampalar:", value=int(parsed_data.get("lampa_soni", 10)), min_value=0, step=1)
        kond_soni   = st.number_input("Kond:", value=int(parsed_data.get("kond_soni", 1)), min_value=0, step=1)
    with c6:
        st.markdown("**Boshqa jihozlar**")
        boyler_soni = st.number_input("Boyler:", value=int(parsed_data.get("boyler_soni", 1)), min_value=0, step=1)
        muzlat_soni = st.number_input("Muzlat:", value=int(parsed_data.get("muzlat_soni", 1)), min_value=0, step=1)
        tv_soni     = st.number_input("TV:", value=int(parsed_data.get("tv_soni", 1)), min_value=0, step=1)
        dazmol_soni = st.number_input("Dazmol:", value=int(parsed_data.get("dazmol_soni", 1)), min_value=0, step=1)
        kir_soni    = st.number_input("Kir yuvish:", value=int(parsed_data.get("kir_soni", 1)), min_value=0, step=1)
        pech_soni   = st.number_input("Pech:", value=int(parsed_data.get("pech_soni", 1)), min_value=0, step=1)
        nasos_soni  = st.number_input("Nasos:", value=int(parsed_data.get("nasos_soni", 1)), min_value=0, step=1)

    st.markdown("---")
    st.markdown("### 🌡️ III. Termografik o'lchovlar")
    ct1, ct2, ct3, ct4 = st.columns(4)
    with ct1:
        temp_1 = st.number_input("Xona 1 (°C):", value=float(parsed_data.get("temp_1", 26.3)))
        hum_1  = st.number_input("Xona 1 (%):", value=float(parsed_data.get("hum_1", 27.6)))
    with ct2:
        temp_2 = st.number_input("Xona 2 (°C):", value=float(parsed_data.get("temp_2", 21.2)))
        hum_2  = st.number_input("Xona 2 (%):", value=float(parsed_data.get("hum_2", 31.5)))
    with ct3:
        temp_3 = st.number_input("Xona 3 (°C):", value=float(parsed_data.get("temp_3", 22.0)))
        hum_3  = st.number_input("Xona 3 (%):", value=float(parsed_data.get("hum_3", 30.0)))
    with ct4:
        temp_4 = st.number_input("Xona 4 (°C):", value=float(parsed_data.get("temp_4", 23.5)))
        hum_4  = st.number_input("Xona 4 (%):", value=float(parsed_data.get("hum_4", 28.0)))

    st.markdown("---")
    st.markdown("### 📊 IV. Oylik energiya (3 yillik)")

    e_def = {"y1": _get_arr(parsed_data,"e_vals_y1",[150,160,140,130,180,220,250,240,190,150,160,170]),
             "y2": _get_arr(parsed_data,"e_vals_y2",[155,165,145,135,185,225,255,245,195,155,165,175]),
             "y3": _get_arr(parsed_data,"e_vals_y3",[160,170,150,140,190,230,260,250,200,160,170,180])}
    g_def = {"y1": _get_arr(parsed_data,"g_vals_y1",[300,280,200,100,50,20,10,15,40,120,250,350]),
             "y2": _get_arr(parsed_data,"g_vals_y2",[310,290,210,105,55,25,15,20,45,125,255,360]),
             "y3": _get_arr(parsed_data,"g_vals_y3",[320,300,220,110,60,30,20,25,50,130,260,370])}

    tab1, tab2, tab3 = st.tabs(["📅 1-Yil", "📅 2-Yil", "📅 3-Yil"])
    e_inp, g_inp = {}, {}

    for tab, yn, label in [(tab1,"y1","1-Yil"),(tab2,"y2","2-Yil"),(tab3,"y3","3-Yil")]:
        with tab:
            ce, cg = st.columns(2)
            with ce:
                st.write("**⚡ Elektr (kVt·soat)**")
                for i, m in enumerate(MONTHS_UZ):
                    e_inp[f"e_{i+1}_{yn}"] = st.number_input(f"{m}", value=e_def[yn][i], key=f"e_{i}_{yn}", step=1, min_value=0)
            with cg:
                st.write("**🔥 Gaz (m³)**")
                for i, m in enumerate(MONTHS_UZ):
                    g_inp[f"gm_{i+1}_{yn}"] = st.number_input(f"{m}", value=g_def[yn][i], key=f"g_{i}_{yn}", step=1, min_value=0)

    st.markdown("---")
    st.markdown("### 📸 V. Fotosuratlari")

    f_rooms = {}
    rc1, rc2 = st.columns(2)
    with rc1:
        for i in range(1, 6):
            f_rooms[i] = st.file_uploader(f"📷 {i}-xona:", accept_multiple_files=True, key=f"r{i}")
    with rc2:
        for i in range(6, 11):
            f_rooms[i] = st.file_uploader(f"📷 {i}-xona:", accept_multiple_files=True, key=f"r{i}")

    f_harorat = st.file_uploader("🌡️ Termografik:", accept_multiple_files=True, key="rtemp")

    st.markdown("---")
    col_btn = st.columns([1, 2, 1])[1]
    with col_btn:
        submit = st.form_submit_button("📄 WORD HUJJAT YARATISH 🚀", use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#                         HUJJAT GENERATSIYASI
# ═══════════════════════════════════════════════════════════════════════════════

if submit:
    progress = st.progress(0, text="Ishga tushirilmoqda...")
    try:
        if not os.path.exists("shablon.docx"):
            st.error("❌ shablon.docx topilmadi!")
            st.stop()

        doc = DocxTemplate("shablon.docx")
        context = {}
        now = datetime.datetime.now()
        solar_kw = float(solar_kw_opt)

        progress.progress(10, "Hisob-kitoblar...")

        # Geometriya
        devor_m  = round(umumiy_m * 1.25, 2)
        shift_m  = round(umumiy_m * 1.05, 2)
        pol_m    = round(umumiy_m * 0.95, 2)
        oyna_m   = round(oyna_soni * 1.9, 2)
        eshik_m  = round(eshik_soni * 2.1, 2)

        # Izolyatsiya
        izol_devor = round(devor_m * NARX_DEVOR / 1_000_000, 2)
        izol_oyna  = round(oyna_m * NARX_OYNA / 1_000_000, 2)
        izol_shift = round(shift_m * NARX_SHIFT / 1_000_000, 2)
        izol_pol   = round(pol_m * NARX_POL / 1_000_000, 2)
        izol_jami  = round(izol_devor + izol_oyna + izol_shift + izol_pol, 2)

        sav_devor = round(devor_m * 42.5, 1)
        sav_oyna  = round(oyna_m * 95.2, 1)
        sav_shift = round(shift_m * 38.0, 1)
        sav_pol   = round(pol_m * 18.5, 1)
        sav_total = round(sav_devor + sav_oyna + sav_shift + sav_pol, 1)

        progress.progress(20, "Solar hisob-kitoblari...")

        # Solar
        solar_panel_mln   = round(solar_kw * SOLAR_PANEL_MLN, 2)
        solar_invert_mln  = round(solar_kw * SOLAR_INVERT_MLN, 2)
        solar_metal_mln   = round(solar_kw * SOLAR_METAL_MLN, 2)
        solar_kabel_mln   = round(solar_kw * SOLAR_KABEL_MLN, 2)
        solar_ornat_mln   = round(solar_kw * SOLAR_ORNAT_MLN, 2)
        solar_jami_mln    = round(solar_panel_mln + solar_invert_mln + solar_metal_mln + solar_kabel_mln + solar_ornat_mln, 2)
        solar_jami_sum    = int(solar_jami_mln * 1_000_000)

        solar_gen_kvt     = round(solar_kw * SUN_HOURS * 365 * SOLAR_EFF)
        solar_spec_cons   = round(solar_gen_kvt / max(umumiy_m, 1), 1)
        gelio_kunlik_kvt  = round(solar_kw * SUN_HOURS * SOLAR_EFF, 1)
        gelio_kunlik_sum  = int(gelio_kunlik_kvt * ELEKTR_TARIF)
        gelio_yillik_sum  = int(solar_gen_kvt * ELEKTR_TARIF)
        gelio_q_kj        = int(solar_gen_kvt * 3600)
        gelio_oqlash      = round(solar_jami_sum / max(gelio_yillik_sum, 1), 1)
        inv_gelio         = solar_jami_mln
        inv_total         = round(izol_jami + solar_jami_mln, 2)

        progress.progress(35, "Energiya ma'lumotlari...")

        # Energiya agregatsiyasi
        e_sum = {"y1":0,"y2":0,"y3":0}
        gm_sum = {"y1":0,"y2":0,"y3":0}
        gk_sum = {"y1":0,"y2":0,"y3":0}
        j_sum = {"y1":0,"y2":0,"y3":0}

        for yn in ("y1","y2","y3"):
            for i in range(1, 13):
                e_v = int(e_inp[f"e_{i}_{yn}"])
                gm_v = int(g_inp[f"gm_{i}_{yn}"])
                gk_v = round(gm_v * GAZ_KVT, 1)
                j_v = round(e_v + gk_v, 1)
                e_sum[yn] += e_v
                gm_sum[yn] += gm_v
                gk_sum[yn] += gk_v
                j_sum[yn] += j_v
                context[f"e_{i}_{yn}"] = e_v
                context[f"gm_{i}_{yn}"] = gm_v
                context[f"gk_{i}_{yn}"] = _f(gk_v)
                context[f"j_{i}_{yn}"] = _f(j_v)

            context[f"e_yil_{yn}"] = e_sum[yn]
            context[f"e_yil_{yn}_matn"] = str(e_sum[yn])
            context[f"gm_yil_{yn}"] = gm_sum[yn]
            context[f"gk_yil_{yn}"] = round(gk_sum[yn], 1)
            context[f"gk_yil_{yn}_matn"] = _f(round(gk_sum[yn], 1))
            context[f"j_yil_{yn}"] = round(j_sum[yn], 1)
            context[f"j_yil_{yn}_matn"] = _f(round(j_sum[yn], 1))

            cost_mln = round((e_sum[yn] * ELEKTR_TARIF + gm_sum[yn] * GAZ_TARIF) / 1_000_000, 2)
            context[f"sum_y{yn[1]}"] = _f(cost_mln)
            context[f"jami_summa_{yn}"] = _f(cost_mln)
            context[f"e_summa_{yn}"] = _f(round(e_sum[yn] * ELEKTR_TARIF / 1_000_000, 2))
            context[f"g_summa_{yn}"] = _f(round(gm_sum[yn] * GAZ_TARIF / 1_000_000, 2))

            total_kvt = e_sum[yn] + gk_sum[yn]
            e_pct = round(e_sum[yn] / max(total_kvt, 1) * 100, 1)
            context[f"e_ulush_{yn}"] = _f(e_pct)
            context[f"g_ulush_{yn}"] = _f(round(100 - e_pct, 1))

        # KPIlar
        avg_j = (j_sum["y1"] + j_sum["y2"] + j_sum["y3"]) / 3
        avg_e = (e_sum["y1"] + e_sum["y2"] + e_sum["y3"]) / 3
        avg_spec = round(avg_j / max(umumiy_m, 1), 1)
        avg_co2 = round(avg_e * CO2_PER_KVT, 2)
        co2_kg = round(avg_co2 * 1000, 1)
        new_spec = round(avg_spec * 0.65, 1)
        new_co2 = round(avg_co2 * 0.5, 2)
        new_summa = round(avg_j * 0.65 * ELEKTR_TARIF / 1_000_000 / 12, 2)
        avg_jami_summa = round(avg_j * ELEKTR_TARIF / 1_000_000 / 12, 1)

        if avg_spec < 80: toifa = "A+ (Eng tejamkor)"
        elif avg_spec < 120: toifa = "A (Tejamkor)"
        elif avg_spec < 160: toifa = "B (Yaxshi)"
        elif avg_spec < 220: toifa = "C (O'rtacha)"
        elif avg_spec < 300: toifa = "D (Past)"
        else: toifa = "E (Isrofgar)"

        # Jihozlar
        dev_counts = {"lampa":lampa_soni,"kond":kond_soni,"boyler":boyler_soni,"muzlat":muzlat_soni,
                      "tv":tv_soni,"dazmol":dazmol_soni,"kir":kir_soni,"pech":pech_soni,"nasos":nasos_soni}
        jami_sutka_v = 0
        jami_oy_v = 0
        for key, (label_d, watt, hours) in DEVICES.items():
            cnt = dev_counts[key]
            sutka = round(cnt * watt * hours / 1000, 2)
            oy = round(sutka * 30, 1)
            context[f"{key}_soni"] = cnt
            context[f"{key}_sutka"] = _f(sutka)
            context[f"{key}_oy"] = _f(oy)
            jami_sutka_v += sutka
            jami_oy_v += oy

        context["jami_soni"] = sum(dev_counts.values())
        context["jami_sutka"] = _f(round(jami_sutka_v, 2))
        context["jami_oy"] = _f(round(jami_oy_v, 1))

        progress.progress(50, "Grafiklar...")

        # Grafiklar (faqat matplotlib ishsa)
        if MATPLOTLIB_OK:
            try:
                plt.style.use("default")
                fig1, ax1 = plt.subplots(figsize=(8,4.5), facecolor="white")
                yl = ["1-Yil","2-Yil","3-Yil"]
                vals = [j_sum["y1"],j_sum["y2"],j_sum["y3"]]
                colors_bar = ["#002060","#004080","#0059b3"]
                bars = ax1.bar(yl,vals,color=colors_bar,width=0.5,edgecolor="white",linewidth=1.5)
                for bar,val in zip(bars,vals):
                    ax1.text(bar.get_x()+bar.get_width()/2,bar.get_height()+max(vals)*0.01,f"{val:,.0f}",
                             ha="center",va="bottom",fontsize=10,fontweight="bold",color="#002060")
                ax1.set_title("Yillik Energiya (kVt·soat)",fontsize=12,fontweight="bold",color="#002060",pad=15)
                ax1.set_ylabel("kVt·soat",fontsize=10)
                ax1.set_ylim(0,max(vals)*1.15)
                ax1.spines[["top","right"]].set_visible(False)
                fig1.tight_layout(pad=2)
                buf1 = io.BytesIO()
                fig1.savefig(buf1,format="png",dpi=160,bbox_inches="tight")
                buf1.seek(0)
                context["diag_jami_bar"] = InlineImage(doc,buf1,width=Mm(150))
                plt.close(fig1)

                pie_colors = [["#1f77b4","#ff7f0e"],["#2ca02c","#d62728"],["#9467bd","#8c564b"]]
                for idx,(yn,year_label) in enumerate([("y1","1-Yil"),("y2","2-Yil"),("y3","3-Yil")]):
                    fig_p,ax_p = plt.subplots(figsize=(4.5,4.5),facecolor="white")
                    e_v,gk_v = e_sum[yn],gk_sum[yn]
                    total_v = e_v + gk_v
                    wedges,texts,autotexts = ax_p.pie([e_v,gk_v],labels=["Elektr","Gaz"],autopct="%1.1f%%",
                                                       colors=pie_colors[idx],startangle=90,
                                                       wedgeprops={"edgecolor":"white","linewidth":2},
                                                       textprops={"fontsize":10})
                    for at in autotexts:
                        at.set_fontsize(10)
                        at.set_fontweight("bold")
                        at.set_color("white")
                    ax_p.set_title(f"{year_label} Balansi",fontsize=11,fontweight="bold",color="#002060")
                    fig_p.tight_layout(pad=1.5)
                    buf_p = io.BytesIO()
                    fig_p.savefig(buf_p,format="png",dpi=150,bbox_inches="tight")
                    buf_p.seek(0)
                    context[f"diag_yil{idx+1}_pie"] = InlineImage(doc,buf_p,width=Mm(95))
                    plt.close(fig_p)
            except Exception as e:
                st.warning(f"⚠️ Grafiklar chizishda xato: {e}")
                context["diag_jami_bar"] = ""
                context["diag_yil1_pie"] = ""
                context["diag_yil2_pie"] = ""
                context["diag_yil3_pie"] = ""
        else:
            context["diag_jami_bar"] = ""
            context["diag_yil1_pie"] = ""
            context["diag_yil2_pie"] = ""
            context["diag_yil3_pie"] = ""

        progress.progress(70, "Fotosuratlari...")

        def place_photos(files,prefix,max_slots):
            for s in range(max_slots): context[f"{prefix}_{s}"] = ""
            if files:
                for idx,f in enumerate(files[:max_slots]):
                    try:
                        img = Image.open(f).convert("RGB")
                        img.thumbnail((1600,1600),Image.LANCZOS)
                        buf = io.BytesIO()
                        img.save(buf,format="JPEG",quality=85,optimize=True)
                        buf.seek(0)
                        context[f"{prefix}_{idx}"] = InlineImage(doc,buf,width=Mm(145))
                    except: pass

        for i in range(1,11):
            place_photos(f_rooms.get(i,[]),f"rasm_{i}",ROOM_SLOTS[i])
        place_photos(f_harorat or [],f"rasm_harorat",2)

        progress.progress(85, "Kontekst yig'ilmoqda...")

        # Asosiy kontekst
        context.update({
            "titul_sana":f"«{now.strftime('%d')}» {now.strftime('%B')} {now.strftime('%Y')} yil",
            "audit_sanasi":now.strftime("%d.%m.%Y"),"xulosa_sanasi":now.strftime("%d.%m.%Y"),"audit_yili":now.strftime("%Y"),
            "lot_raqami":lot_raqami,"shartnoma_raqami":shartnoma_raqami,"kadastr_raqami":kadastr_raqami,
            "elektr_raqami":elektr_raqami,"gaz_raqami":gaz_raqami,
            "mijoz_ismi":mijoz_ismi,"manzil":manzil,"kenglik":kenglik,"uzunlik":uzunlik,
            "qurilgan_yili":qurilgan_yili,"oxirgi_remont_yili":oxirgi_remont,"qavat_soni":qavat_soni,
            "bolimlar_soni":bolimlar,"odam_soni":odam_soni,"oyna_soni":oyna_soni,"tashqi_eshik":eshik_soni,
            "umumiy_maydon_matn":_f(umumiy_m),"devor_maydoni_matn":_f(devor_m),"shift_maydoni_matn":_f(shift_m),
            "pol_maydoni_matn":_f(pol_m),"oyna_maydoni_matn":_f(oyna_m),"eshik_maydoni_matn":_f(eshik_m),
            "temp_1":_f(temp_1),"hum_1":_f(hum_1),"temp_2":_f(temp_2),"hum_2":_f(hum_2),
            "temp_3":_f(temp_3),"hum_3":_f(hum_3),"temp_4":_f(temp_4),"hum_4":_f(hum_4),
            "ortacha_ichki_harorat":_f(round((temp_1+temp_2+temp_3+temp_4)/4,1)),
            "izol_devor_narx_mln":_f(izol_devor),"izol_oyna_narx_mln":_f(izol_oyna),
            "izol_shift_narx_mln":_f(izol_shift),"izol_pol_narx_mln":_f(izol_pol),"izol_jami_narx_mln":_f(izol_jami),
            "sav_devor":_f(sav_devor),"sav_oyna":_f(sav_oyna),"sav_shift":_f(sav_shift),
            "sav_pol":_f(sav_pol),"sav_total":_f(sav_total),"sav_gelio":str(int(solar_gen_kvt)),
            "solar_kw":_f(solar_kw),"solar_panel_mln":_f(solar_panel_mln),"solar_invertor_mln":_f(solar_invert_mln),
            "solar_metal_mln":_f(solar_metal_mln),"solar_kabel_mln":_f(solar_kabel_mln),
            "solar_ornatish_mln":_f(solar_ornat_mln),"solar_jami_mln":_f(solar_jami_mln),
            "solar_gen_kwh_matn":f"{int(solar_gen_kvt):,}".replace(",","  "),
            "solar_spec_cons":_f(solar_spec_cons),"solar_tejam_sum_matn":f"{gelio_yillik_sum:,}".replace(",","  "),
            "solar_jami_sum_matn":f"{solar_jami_sum:,}".replace(",","  "),"solar_oqlash_matn":_f(gelio_oqlash),
            "gelio_hajmi":f"{int(solar_kw)} kVt","gelio_kunlik_kvt":_f(gelio_kunlik_kvt),
            "gelio_kunlik_sum_matn":f"{gelio_kunlik_sum:,}".replace(",","  "),
            "gelio_yillik_sum_matn":f"{gelio_yillik_sum:,}".replace(",","  "),
            "gelio_q_kj_matn":f"{gelio_q_kj:,}".replace(",","  "),"gelio_oqlash_muddat":_f(gelio_oqlash),
            "inv_gelio":_f(inv_gelio),"inv_total":_f(inv_total),
            "avg_spec_cons":_f(avg_spec),"avg_co2":_f(avg_co2),"avg_jami_summa":_f(avg_jami_summa),
            "co2_kg_matn":_f(co2_kg),"co2_tonna_matn":_f(avg_co2),
            "new_spec_cons":_f(new_spec),"new_summa":_f(new_summa),"new_co2":_f(new_co2),
            "energiya_toifasi":toifa,
        })

        progress.progress(95, "Word yaratilmoqda...")

        doc.render(context,autoescape=True)
        safe_name = "".join(c for c in mijoz_ismi if c.isalnum() or c in " _-").strip().replace(" ","_")
        file_name = f"Energo_Audit_{safe_name}_{now.strftime('%Y%m%d_%H%M')}.docx"

        out_buf = io.BytesIO()
        doc.save(out_buf)
        out_buf.seek(0)

        progress.progress(100,"✅ Tayyor!")
        st.balloons()
        st.success(f"🎉 Hujjat tayyor! — `{file_name}`")

        kk1,kk2,kk3,kk4 = st.columns(4)
        kk1.metric("Sarif","o'rtacha",f"{avg_spec} kVt/m²")
        kk2.metric("CO₂",f"{avg_co2} t/yil","")
        kk3.metric("Solar tejam",f"{gelio_yillik_sum:,}","so'm")
        kk4.metric("Investitsiya",f"{inv_total} mln","so'm")

        st.download_button(label="📥 WORD YUKLAB OLISH",data=out_buf,file_name=file_name,
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           use_container_width=True)

    except Exception:
        progress.empty()
        st.error("❌ Hujjat yaratishda xatolik!")
        st.code(traceback.format_exc(),language="python")
