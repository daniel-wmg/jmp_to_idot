class Solution():

    def __init__(self, name, stock_conc, stock_location):
        self.name = name
        self.stock_conc = stock_conc
        self.stock_location = stock_location
        self.levels = {}
        self.final_sol_vol = 1

    def _get_v1(self, c1, c2, v2):
        return (c2 * v2) / c1

    def set_levels(self, levels, final_solution_vol):
        self.final_sol_vol = final_solution_vol
        for level in levels:
            self.levels[level] = self._get_v1(self.stock_conc, level, final_solution_vol)

    def set_stock_conc(self, conc):
        self.stock_conc = conc
        for level in self.levels:
            self.levels[level] = self._get_v1(self.stock_conc, level, self.final_sol_vol)

    def set_stock_location(self, location):
        self.stock_location = location

    def get_volume_for_level(self, level):
        return self.levels[level]

    def get_stock_source_well(self):
        return self.stock_location

    def __repr__(self):
        return f"Solution of {self.name} with stock conc {self.stock_conc} (mM). Levels:\n{self.levels}"
