import json
import argparse
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_data_with_ids(file_path):
    """Load 'numero_atto' and 'assessorato' fields from a JSONL file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = {json.loads(line)["numero_atto"]: json.loads(line)["assessorato"] for line in f}
    return data

def compute_metrics(true_values, predicted_values):
    """Compute metrics between true and predicted assessorato values."""
    # Compute metrics
    accuracy = accuracy_score(true_values, predicted_values)
    precision = precision_score(true_values, predicted_values, average='weighted', zero_division=0)
    recall = recall_score(true_values, predicted_values, average='weighted', zero_division=0)
    f1_micro = f1_score(true_values, predicted_values, average='micro', zero_division=0)
    f1_macro = f1_score(true_values, predicted_values, average='macro', zero_division=0)
    
    return accuracy, precision, recall, f1_micro, f1_macro

def main(original_file, modified_file):
    # Load data from both files
    original_data = load_data_with_ids(original_file)
    modified_data = load_data_with_ids(modified_file)
    
    # Get the intersection of keys (numero_atto)
    common_ids = set(original_data.keys()).intersection(set(modified_data.keys()))
    
    if not common_ids:
        raise ValueError("No matching 'numero_atto' IDs found between the two files.")
    
    # Extract assessorato values for matching IDs
    true_assessorato = [original_data[atto_id] for atto_id in common_ids]
    predicted_assessorato = [modified_data[atto_id] for atto_id in common_ids]

    # Compute metrics
    accuracy, precision, recall, f1_micro, f1_macro = compute_metrics(true_assessorato, predicted_assessorato)

    # Print results
    print("Metrics for 'assessorato' comparison")
    print(f"Comparing {len(predicted_assessorato)} elements:")
    print(f"  Accuracy: {accuracy:.4f}")

    #TODO de-comment the following lines if interested in other metrics.
    #print(f"  Precision: {precision:.4f}")
    #print(f"  Recall: {recall:.4f}")
    #print(f"  F1 Micro: {f1_micro:.4f}")
    #print(f"  F1 Macro: {f1_macro:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare 'assessorato' field in two JSONL files using matching 'numero_atto'.")
    parser.add_argument("original_file", help="Path to the original JSONL file.")
    parser.add_argument("modified_file", help="Path to the modified JSONL file.")
    args = parser.parse_args()

    main(args.original_file, args.modified_file)


# example:
# python scorer.py reference_file.jsonl answer_file.jsonl