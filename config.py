"""
Central configuration file for the Flask application.

This file contains all the settings and constants used across the application,
making it easy to manage and modify configurations from a single location.
"""

# --- Database Configuration ---
DATABASE_NAME = 'db.sqlite'

# --- Server Configuration ---
SERVER_PORT = 5000

# --- Real-Time Simulation Configuration ---
# The time in seconds that the data generator waits before sending a new update.
SIMULATION_INTERVAL_SECONDS = 5

# --- Manually Verified Coordinate Data ---
VERIFIED_COORDINATES = {
    "Abdullah Hukum": {"lat": 3.1188319, "lon": 101.6732377},
    "Alam Megah": {"lat": 3.0231025098204394, "lon": 101.57211549888724},
    "Ampang Park": {"lat": 3.160062, "lon": 101.7190053},
    "Ara Damansara": {"lat": 3.108771553447338, "lon": 101.5864149115486},
    "Asia Jaya": {"lat": 3.104441327047661, "lon": 101.63770721799644},
    "Bandar Tun Hussein Onn": {"lat": 3.0483702717217134, "lon": 101.77512808852975},
    "Bandar Utama": {"lat": 3.1468634, "lon": 101.6186865},
    "Bangsar": {"lat": 3.1275597, "lon": 101.6790602},
    "Batu 11 Cheras": {"lat": 3.0415490607439075, "lon": 101.7733156711643},
    "Bukit Bintang": {"lat": 3.1460953, "lon": 101.7114762},
    "Bukit Dukung": {"lat": 3.026512260525024, "lon": 101.771092267453},
    "Cochrane": {"lat": 3.1324723, "lon": 101.7230543},
    "Damai": {"lat": 3.1644733, "lon": 101.7244083},
    "Dang Wangi": {"lat": 3.1568579, "lon": 101.7019848},
    "Dato' Keramat": {"lat": 3.1650189, "lon": 101.731853},
    "Glenmarie": {"lat": 3.096073268173765, "lon": 101.59025995211034},
    "Gombak": {"lat": 3.2312176, "lon": 101.7244253},
    "Jelatek": {"lat": 3.1673333, "lon": 101.7353159},
    "KL Sentral (KJL)": {"lat": 3.1343094015014534, "lon": 101.68609334693598},
    "KLCC": {"lat": 3.1592469, "lon": 101.7133662},
    "Kajang": {"lat": 2.983291228870008, "lon": 101.79053187175903},
    "Kampung Baru": {"lat": 3.1613264, "lon": 101.7065974},
    "Kelana Jaya": {"lat": 3.1126776830519387, "lon": 101.6044900809461},
    "Kerinchi": {"lat": 3.1154917, "lon": 101.6684949},
    "Kota Damansara": {"lat": 3.1505241189110476, "lon": 101.57864315506677},
    "Kwasa Damansara": {"lat": 3.1767415079468546, "lon": 101.57236334656068},
    "Kwasa Sentral": {"lat": 3.17017353275566, "lon": 101.56483436930343},
    "Lembah Subang": {"lat": 3.1122616050632335, "lon": 101.59122896745326},
    "Maluri (SBK)": {"lat": 3.1247549674463815, "lon": 101.72727635211051},
    "Masjid Jamek (KJL)": {"lat": 3.1494620854175155, "lon": 101.69642181864305},
    "Merdeka": {"lat": 3.1429735, "lon": 101.7021849},
    "Mutiara Damansara": {"lat": 3.1553010001163844, "lon": 101.60871960112053},
    "Muzium Negara": {"lat": 3.1371006, "lon": 101.6873833},
    "Pasar Seni (KJL)": {"lat": 3.1427085851764684, "lon": 101.695410170714},
    "Pasar Seni (SBK)": {"lat": 3.142481415420169, "lon": 101.69531614794404},
    "Phileo Damansara": {"lat": 3.1291991, "lon": 101.6429822},
    "Pusat Bandar Damansara": {"lat": 3.1432978, "lon": 101.6624268},
    "Putra Heights (KJL)": {"lat": 2.9960778476011956, "lon": 101.57551791822944},
    "SS 15": {"lat": 3.076219, "lon": 101.58811},
    "SS 18": {"lat": 3.06915, "lon": 101.5852},
    "Semantan": {"lat": 3.1509652, "lon": 101.6653573},
    "Setiawangsa": {"lat": 3.175800522606992, "lon": 101.73589617084988},
    "Sri Rampai": {"lat": 3.1992489, "lon": 101.7372696},
    "Sri Raya": {"lat": 3.0622258470111072, "lon": 101.77286110369512},
    "Stadium Kajang": {"lat": 2.994544316111254, "lon": 101.7863435958347},
    "Subang Alam": {"lat": 3.0094572000250905, "lon": 101.5722796108533},
    "Subang Jaya": {"lat": 3.0845797544535625, "lon": 101.5873752659475},
    "Sungai Jernih": {"lat": 3.0007633321499747, "lon": 101.78396771663952},
    "Surian": {"lat": 3.1497108546873873, "lon": 101.59367164252724},
    "TTDI": {"lat": 3.1361413, "lon": 101.6307373},
    "Taipan": {"lat": 3.0481687210747563, "lon": 101.59023720769395},
    "Taman Bahagia": {"lat": 3.1107266099634368, "lon": 101.61269758648046},
    "Taman Connaught": {"lat": 3.0791818, "lon": 101.7451427},
    "Taman Jaya": {"lat": 3.1075, "lon": 101.646},
    "Taman Melati": {"lat": 3.2195172, "lon": 101.721876},
    "Taman Midah": {"lat": 3.104286, "lon": 101.7323396},
    "Taman Mutiara": {"lat": 3.0912676, "lon": 101.7403423},
    "Taman Paramount": {"lat": 3.1047123428799814, "lon": 101.62315876050071},
    "Taman Pertama": {"lat": 3.1127246, "lon": 101.7292803},
    "Taman Suntex": {"lat": 3.0715969903540437, "lon": 101.76358207087557},
    "Tun Razak Exchange (TRX)": {"lat": 3.1427699, "lon": 101.7200049},
    "USJ 21": {"lat": 3.029892040067465, "lon": 101.58171229295425},
    "USJ 7 (KJL)": {"lat": 3.0553321159333717, "lon": 101.59190822389331},
    "Universiti": {"lat": 3.1145395, "lon": 101.6617007},
    "Wangsa Maju": {"lat": 3.2057781, "lon": 101.7318615},
    "Wawasan": {"lat": 3.03507492592289, "lon": 101.58834495372092},
}

