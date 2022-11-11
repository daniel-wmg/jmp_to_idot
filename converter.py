import pandas as pd
from solution import Solution


class Converter:

    def __init__(self, jmp_output, final_vol=1):
        self.input_df = pd.read_csv(jmp_output)
        self.final_vol = final_vol
        self.solutions = {}

        self.parse_input()

    def parse_input(self):
        for col in self.input_df.columns:
            self.input_df[col] = self.input_df[col].astype("category")
            self.input_df[col] = self.input_df[col].astype("category")

            self.solutions[col] = Solution(col, 1, "")
            self.solutions[col].set_levels(self.input_df[col].cat.categories.to_list(), self.final_vol)

    def get_reagents(self):
        return self.input_df.columns.tolist()

    def set_liquid_stocks(self, stocks):
        for i, sol in enumerate(self.solutions):
            self.solutions[sol].set_stock_conc(stocks[sol]["stock"])
            self.solutions[sol].set_stock_location(stocks[sol]["location"])

    def _get_conc_vol(self, x, solution):
        sol = self.solutions[solution]
        return sol.get_volume_for_level(x)

    def _get_liquid_source_well(self, x):
        sol = self.solutions[x]
        return sol.get_stock_source_well()

    def generate_plate_indices(self, num_samples):
        num_rows = num_samples // 12
        num_cols_remaining = num_samples - (12 * num_rows)

        a = []
        final_row = 0
        for i in range(0, num_rows):
            current_letter = chr(i + 65)
            final_row = i
            for j in range(0, 12):
                a.append(f"{current_letter}{j + 1}")

        for k in range(0, num_cols_remaining):
            a.append(f"{chr(final_row + 66)}{k + 1}")

        return a

    def build_output(self):
        output_df = self.input_df.copy()

        for col in output_df:
            output_df[col] = pd.to_numeric(output_df[col])
            output_df[col] = output_df[col].apply(lambda x: self._get_conc_vol(x, col))

        num_samples = len(output_df)

        output_df["well"] = self.generate_plate_indices(num_samples)

        output_df = pd.melt(output_df, id_vars="well")

        output_df["liquid"] = output_df["variable"]
        output_df["variable"] = output_df["variable"].apply(self._get_liquid_source_well)
        output_df["value"] = output_df["value"] / 10000000
        output_df = output_df[output_df["value"] != 0]
        output_df = output_df.rename(
            {"well": "Source Well", "variable": "Target Well", "value": "Volume [L]", "liquid": "Liquid Name"}, axis=1)

        return output_df

    def build_header(self):

        header_items = [
            [
                "calibration_protocol_1.1",
                "1.4.20190923",
                "<User Name>",
                "15/11/2019",
                "12:00",
                "",
                ""],
            ["SourcePlate500_90",
             "Source Plate 1",
             "",
             "MWP 384",
             "Target Plate 1",
             "",
             "Eppi"],
            ["DispenseToWaste=True",
             "DispenseToWasteCycles=3",
             "DispenseToWasteVolume=1e-7",
             "UseDeionisation=True",
             "OptimizationLevel=ReorderAndParallel",
             "WasteErrorHandlingLevel=Ask",
             ""]

        ]

        header = ""

        for row in header_items:
            header += f"{','.join(row)}\n"

        return header

    def write_output(self, filename, header, body_df):
        body = body_df.to_csv(index=False)

        output_str = header + body

        with open(filename, "w") as f:
            f.write(output_str)
