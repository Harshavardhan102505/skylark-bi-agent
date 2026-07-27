import os
import re
import json
from groq import Groq
from monday_client import MondayClient
from data_cleaner import DataResilienceEngine

class BIAgent:
    def __init__(self, monday_token: str = None, groq_key: str = None):
        self.groq_api_key = groq_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing!")
            
        self.client = Groq(api_key=self.groq_api_key)
        self.monday_client = MondayClient(api_token=monday_token)
        self.deals_board_id = os.getenv("DEALS_BOARD_ID")
        self.work_orders_board_id = os.getenv("WORK_ORDERS_BOARD_ID")

    def _get_board_data_tool(self, board_type: str) -> str:
        """Fetch real board items and summarize metrics."""
        board_id = self.deals_board_id if board_type == "deals" else self.work_orders_board_id
        if not board_id:
            return json.dumps({
                "error": f"Board ID for '{board_type}' is not configured in .env file.",
                "status": "missing_config"
            })
            
        raw_items = self.monday_client.fetch_board_items(board_id, limit=30)
        df, quality_report = DataResilienceEngine.process_board_dataframe(raw_items)
        
        if df.empty:
            return json.dumps({
                "board_type": board_type,
                "message": "No live records retrieved from monday.com.",
                "quality": quality_report
            })

        # Keep essential business columns
        essential_cols = [
            c for c in df.columns 
            if any(k in c.lower() for k in ['name', 'value', 'amount', 'stage', 'status', 'sector', 'owner', 'date'])
        ]
        trimmed_df = df[essential_cols] if essential_cols else df

        summary = {
            "total_records": len(df),
            "columns": list(trimmed_df.columns),
            "records_sample": trimmed_df.head(5).to_dict(orient="records")
        }

        # Value sums
        val_cols = [c for c in trimmed_df.columns if any(k in c.lower() for k in ['value', 'amount'])]
        for v_col in val_cols:
            if trimmed_df[v_col].dtype in ['float64', 'int64']:
                summary[f"total_{v_col}"] = float(trimmed_df[v_col].sum())

        # Sector / Stage breakdowns
        cat_cols = [c for c in trimmed_df.columns if any(k in c.lower() for k in ['stage', 'status', 'sector'])]
        summary["breakdowns"] = {c: trimmed_df[c].value_counts().to_dict() for c in cat_cols}

        return json.dumps({
            "board_type": board_type,
            "metrics": summary,
            "data_quality": quality_report
        })

    def run(self, user_query: str, chat_history: list = None) -> str:
        """Executes query with fallback execution for string tool calls."""
        
        model_name = "llama-3.1-8b-instant"

        system_prompt = (
            "You are an executive BI Agent for Skylark Drones. "
            "You provide real-time business insights based on live monday.com data. "
            "Do NOT invent or hallucinate metrics. Rely ONLY on the board data retrieved."
        )

        messages = [{"role": "system", "content": system_prompt}]
        
        if chat_history and len(chat_history) > 0:
            last_msg = chat_history[-1]
            if last_msg["role"] in ["user", "assistant"]:
                messages.append({"role": last_msg["role"], "content": last_msg["content"][:300]})
            
        messages.append({"role": "user", "content": user_query})

        tools = [{
            "type": "function",
            "function": {
                "name": "get_board_data",
                "description": "Fetch live data from monday.com boards (deals or work_orders)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "board_type": {
                            "type": "string",
                            "enum": ["deals", "work_orders"],
                            "description": "Board to query"
                        }
                    },
                    "required": ["board_type"]
                }
            }
        }]

        # Turn 1: Check for Tool Request
        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=400
        )
        res_message = response.choices[0].message
        content = res_message.content or ""

        target_board = None

        # Case A: Model used standard Groq tool_calls API
        if res_message.tool_calls:
            for tool_call in res_message.tool_calls:
                fn_args = json.loads(tool_call.function.arguments)
                target_board = fn_args.get("board_type")

        # Case B: Model generated inline text function tags like <function=get_board_data>...
        elif "<function=get_board_data" in content:
            if "work_orders" in content or "work" in user_query.lower():
                target_board = "work_orders"
            else:
                target_board = "deals"

        # If a tool call was detected (via API or text tag), execute real fetch
        if target_board:
            tool_output = self._get_board_data_tool(target_board)
            
            synthesis_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": f"Retrieved live {target_board} board data from monday.com: {tool_output}"},
                {"role": "user", "content": "Analyze the retrieved metrics above and give a clear executive summary."}
            ]
            
            final_response = self.client.chat.completions.create(
                model=model_name,
                messages=synthesis_messages,
                max_tokens=600
            )
            return final_response.choices[0].message.content

        # Case C: Direct answer without tools
        return content