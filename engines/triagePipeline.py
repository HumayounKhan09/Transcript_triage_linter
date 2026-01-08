"""
File Name: triagePipeline.py
Description: Pipeline that orchestrates all engines
"""

from Data_Classes.transcript import transcript as Transcript
from Data_Classes.triageResult import triageResult as TriageResult
from engines.transcriptParser import transcriptParser as TranscriptParser
from engines.ruleEngine import ruleEngine as RuleEngine
from engines.entityExtractor import entityExtractor as EntityExtractor
from engines.intentClassifier import intentClassifier as IntentClassifier
from engines.escalationEngine import escalationEngine as EscalationEngine
from engines.summaryGenerator import summaryGenerator as SummaryGenerator

class TriagePipeline:
    def __init__(self):
        self.parser = TranscriptParser()
        self.entity_extractor = EntityExtractor()
        # Note: rule_engine, intent_classifier, escalation_engine, summary_generator
        # will be instantiated per transcript since some take transcript in __init__
    
    def process_single(self, file_path: str) -> TriageResult:
        """Process a single transcript file and return TriageResult"""
        # Parse transcript - read file and parse
        with open(file_path, 'r') as f:
            raw_text = f.read()
        transcript = self.parser.parse_transcript(raw_text)
        
        # Initialize engines
        rule_engine = RuleEngine(transcript)
        intent_classifier = IntentClassifier()
        escalation_engine = EscalationEngine()
        summary_generator = SummaryGenerator()
        
        # Run through rule engine
        reason_codes = rule_engine.apply_rules()
        
        # Extract entities
        entities = self.entity_extractor.extract_all_entities(transcript)
        
        # Classify intent
        intent = intent_classifier.classify(reason_codes)
        
        # Determine escalation
        escalation_result = escalation_engine.evaluate_escalation(reason_codes)
        escalation_needed = escalation_result["escalation_needed"]
        risk_level = escalation_result["risk_level"]
        
        # Generate summary
        summary_bullets = []
        payment_bullet = summary_generator.extract_payment_bulllet(entities)
        if payment_bullet:
            summary_bullets.append(payment_bullet)
        
        # Create and return TriageResult
        return TriageResult(
            intent=intent,
            escalate=escalation_needed,
            risk_level=risk_level,
            reason_codes=reason_codes,
            entities=[entities],
            summary_bullet=summary_bullets
        )
    
    def process_batch(self, file_paths: list) -> list:
        """Process multiple transcripts and return list of TriageResults"""
        results = []
        for file_path in file_paths:
            result = self.process_single(file_path)
            results.append(result)
        return results


