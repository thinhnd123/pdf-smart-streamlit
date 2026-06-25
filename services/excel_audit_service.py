import pandas as pd
import tempfile
from openpyxl import load_workbook

def run_data_audit(
    excel_path,
    key_col,
    value_col
    ):


    try:

        df = pd.read_excel(
            excel_path,
            dtype=str
        ).fillna("")

        # =====================================
        # Duplicate Summary
        # =====================================

        duplicate_summary = []

        for col in df.columns:

            total = len(df)

            unique = df[col].nunique()

            duplicate = total - unique

            duplicate_summary.append(
                {
                    "Column": col,
                    "Total Rows": total,
                    "Unique Values": unique,
                    "Duplicate Count": duplicate
                }
            )

        duplicate_summary = pd.DataFrame(
            duplicate_summary
        ).sort_values(
            "Duplicate Count",
            ascending=False
        )

        # =====================================
        # Top Duplicate Values
        # =====================================

        duplicate_detail = []

        for col in df.columns:

            vc = (
                df[col]
                .value_counts()
                .reset_index()
            )

            vc.columns = [
                "Value",
                "Count"
            ]

            vc = vc[
                vc["Count"] > 1
            ]

            vc = vc.head(10)

            for _, row in vc.iterrows():

                duplicate_detail.append(
                    {
                        "Column": col,
                        "Value": row["Value"],
                        "Count": row["Count"]
                    }
                )

        duplicate_detail = pd.DataFrame(
            duplicate_detail
        )

        # =====================================
        # Auto Relationship Audit
        # =====================================

        relationship_result = []

        for k_col in df.columns:

            for v_col in df.columns:

                if k_col == v_col:
                    continue

                temp = (
                    df.groupby(k_col)[v_col]
                    .nunique()
                )

                issue_count = (
                    temp > 1
                ).sum()

                if issue_count > 0:

                    relationship_result.append(
                        {
                            "Key Column": k_col,
                            "Value Column": v_col,
                            "Issue Count": issue_count
                        }
                    )

        relationship_df = pd.DataFrame(
            relationship_result
        )

        if len(relationship_df):

            relationship_df = relationship_df.sort_values(
                "Issue Count",
                ascending=False
            )
        # =====================================
        # Relationship Check
        # =====================================

        issue_df = (

            df.groupby(key_col)[value_col]

            .nunique()

            .reset_index(
                name="Different Values"
            )

        )

        issue_df = issue_df[
            issue_df["Different Values"] > 1
        ]

        issue_df = issue_df.sort_values(
            "Different Values",
            ascending=False
        )

        # =====================================
        # Detail
        # =====================================

        if len(issue_df):

            bad_keys = issue_df[
                key_col
            ].tolist()

            detail_df = df[
                df[key_col].isin(
                    bad_keys
                )
            ]

        else:

            detail_df = pd.DataFrame()

        # =====================================
        # Export
        # =====================================

        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".xlsx"
        ).name

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            duplicate_summary.to_excel(
                writer,
                sheet_name="Duplicate Summary",
                index=False
            )

            duplicate_detail.to_excel(
                writer,
                sheet_name="Duplicate Detail",
                index=False
            )

            issue_df.to_excel(
                writer,
                sheet_name="Model Multi Price",
                index=False
            )

            detail_df.to_excel(
                writer,
                sheet_name="Detail",
                index=False
            )
            
            relationship_df.to_excel(
                writer,
                sheet_name="Relationship Audit",
                index=False
            )

        return (
            output_file,
            duplicate_summary,
            duplicate_detail,
            issue_df,
            detail_df,
            relationship_df,
            "Audit hoàn tất"
        )

    except Exception as e:

        return (
            None,
            None,
            None,
            None,
            None,
            str(e)
        )

