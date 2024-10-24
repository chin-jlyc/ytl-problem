import json
import re

def normalize_section(section: str) -> str:
    """Normalize section labels for comparison."""
    # Remove brackets and spaces
    section = section.replace('[', '').replace(']', '').strip()
    
    # Convert to lowercase
    section = section.lower()
    
    # Remove 'pg' or 'page' prefix and clean up
    section = re.sub(r'^pg\s*', '', section)
    section = re.sub(r'^page\s*', '', section)
    
    # Handle ranges with dashes or periods
    section = section.replace('.', '-')
    
    # Clean up any multiple spaces or dashes
    section = re.sub(r'\s+', ' ', section)
    section = re.sub(r'-+', '-', section)
    
    return section.strip()

def score_sections(submission_data: dict, ground_truth: dict) -> dict:
    # Extract ground truth sections
    ground_truth_sections = set(
        normalize_section(item["section"]) 
        for item in ground_truth["Goal1"]["RiskManagementInTechnology_v2023"]
    )
    
    # Extract submission sections
    submission_sections = set(
        normalize_section(item["new_section_label"])
        for item in submission_data["part_1"]["rmit"]
        if "new_section_label" in item
    )
    
    # Calculate matches
    matches = submission_sections.intersection(ground_truth_sections)
    false_positives = submission_sections - ground_truth_sections
    false_negatives = ground_truth_sections - matches
    
    # Calculate metrics
    precision = len(matches) / len(submission_sections) if submission_sections else 0
    recall = len(matches) / len(ground_truth_sections) if ground_truth_sections else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "matched_sections": sorted(list(matches)),
        "false_positives": sorted(list(false_positives)),
        "false_negatives": sorted(list(false_negatives)),
        "num_matches": len(matches),
        "num_submission_sections": len(submission_sections),
        "num_ground_truth_sections": len(ground_truth_sections)
    }

def main():
    # Load HOCK's submission
    with open('eval/hock/HOCKsubmission.json', 'r') as f:
        hock_submission = json.load(f)
    
    # Ground truth
    ground_truth = {
        "Goal1": {
            "RiskManagementInTechnology_v2023": [
                {"section": "Pg 5.2", "change": "Inclusion of the definition of cloud service providers"},
                {"section": "Pg 7.1", "change": "Updated superseded guidelines with different effective dates"},
                {"section": "Pg 10.49 - 10.52", "change": "Introduction of a new Appendix 10"},
                {"section": "Pg 10.68", "change": "Enforcement of MFA becomes mandatory"},
                {"section": "Pg 10.70", "change": "Introduction of additional requirements for MFA security controls"},
                {"section": "Pg 15.1 - 15.5", "change": "Updated introduction to cloud consultation and notification related to cloud services"},
                {"section": "Pg 16.1", "change": "Updated requirements on gap analysis and assessment"},
                {"section": "Appendix 7", "change": "Updated risk assessment report to include cloud services"},
                {"section": "Appendix 8", "change": "Updated confirmation template to include cloud services"},
                {"section": "Appendix 10", "change": "New appendix with guidance on managing cloud risks"}
            ]
        }
    }
    
    results = score_sections(hock_submission, ground_truth)
    
    print(f"Number of matches: {results['num_matches']}")
    print(f"Number of submission sections: {results['num_submission_sections']}")
    print(f"Number of ground truth sections: {results['num_ground_truth_sections']}")
    print(f"\nPrecision: {results['precision']:.2f}")
    print(f"Recall: {results['recall']:.2f}")
    print(f"F1 Score: {results['f1']:.2f}")
    
    print("\nMatched sections:")
    for section in results['matched_sections']:
        print(f"- {section}")
    
    print("\nMissed sections (in ground truth but not submission):")
    for section in results['false_negatives']:
        print(f"- {section}")
    
    print("\nExtra sections (in submission but not ground truth):")
    for section in results['false_positives']:
        print(f"- {section}")
    
    # Print normalized versions for debugging
    print("\nNormalized Ground Truth sections:")
    for item in ground_truth["Goal1"]["RiskManagementInTechnology_v2023"]:
        print(f"{item['section']} -> {normalize_section(item['section'])}")
    
    print("\nNormalized Submission sections:")
    for item in hock_submission["part_1"]["rmit"]:
        if "new_section_label" in item:
            print(f"{item['new_section_label']} -> {normalize_section(item['new_section_label'])}")

if __name__ == "__main__":
    main()