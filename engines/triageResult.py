"""
File Name: triageResult.py
Description: This is the main driver of the entire linter
"""



from Data_Classes.triageResult import triageResult as TriageResult
from engines.transcriptParser import transcriptParser
from engines.ruleEngine import ruleEngine as RuleEngine
from engines.entityExtractor import entityExtractor as EntityExtractor
from engines.intentClassifier import intentClassifier as IntentClassifier
from engines.escalationEngine import escalationEngine as EscalationEngine
from engines.summaryGenerator import summaryGenerator as SummaryGenerator

class TriagePipeline:
    def __init__(self):
        self.parser = transcriptParser()
        self.entity_extractor = EntityExtractor()
        self.intent = IntentClassifier()
        self.escalate = EscalationEngine()
        self.summary = SummaryGenerator()
        
    def process_single(self, file_path: str) -> TriageResult:
        """Process a single transcript file and return TriageResult"""
        #Getting the file (need to tie error in with CLI)
        try: 
            with open(file_path, 'r') as f:
                raw_text = f.read()
        except FileNotFoundError: 
            raise FileNotFoundError(f"Transcript file not found: {file_path}") 
        
        #  Parse transcript
        transcript = self.parser.parse_transcript(raw_text)

        # Run through rule engine
        rules = RuleEngine(transcript)
        reason_codes = rules.apply_rules()

        # Extract entities
        entity = self.entity_extractor.extract_all_entities(transcript)
        # Classify intent
        intents = self.intent.classify(reason_codes)
        # Determine escalation
        escalation_result = self.escalate.evaluate_escalation(reason_codes)
        escalations = escalation_result["escalation_needed"]
        risk_level = escalation_result["risk_level"]

        # Generate summary
        summary = self.summary.generate_bullets(intents, entity, reason_codes)
        # Create and return TriageResult
        triage_res= TriageResult(intents,escalations,risk_level,reason_codes,entity,summary)
        return triage_res
    
    def process_batch(self, file_paths: list) -> list[TriageResult]:
        """Process multiple transcripts and return list of TriageResults"""
        # Loop through file_paths
        results = []
        for path in file_paths:
            triage_result = self.process_single(path)
            results.append(triage_result)
        return results
