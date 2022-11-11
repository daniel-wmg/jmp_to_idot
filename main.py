from converter import Converter

conv = Converter(jmp_output="input.csv", final_vol=1000)

stocks = {
    "MgCl2 (mM)": {"stock": 1000, "location": "A1"},
    "(NH4)2SO4 (mM)": {"stock": 1000, "location": "A1"},
    "KCl (mM)": {"stock": 1000, "location": "A1"},
    "Enzyme (ng/ul)": {"stock": 1000, "location": "A1"},
    "TMAC (mM)": {"stock": 1000, "location": "A1"},
    "DMSO (%)": {"stock": 1000, "location": "A1"}
}

conv.set_liquid_stocks(stocks)
output = conv.build_output()
conv.write_output("aa.csv", conv.build_header(), output)
