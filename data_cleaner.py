import pandas as pd

class DataResilienceEngine:
    @staticmethod
    def process_board_dataframe(raw_items: list):
        if not raw_items:
            return pd.DataFrame(), {"status": "empty", "total_records": 0}

        cleaned_records = []
        for item in raw_items:
            record = {"Item_ID": item.get("id"), "Item_Name": item.get("name")}
            for cv in item.get("column_values", []):
                col_title = cv.get("column", {}).get("title")
                val_text = cv.get("text")
                if col_title and val_text:
                    record[col_title] = val_text
            cleaned_records.append(record)

        df = pd.DataFrame(cleaned_records)
        
        quality_report = {
            "total_records": len(df),
            "missing_cells": int(df.isna().sum().sum()) if not df.empty else 0
        }
        
        return df, quality_report