# --- Definitive Source for Line Sequences (from Official Maps) ---
KAJANG_LINE = [
    "Kajang", "Stadium Kajang", "Sungai Jernih", "Bukit Dukung", "Batu 11 Cheras",
    "Bandar Tun Hussein Onn", "Sri Raya", "Taman Suntex", "Taman Connaught",
    "Taman Mutiara", "Taman Midah", "Taman Pertama", "Maluri (SBK)", "Cochrane",
    "Tun Razak Exchange (TRX)", "Bukit Bintang", "Merdeka", "Pasar Seni (SBK)",
    "Muzium Negara", "Semantan", "Pusat Bandar Damansara", "Phileo Damansara",
    "TTDI", "Bandar Utama", "Mutiara Damansara", "Surian", "Kota Damansara",
    "Kwasa Sentral", "Kwasa Damansara"
]

KELANA_JAYA_LINE = [
    "Gombak", "Taman Melati", "Wangsa Maju", "Sri Rampai", "Setiawangsa", "Jelatek", 
    "Dato' Keramat", "Damai", "Ampang Park", "KLCC", "Kampung Baru", "Dang Wangi", 
    "Masjid Jamek (KJL)", "Pasar Seni (KJL)", "KL Sentral (KJL)", "Bangsar", 
    "Abdullah Hukum", "Kerinchi", "Universiti", "Taman Jaya", "Asia Jaya", 
    "Taman Paramount", "Taman Bahagia", "Kelana Jaya", "Lembah Subang", 
    "Ara Damansara", "Glenmarie", "Subang Jaya", "SS 15", "SS 18", 
    "USJ 7 (KJL)", "Taipan", "Wawasan", "USJ 21", "Alam Megah", "Subang Alam", 
    "Putra Heights (KJL)"
]

INTERCHANGE_STATIONS = {
    "Pasar Seni (KJL)": "Pasar Seni (SBK)",
    "Muzium Negara": "KL Sentral (KJL)",
}

STATIONS_TO_EXCLUDE = {"Sungai Buloh", "Kampung Selamat"}
