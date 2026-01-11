"""
File Name: cli.py
Description: Command Line Interface
"""

import argparse
import os
import sys
import glob
import json
import time

# Ensure package imports work when running `python cli.py` from inside `engines/`.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from engines.batchReporter import batchReporter
from engines.triageResult import TriagePipeline

class CLI:
    def __init__(self):
        self.pipeline = TriagePipeline()
        self.batch_reporter = batchReporter()
    
    def parse_args(self):
        parser = argparse.ArgumentParser(description="Transcript Triage Linter")
        
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--single', type=str, help='Process single transcript file')
        group.add_argument('--batch', action='store_true', help='Process all transcripts')
        group.add_argument('--list', action='store_true', help='List available transcripts')
        
        parser.add_argument('--format', choices=['json', 'csv', 'both'], 
                          help='Output format (required for --single and --batch)')
        
        return parser.parse_args()
    
    def list_transcripts(self):
        # Find all .txt files in transcripts/
        files = glob.glob('transcripts/*.txt')

        # Display numbered list
        print("Available Transcript Files:")
        for i, file in enumerate(files, start=1):
            print(f"{i}. {os.path.basename(file)}")

        # Show usage examples
        print("\nUsage Examples:")
        print("  python cli.py --single transcripts/example.txt --format json")
        print("  python cli.py --batch --format csv")
        print("  python cli.py --list")
        return
    
    def validate_args(self, args):
        # Check if format is provided when needed
        if (args.single or args.batch) and not args.format:
            print("✗ Error: --format is required when using --single or --batch")
            return False
        # Check if single file exists
        if args.single and not os.path.isfile(args.single):
            print(f"✗ Error: Transcript file not found: {args.single}")
            return False
        #Check if transcripts directory exists
        if args.batch and not os.path.isdir('transcripts'):
            print("✗ Error: transcripts/ directory not found for batch processing")
            return False
        return True
    
    def run_single_mode(self, file_path, format):
        # Call pipeline.process_single()
        detail = self.pipeline.process_single(file_path)
        if format not in ("json", "csv", "both"):
            raise ValueError(f"Unsupported format: {format}")
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        if format in ("json", "both"):
            output_path = os.path.join("results", f"{base_name}.json")
            with open(output_path, "w") as f:
                json.dump(detail.to_json(), f, default=lambda obj: obj.__dict__)
        if format in ("csv", "both"):
            output_path = os.path.join("results", f"{base_name}.csv")
            csv_string = self.batch_reporter.generate_csv([detail])
            with open(output_path, "w") as f:
                f.write(csv_string)
        self.print_summary(detail)
        return detail
    
    def run_batch_mode(self, format):
        """Process all transcripts in batch"""
        files = [
            entry.path
            for entry in os.scandir("transcripts")
            if entry.is_file() and entry.name.endswith(".txt")
        ]
        batch_results = self.pipeline.process_batch(files)
        if format not in ("json", "csv", "both"):
            raise ValueError(f"Unsupported format: {format}")
        if format in ("json", "both"):
            output_path = os.path.join("results", "batch_results.json")
            payload = [
                {"filename": os.path.basename(path), **result.to_json()}
                for path, result in zip(files, batch_results)
            ]
            with open(output_path, "w") as f:
                json.dump(payload, f, default=lambda obj: obj.__dict__)
        if format in ("csv", "both"):
            output_path = os.path.join("results", "batch_results.csv")
            csv_string = self.batch_reporter.generate_csv(batch_results)
            with open(output_path, "w") as f:
                f.write(csv_string)
        self.print_batch_stats(batch_results)
        return batch_results
    
    def run_single_mode_safe(self, file_path, format):
        """Run single mode with error handling"""
        try:
            return self.run_single_mode(file_path, format)
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            print("Check that the transcript file is properly formatted.")
            return None
    
    def run_batch_mode_safe(self, format):
        """Run batch mode with error handling"""
        try:
            files = glob.glob('transcripts/*.txt')
            if not files:
                print("✗ No transcript files found in transcripts/ directory")
                print("Add .txt files to transcripts/ and try again")
                return None
            
            return self.run_batch_mode(format)
        except Exception as e:
            print(f"✗ Error during batch processing: {e}")
            print("Some files may have been processed successfully.")
            return None
    
    def save_json(self, result, filename):
        """Save TriageResult as JSON file"""
        json_payload = result.to_json() if hasattr(result, "to_json") else result
        os.makedirs("results", exist_ok=True)
        output_path = os.path.join("results", filename)
        with open(output_path, "w") as f:
            json.dump(json_payload, f, default=lambda obj: obj.__dict__)
    
    def save_csv(self, csv_string, filename):
        """Save CSV string to file"""
        os.makedirs("results", exist_ok=True)
        output_path = os.path.join("results", filename)
        with open(output_path, "w") as f:
            f.write(csv_string)
    
    def print_summary(self, result):
        """Print single result summary to terminal"""
        reason_codes = result.get_reason_codes() if hasattr(result, "get_reason_codes") else []
        reason_codes_display = ", ".join(rc.get_code() for rc in reason_codes) if reason_codes else "None"
        print("\nSummary:")
        print(f"Intent: {result._intent}")
        print(f"Escalate: {result._escalate}")
        print(f"Risk Level: {result._risk_level}")
        print(f"Reason Codes: {reason_codes_display}")
    
    def print_batch_stats(self, results):
        """Print aggregate batch statistics to terminal"""
        total = len(results)
        if total == 0:
            print("\nBatch Statistics:")
            print("Total processed: 0")
            print("Escalation rate: 0.0%")
            print("Top intents: None")
            return

        escalated_count = 0
        intent_counts = {}
        for result in results:
            if result._escalate:
                escalated_count += 1
            intent = result._intent
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        esc_rate = (escalated_count / total) * 100.0
        top_items = sorted(intent_counts.items(), key=lambda item: item[1], reverse=True)[:3]
        top_intents = ", ".join(f"{intent} ({count})" for intent, count in top_items) if top_items else "None"

        print("\nBatch Statistics:")
        print(f"Total processed: {total}")
        print(f"Escalation rate: {esc_rate:.1f}%")
        print(f"Top intents: {top_intents}")

    def format_duration(self, elapsed_seconds):
        """Format duration in ms or s depending on length."""
        if elapsed_seconds < 1:
            return f"{round(elapsed_seconds * 1000)} ms"
        return f"{elapsed_seconds:.2f} s"
    
    def wait_for_exit(self):
        """No-op pause for CLI completion (kept for compatibility)."""
        return
    
    def main(self):
        try:
            # Normalize CWD to repo root so relative paths (transcripts/, results/) work.
            os.chdir(ROOT_DIR)
            # Parse arguments
            args = self.parse_args()
            
            # Handle list mode
            if args.list:
                self.list_transcripts()
                self.wait_for_exit()
                return
            
            # Validate arguments
            if not self.validate_args(args):
                self.wait_for_exit()
                return
            
            # Create results directory
            os.makedirs('results', exist_ok=True)
            
            # Route to correct mode with error handling
            if args.single:
                start = time.perf_counter()
                result = self.run_single_mode_safe(args.single, args.format)
                if result is not None:
                    elapsed = time.perf_counter() - start
                    duration = self.format_duration(elapsed)
                    print(f"\nCompleted 1 transcript in {duration}.")
            elif args.batch:
                start = time.perf_counter()
                results = self.run_batch_mode_safe(args.format)
                if results is not None:
                    elapsed = time.perf_counter() - start
                    duration = self.format_duration(elapsed)
                    total = len(results)
                    label = "transcript" if total == 1 else "transcripts"
                    print(f"\nCompleted {total} {label} in {duration}.")
            
            # Success message
            print("\n✓ Process completed successfully!")
            self.wait_for_exit()
            
        except KeyboardInterrupt:
            print("\n\nProcess interrupted by user. Exiting gracefully...")
            return
        except Exception as e:
            print(f"\n✗ Unexpected error: {e}")
            print("Please report this issue if it persists.")
            self.wait_for_exit()


if __name__ == "__main__":
    cli = CLI()
    cli.main()
