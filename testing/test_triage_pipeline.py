"""
Test for triagePipeline.py to verify the rule engine integration
"""
import os
import tempfile
from engines.triagePipeline import TriagePipeline
from Data_Classes.triageResult import triageResult

def test_process_single():
    """Test processing a single transcript through the pipeline"""
    # Create a temporary transcript file with hardship language
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Customer: Hi, I lost my job and I'm struggling to make my mortgage payment of $2000.")
        temp_file = f.name
    
    try:
        # Create pipeline and process
        pipeline = TriagePipeline()
        result = pipeline.process_single(temp_file)
        
        # Verify result is a triageResult
        assert isinstance(result, triageResult)
        
        # Verify we got reason codes
        reason_codes = result.get_reason_codes()
        assert len(reason_codes) > 0, "Should have detected at least one reason code"
        
        # Verify intent was classified
        assert result._intent is not None
        
        # Verify escalation was evaluated
        assert isinstance(result._escalate, bool)
        assert result._risk_level in ["LOW", "MEDIUM", "HIGH"]
        
        # Verify entities were extracted
        assert result.entities is not None
        assert len(result.entities) > 0
        
        # Verify summary was generated
        assert isinstance(result._summary_bullet, list)
        
        print("✓ test_process_single passed")
        print(f"  - Intent: {result._intent}")
        print(f"  - Escalate: {result._escalate}")
        print(f"  - Risk Level: {result._risk_level}")
        print(f"  - Reason Codes: {[rc.get_code() for rc in reason_codes]}")
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

def test_process_batch():
    """Test processing multiple transcripts through the pipeline"""
    # Create temporary transcript files
    temp_files = []
    
    transcripts = [
        "Customer: I need to make a payment on my mortgage.",
        "Customer: I lost my job and can't afford my mortgage.",
        "Customer: I want to speak to a supervisor about this."
    ]
    
    try:
        for transcript_text in transcripts:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(transcript_text)
                temp_files.append(f.name)
        
        # Create pipeline and process batch
        pipeline = TriagePipeline()
        results = pipeline.process_batch(temp_files)
        
        # Verify we got results for all files
        assert len(results) == len(temp_files)
        
        # Verify all results are triageResult instances
        for result in results:
            assert isinstance(result, triageResult)
        
        print("✓ test_process_batch passed")
        print(f"  - Processed {len(results)} transcripts")
        
    finally:
        # Clean up temp files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    test_process_single()
    test_process_batch()
    print("\n✅ All tests passed!")
