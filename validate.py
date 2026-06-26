# validate.py
import shutil
import os
import great_expectations as gx
import pandas as pd

# ── 0. Clean slate: remove old GX context so reruns don't conflict ──
if os.path.exists("gx"):
    shutil.rmtree("gx")

# ── 1. Load data ──────────────────────────────────────────────
df = pd.read_csv("customer_data.csv")
print(f"Loaded {len(df)} rows")

# ── 2. Get context ────────────────────────────────────────────
context = gx.get_context(mode="file")

# ── 3. Add datasource ─────────────────────────────────────────
datasource = context.data_sources.add_pandas(name="customer_datasource")
asset = datasource.add_dataframe_asset(name="customer_data")
batch_definition = asset.add_batch_definition_whole_dataframe("customer_batch")

# ── 4. Create expectation suite ───────────────────────────────
suite = context.suites.add(
    gx.ExpectationSuite(name="customer_data_expectations")
)

# ── 5. Add all 8 expectations ─────────────────────────────────
from great_expectations.expectations import (
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeUnique,
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToBeInSet,
    ExpectTableRowCountToBeBetween,
)

suite.add_expectation(ExpectColumnValuesToNotBeNull(column="customer_id"))
suite.add_expectation(ExpectColumnValuesToBeUnique(column="customer_id"))

suite.add_expectation(
    ExpectColumnValuesToBeBetween(column="age", min_value=0, max_value=120)
)

suite.add_expectation(
    ExpectColumnValuesToMatchRegex(
        column="email",
        regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )
)

suite.add_expectation(
    ExpectColumnValuesToNotBeNull(column="salary", mostly=0.95)
)

suite.add_expectation(
    ExpectColumnValuesToBeInSet(
        column="country",
        value_set=["USA", "Canada", "UK", "Australia"]
    )
)

suite.add_expectation(
    ExpectColumnValuesToMatchRegex(
        column="signup_date",
        regex=r"^\d{1,2}/\d{1,2}/\d{4}$|^\d{4}-\d{2}-\d{2}$"
    )
)

suite.add_expectation(
    ExpectColumnValuesToMatchRegex(
        column="phone",
        regex=r"^\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}$",
        mostly=0.80
    )
)

suite.add_expectation(
    ExpectTableRowCountToBeBetween(min_value=500, max_value=1000)
)

# ── 6. Create validation definition ───────────────────────────
validation_definition = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="customer_validation",
        data=batch_definition,
        suite=suite,
    )
)

# ── 7. Run validation ─────────────────────────────────────────
results = validation_definition.run(batch_parameters={"dataframe": df})

# ── 8. Print summary ──────────────────────────────────────────
print(f"\nOverall success: {results.success}")
passed = sum(1 for r in results.results if r.success)
failed = len(results.results) - passed
print(f"Evaluated : {len(results.results)}")
print(f"Passed    : {passed}")
print(f"Failed    : {failed}")

print("\n── Full Validation Results ──")

issues_found = []

for result in results.results:
    kwargs = result.expectation_config.kwargs
    col = kwargs.get("column", "TABLE")
    expectation = result.expectation_config.type
    status_icon = "✅" if result.success else "❌"

    if expectation == "expect_table_row_count_to_be_between":
        if result.success:
            detail = "N/A"
            count_for_issue = "N/A"
            pct_str = "N/A"
        else:
            observed = result.result.get("observed_value", "N/A")
            min_val = kwargs.get("min_value", "N/A")
            max_val = kwargs.get("max_value", "N/A")
            detail = f"Observed: {observed} (expected {min_val}–{max_val})"
            count_for_issue = observed
            pct_str = "N/A"
    else:
        if result.success:
            detail = "N/A"
            count_for_issue = "N/A"
            pct_str = "N/A"
        else:
            unexpected = result.result.get("unexpected_count", "N/A")
            pct = result.result.get("unexpected_percent", "N/A")
            pct_str = f"{round(pct, 1)}%" if isinstance(pct, float) else str(pct)
            detail = f"Count: {str(unexpected):<10} ({pct_str})"
            count_for_issue = unexpected

    print(f"{status_icon} {col:15s} | {expectation:40s} | {detail}")

    if not result.success:
        issues_found.append({
            "column": col,
            "expectation": expectation,
            "count": count_for_issue,
            "percent": pct_str
        })

print(f"\nTotal issues found: {len(issues_found)}")

# ── 9. Build Data Docs HTML ───────────────────────────────────
context.build_data_docs()
print("\n✅ Data Docs HTML generated.")
print("   Open: gx/uncommitted/data_docs/local_site/index.html")