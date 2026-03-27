"""
Data for NYC Expense Budget
Dataset Identifier: mwzb-yiwb
SOURCE: https://data.cityofnewyork.us/City-Government/Expense-Budget/mwzb-yiwb/about_data
"""

import polars as pl

from data.utils.utils import load_data, prepare_dataset_for_db, upload_dataset


ID = "mwzb-yiwb"
SOURCE = "https://data.cityofnewyork.us/City-Government/Expense-Budget/mwzb-yiwb/about_data"
data = load_data(ID)


def _pick_column(columns: list[str], candidates: list[str]) -> str:
	for candidate in candidates:
		if candidate in columns:
			return candidate
	raise ValueError(f"Missing expected columns. Tried: {candidates}")


def expense_budget_per_year(data) -> dict:

	year_col = _pick_column(data.columns, ["fiscal_year", "FISC_YEAR"])
	amount_col = _pick_column(data.columns, ["adopted_budget_amount", "Adopted_Amt"])

	by_year = (
		data.with_columns(
			pl.col(year_col).cast(pl.Int64, strict=False).alias("fiscal_year"),
			pl.col(amount_col).cast(pl.Float64, strict=False).alias("adopted_amount"),
		)
		.filter(pl.col("fiscal_year").is_not_null() & pl.col("adopted_amount").is_not_null())
		.group_by("fiscal_year")
		.agg(pl.col("adopted_amount").sum().alias("adopted_total"))
		.sort("fiscal_year")
	)
	

	filename = prepare_dataset_for_db(
		dataset=by_year,
		dataset_x="fiscal_year",
		dataset_y="adopted_total",
		title="NYC Expense Budget per Fiscal Year",
		type="line",
		city="New York City",
		y_min=0,
		source=SOURCE,
		subtitle="Sum of adopted expense budget amount by fiscal year",
		note="Grouped by fiscal year and summed adopted budget amount.",
	)

	return filename


if __name__ == "__main__":
	filename = expense_budget_per_year(data)
	upload_dataset(filename)
