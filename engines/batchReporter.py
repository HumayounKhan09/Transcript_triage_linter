"""
File Name: batchReporter.py
Description: Engine to generate batch reports
"""
from Data_Classes.triageResult import triageResult as TriageResult
import pandas as pd

class batchReporter:
    def __init__(self):
        pass

    def count_reason_codes(self, results: list[TriageResult]) -> dict:
        #Count the occurrences of each reason code in the batch of triage results
        reason_code_count = {}
        for result in results:
            for rc in result.get_reason_codes():
                code = rc.get_code()

                if code in reason_code_count:
                    reason_code_count[code] += 1
                else:
                    reason_code_count[code] = 1
        return reason_code_count
    
    def calculate_escalation_rate(self, results: list[TriageResult]) -> float:
        #Calculate the percentage of escalated cases in the batch
        if len(results) == 0:
            return 0.0
        escalated_count = sum(1 for result in results if result._escalate)
        return (escalated_count / len(results)) * 100.0
    
    def get_top_intents(self, results: list[TriageResult], top_n: int = 3) -> list[tuple[str, int]]:
        #Get the top N intents from the batch of triage results
        intent_count = {}
        for result in results:
            intent = result._intent
            if intent in intent_count:
                intent_count[intent] += 1
            else:
                intent_count[intent] = 1
        #Sort intents by count and return top N
        sorted_intents = sorted(intent_count.items(), key=lambda item: item[1], reverse=True)
        return sorted_intents[:top_n]
    
    def common_patterns(self, results: list[TriageResult]) -> list[str]:
        """Identify common failure patterns in the batch of results"""
        patterns = {
            "payment + hardship": 0,
            "payment + dispute": 0,
            "third party + escalation": 0,
            "multiple escalation triggers": 0,
            "abusive without supervisor escalation": 0
        }
        
        for result in results:
            # Get list of reason code strings
            reason_codes = [rc.get_code() for rc in result.get_reason_codes()]
            
            # Pattern 1: Payment intent but customer mentions hardship
            if result._intent == "payment" and any(code in reason_codes for code in ["HARDSHIP_LANGUAGE", "LOAN_MOD_REQUEST"]):
                patterns["payment + hardship"] += 1
            
            # Pattern 2: Payment intent but disputing charges
            if result._intent == "payment" and "DISPUTE_FEE_OR_CHARGE" in reason_codes:
                patterns["payment + dispute"] += 1
            
            # Pattern 3: Third party caller with escalation issues
            if "THIRD_PARTY_CALLER" in reason_codes and result._escalate:
                patterns["third party + escalation"] += 1
            
            # Pattern 4: Multiple escalation triggers (high risk)
            if result._risk_level == "high":
                patterns["multiple escalation triggers"] += 1
            
            # Pattern 5: Abusive language but didn't request supervisor
            if "ABUSIVE_LANGUAGE" in reason_codes and "SUPERVISOR_REQUEST" not in reason_codes:
                patterns["abusive without supervisor escalation"] += 1
        
        # Return only patterns that occurred with their counts
        return [f"{pattern} ({count} occurrences)" for pattern, count in patterns.items() if count > 0]
        
    def build_report_dataframe(self, results: list[TriageResult]) -> pd.DataFrame:
        #Build a pandas DataFrame summarizing the batch of triage results
        data = []
        for result in results:
            data.append({
                "Intent": result._intent,
                "Escalated": result._escalate,
                "Risk Level": result._risk_level,
                "Reason Codes": ", ".join([rc.get_code() for rc in result.get_reason_codes()]),
                "Summary Bullets": " | ".join(result._summary_bullet)
            })
        df = pd.DataFrame(data)
        return df
    
 
    def generate_csv(self, results: list[TriageResult]) -> str:
        # Get all metrics
        total = len(results)
        esc_rate = self.calculate_escalation_rate(results)
        top_intents = self.get_top_intents(results)
        reason_counts = self.count_reason_codes(results)
        patterns = self.common_patterns(results)
        
        # Build summary section
        csv = "SUMMARY METRICS\n"
        csv += f"Total Transcripts,{total}\n"
        csv += f"Escalation Rate,{esc_rate:.1f}%\n"
        csv += f"Top Intent,{top_intents[0][0]} ({top_intents[0][1]})\n"
        top_reason = max(reason_counts, key=lambda k: reason_counts[k])
        csv += f"Top Reason Code,{top_reason} ({reason_counts[top_reason]})\n"
        if patterns:
            csv += f"Common Patterns,{'; '.join(patterns)}\n"
        
        csv += "\n"  # blank line
        
        # Build data rows
        csv += "filename,intent,escalate,risk_level,reason_codes,summary\n"
        for i, result in enumerate(results):
            codes = "|".join([rc.get_code() for rc in result.get_reason_codes()])
            summary = " | ".join(result._summary_bullet)
            csv += f"transcript_{i+1:03d}.txt,{result._intent},{result._escalate},{result._risk_level},{codes},{summary}\n"
        
        return csv
