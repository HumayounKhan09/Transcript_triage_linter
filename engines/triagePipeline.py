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
        # Parse transcript
        transcript = self.parser.parse(file_path)
        
        # Initialize engines that need transcript
        rule_engine = RuleEngine(transcript)
        intent_classifier = IntentClassifier(transcript)
        escalation_engine = EscalationEngine(transcript)
        summary_generator = SummaryGenerator(transcript)
        
        # Run through rule engine
        rule_violations = rule_engine.check_rules()
        
        # Extract entities
        entities = self.entity_extractor.extract(transcript)
        
        # Classify intent
        intent = intent_classifier.classify()
        
        # Determine escalation
        escalation_needed = escalation_engine.should_escalate()
        
        # Generate summary
        summary = summary_generator.generate()
        
        # Create and return TriageResult
        return TriageResult(
            transcript=transcript,
            rule_violations=rule_violations,
            entities=entities,
            intent=intent,
            escalation_needed=escalation_needed,
            summary=summary
        )
    
    def process_batch(self, file_paths: list) -> list:
        """Process multiple transcripts and return list of TriageResults"""
        # TODO: Loop through file_paths
        # TODO: Call process_single() for each
        # TODO: Collect all TriageResults in a list
        # TODO: Return the list
        pass


