"""
File Name: cli.py
Description: Command Line Interface
"""

import argparse
import os
import glob
import json
from engines.batchReporter import batchReporter


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
        """Display all available transcript files and exit"""
        # TODO: Find all .txt files in transcripts/
        # TODO: Display numbered list
        # TODO: Show usage examples
        pass
    
    def validate_args(self, args):
        """Validate arguments before processing"""
        # TODO: Check if format is provided when needed
        # TODO: Check if single file exists
        # TODO: Check if transcripts directory exists
        # TODO: Return True if valid, False otherwise
        pass
    
    def run_single_mode(self, file_path, format):
        """Process single transcript file"""
        # TODO: Call pipeline.process_single()
        # TODO: Check format argument
        # TODO: Save outputs accordingly
        # TODO: Print summary
        pass
    
    def run_batch_mode(self, format):
        """Process all transcripts in batch"""
        # TODO: Find all .txt files in transcripts/
        # TODO: Call pipeline.process_batch()
        # TODO: Check format argument
        # TODO: Save outputs accordingly
        # TODO: Print batch stats
        pass
    
    def run_single_mode_safe(self, file_path, format):
        """Run single mode with error handling"""
        try:
            self.run_single_mode(file_path, format)
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")
            print("Check that the transcript file is properly formatted.")
    
    def run_batch_mode_safe(self, format):
        """Run batch mode with error handling"""
        try:
            files = glob.glob('transcripts/*.txt')
            if not files:
                print("✗ No transcript files found in transcripts/ directory")
                print("Add .txt files to transcripts/ and try again")
                return
            
            self.run_batch_mode(format)
        except Exception as e:
            print(f"✗ Error during batch processing: {e}")
            print("Some files may have been processed successfully.")
    
    def save_json(self, result, filename):
        """Save TriageResult as JSON file"""
        # TODO: Convert result to JSON
        # TODO: Write to results/ directory
        pass
    
    def save_csv(self, csv_string, filename):
        """Save CSV string to file"""
        # TODO: Write CSV string to results/ directory
        pass
    
    def print_summary(self, result):
        """Print single result summary to terminal"""
        # TODO: Display intent, escalate, risk_level, reason_codes
        pass
    
    def print_batch_stats(self, results):
        """Print aggregate batch statistics to terminal"""
        # TODO: Display total processed, escalation rate, top intents
        pass
    
    def wait_for_exit(self):
        """Wait for user to press Enter before exiting"""
        input("\nPress Enter to exit...")
    
    def main(self):
        try:
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
                self.run_single_mode_safe(args.single, args.format)
            elif args.batch:
                self.run_batch_mode_safe(args.format)
            
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
