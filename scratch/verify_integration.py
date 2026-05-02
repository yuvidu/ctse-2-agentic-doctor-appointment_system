from pipeline import run_system
import json

def test_full_pipeline():
    # We'll use a specific input that we know matches sample_schedules.json
    user_input = "I want to book a cardiology appointment on 2026-05-02"
    
    print(f"Running pipeline with input: {user_input}")
    result = run_system(user_input)
    
    print("\nPipeline Result:")
    print(json.dumps(result, indent=2))
    
    if result.get("status") == "confirmed":
        print("\nSUCCESS: Appointment confirmed!")
        print(f"Booking ID: {result['appointment'].get('id')}")
    else:
        print(f"\nFAILURE: Status is {result.get('status')}")
        if result.get("errors"):
            print(f"Errors: {result['errors']}")

if __name__ == "__main__":
    test_full_pipeline()
