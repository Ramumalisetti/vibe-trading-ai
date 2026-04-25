"""
Local API Server — Full Nifty 500 + All F&O Universe (~450 stocks)
Run this on your computer every morning before market hours.
Access the scanner at: http://localhost:3000
"""
from http.server import HTTPServer
from api.scan import handler, analyze_stock, TICKERS
import concurrent.futures, json

# ── Complete Nifty 500 + F&O Universe ────────────────────────────────────────
FULL_TICKERS = TICKERS + [
    # ── Nifty Next 50 ──────────────────────────────────────────────────────
    "BHEL.NS","BEL.NS","HAL.NS","IRFC.NS","PFC.NS","RECLTD.NS","GAIL.NS",
    "SAIL.NS","NMDC.NS","AMBUJACEM.NS","PNB.NS","BANKBARODA.NS","CANBK.NS",
    "DLF.NS","GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","PIDILITIND.NS",
    "HAVELLS.NS","VOLTAS.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS","ASHOKLEY.NS",
    "TVSMOTOR.NS","TATACOMM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "SRF.NS","ASTRAL.NS","DIXON.NS","POLYCAB.NS","TATAPOWER.NS",
    "ATGL.NS","PETRONET.NS","INDHOTEL.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "IDFCFIRSTB.NS","BANDHANBNK.NS","FEDERALBNK.NS","RBLBANK.NS","AUBANK.NS",
    "JIOFIN.NS","LODHA.NS","VEDL.NS","SHRIRAMFIN.NS","HDFCAMC.NS",
    "NIPPONLIFE.NS","ICICIPRAMC.NS","UTIAMC.NS","NAUKRI.NS","DMART.NS",
    # ── All F&O Pharma / Healthcare ────────────────────────────────────────
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "LALPATHLAB.NS","METROPOLIS.NS","FORTIS.NS","MAXHEALTH.NS",
    "GLAXO.NS","PFIZER.NS","ABBOTINDIA.NS","SANOFI.NS","NATCOPHARMA.NS",
    "POLYMED.NS","APOLLOHOSP.NS","AARTIIND.NS","GRANULES.NS","GLENMARK.NS",
    "BIOCON.NS","AJANTPHARM.NS","JBCHEPHARM.NS","ERIS.NS","LAURUSLABS.NS",
    "STRIDES.NS","SOLARA.NS","SEQUENT.NS","SUVEN.NS","NEULANDLAB.NS",
    # ── All F&O IT / Technology ────────────────────────────────────────────
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS",
    "RATEGAIN.NS","TANLA.NS","INTELLECT.NS","MASTEK.NS","ZENSAR.NS",
    "NIITTECH.NS","HEXAWARE.NS","BIRLASOFT.NS","SONATSOFTW.NS","HINDWARE.NS",
    "CMSINFO.NS","ECLERX.NS","NUCLEUS.NS","DATAMATICS.NS","FIRSTSOURCE.NS",
    # ── All F&O Auto & EV ──────────────────────────────────────────────────
    "EXIDEIND.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    "SUNDRMFAST.NS","MINDAIND.NS","GABRIEL.NS","CRAFTSMAN.NS","PRICOL.NS",
    "ENDURANCE.NS","SUPRAJIT.NS","MINDA.NS","SUBROS.NS","LUMAXTECH.NS",
    "TIINDIA.NS","GREENPANEL.NS","SCHAEFFLER.NS","SKFINDIA.NS","TIMKEN.NS",
    # ── All F&O Infrastructure / Capital Goods ─────────────────────────────
    "CESC.NS","TORNTPOWER.NS","INOXWIND.NS","SUZLON.NS","THERMAX.NS",
    "KPIL.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS","RITES.NS",
    "RAILVIKAS.NS","GRINFRA.NS","PNCINFRATECH.NS","HGINFRA.NS",
    "AHLUCONT.NS","PSP.NS","KNRCON.NS","HCC.NS","CAPACITE.NS",
    "GPPL.NS","JMFINANCIAL.NS","ENGINERSIN.NS","BHEL.NS","POWMECH.NS",
    # ── All F&O Consumer / FMCG ────────────────────────────────────────────
    "RADICO.NS","VARUN.NS","VBLLTD.NS","UNITDSPR.NS",
    "JYOTHYLAB.NS","EMAMILTD.NS","BAJAJCONS.NS","HATSUN.NS",
    "TATACONSUM.NS","BRITANNIA.NS","NESTLEIND.NS","HINDUNILVR.NS",
    "GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","ITC.NS",
    "PGHH.NS","BERGEPAINT.NS","KANSAINER.NS","AKZONOBEL.NS",
    "SUPREMEIND.NS","APLAPOLLO.NS","HERITGFOOD.NS","AGRO.NS",
    # ── All F&O Metals & Mining ────────────────────────────────────────────
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    "MAHSEAMLES.NS","MIDHANI.NS","WELSPUNIND.NS","JSWENERGY.NS",
    "NSLNISP.NS","TINPLATE.NS","GMRINFRA.NS","APL.NS","SSWL.NS",
    # ── All F&O Real Estate / Cement ───────────────────────────────────────
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","KOLTEPATIL.NS","MAHLIFE.NS","SUNTECK.NS",
    "RAMCOCEM.NS","DALMIA.NS","HEIDELBERG.NS","JKCEMENT.NS","STARCEMENT.NS",
    "ORIENTCEM.NS","BIRLACORPN.NS","PRISMJOINTS.NS","JKPAPER.NS","TNPL.NS",
    # ── All F&O Chemicals / Specialty ──────────────────────────────────────
    "DEEPAKNITR.NS","GNFC.NS","ALKYLAMINE.NS","VINATIORGA.NS","NAVINFLUOR.NS",
    "FLUOROCHEM.NS","PCBL.NS","AAVAS.NS","CLEAN.NS","PIDILITIND.NS",
    "BALAMINES.NS","FINEORG.NS","GALAXYSURF.NS","NOCIL.NS","TATACHEM.NS",
    "GHCL.NS","ATUL.NS","SUDARSCHEM.NS","HFCL.NS","LXCHEM.NS",
    # ── All F&O Banking / Finance ──────────────────────────────────────────
    "ABCAPITAL.NS","CHOLAHLDNG.NS","PNBHOUSING.NS","LICHSGFIN.NS",
    "MANAPPURAM.NS","BAJAJHFL.NS","UJJIVANSFB.NS","EQUITASBNK.NS",
    "ESAFSFB.NS","CSBBANK.NS","SURYODAY.NS","KARURVYSYA.NS","DCBBANK.NS",
    "INDIAMART.NS","ANGELONE.NS","5PAISA.NS","IIFL.NS","MOFSL.NS",
    "GEOJITFSL.NS","SMCGLOBAL.NS","NSIL.NS","IREDA.NS",
    # ── All F&O Telecom / Media ────────────────────────────────────────────
    "INDUSTOWER.NS","TTML.NS","TEJASNET.NS",
    "SAREGAMA.NS","ZEEMEDIA.NS","SUNTV.NS","PVRINOX.NS","INOXLEISUR.NS",
    # ── All F&O Logistics / Transport ─────────────────────────────────────
    "BLUEDART.NS","TCI.NS","GATI.NS","MAHLOG.NS",
    "CONCOR.NS","VRL.NS","TVSSCS.NS","ALLCARGO.NS","AEGISCHEM.NS",
    # ── All F&O Retail / E-Commerce ───────────────────────────────────────
    "NYKAA.NS","PAYTM.NS","CARTRADE.NS","JUBLFOOD.NS","WESTLIFE.NS",
    "DEVYANI.NS","SAPPHIRE.NS","BARBEQUE.NS","SPECIALITY.NS","DMART.NS",
    # ── Nifty Midcap 150 (Additional) ─────────────────────────────────────
    "APOLLOTYRE.NS","MRF.NS","CEATLTD.NS","BALKRISIND.NS","JKTYRE.NS",
    "BATAINDIA.NS","RELAXO.NS","VMART.NS","TRENT.NS","SHOPERSTOP.NS",
    "SPARC.NS","WOCKPHARMA.NS","SYNGENE.NS","DISHTV.NS","NETWORK18.NS",
    "TV18BRDCST.NS","ZEEL.NS","NDTV.NS","EDELWEISS.NS","MOTILALOFS.NS",
    "JMFINANCIL.NS","JSWINFRA.NS","ADANIGREEN.NS","ADANIPOWER.NS","ATGL.NS",
    "ADANITRANS.NS","AWL.NS","ADANIPORTS.NS","NAUKRI.NS","POLICYBZR.NS",
    "CENSUSINDIA.NS","ROUTE.NS","CDSL.NS","BSE.NS","MCX.NS","CAMS.NS",
    "KFINTECH.NS","MAPMYINDIA.NS","INDIGOPNTS.NS","SIGNATUREG.NS",
    # ── PSU / Government ───────────────────────────────────────────────────
    "BPCL.NS","IOC.NS","HINDPETRO.NS","MRPL.NS","CPCL.NS",
    "OIL.NS","PETRONET.NS","GAIL.NS","MGL.NS","IGL.NS","GSPL.NS",
    "SJVN.NS","NHPC.NS","THANGAMAYL.NS","BEML.NS","MIDHANI.NS",
    "MTNL.NS","BSNL.NS","HUDCO.NS","REC.NS","IREDA.NS",
]
FULL_TICKERS = list(dict.fromkeys(FULL_TICKERS))  # remove any duplicates


class FullHandler(handler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            for res in concurrent.futures.as_completed(
                    {ex.submit(analyze_stock, t): t for t in FULL_TICKERS}):
                if res.result(): all_setups.extend(res.result())

        priority = {'RSI Divergence + Vol Spike':0,'DEMA Momentum Spike':1,
                    'Pullback to Value':2,'Darvas Breakout':3}
        all_setups.sort(key=lambda x: (priority.get(x['strategy'],9), -x['rr']))

        payload = json.dumps({"status":"success","data":all_setups}).encode()
        self.wfile.write(payload)
        print(f"✅ Scan complete. {len(all_setups)} setups found across {len(FULL_TICKERS)} stocks.")


if __name__ == "__main__":
    total = len(FULL_TICKERS)
    print("")
    print("==========================================")
    print("  Vibe Trading AI - Full Universe Server")
    print("==========================================")
    print(f"Sectors: Nifty50, Next50, F&O, Pharma, IT,")
    print(f"         Auto, Infra, Metals, Cement, Chem,")
    print(f"         Banking, Finance, PSU, Midcap, Retail")
    print("")
    print(f"TOTAL UNIQUE STOCKS TO SCAN: {total}")
    print(f"Dashboard: http://localhost:3000")
    print(f"Note: First scan takes 60-120 seconds")
    print("==========================================")
    print("")
    server = HTTPServer(('localhost', 5000), FullHandler)
    server.serve_forever()
