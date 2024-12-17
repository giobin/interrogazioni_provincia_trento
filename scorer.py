import json
import argparse
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from evaluate import load

def load_data_with_ids(file_path):
    """Load 'numero_atto', 'assessorato', and 'risposta' fields from a JSONL file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = {
            json.loads(line)["numero_atto"]: {
                "assessorato": json.loads(line).get("assessorato"),  # Use get to handle missing 'assessorato'
                "risposta": json.loads(line).get("risposta", "")  # Default to empty string if 'risposta' is missing
            }
            for line in f
        }
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

def compute_rouge(reference_risposte, predicted_risposte):
    """Compute ROUGE-1 scores between true and predicted 'risposta' values."""
    rouge_scorer = load("rouge", keep_in_memory=True)
    rouge_scores = rouge_scorer.compute(predictions=predicted_risposte, references=reference_risposte)
    return rouge_scores["rouge1"]

def main(reference_file, answer_file, task):
    # Load data
    reference_data = load_data_with_ids(reference_file)
    answer_data = load_data_with_ids(answer_file)
    
    # Get the intersection of keys (numero_atto)
    common_ids = set(reference_data.keys()).intersection(set(answer_data.keys()))

    if not common_ids:
        raise ValueError("No matching 'numero_atto' IDs found between the two files.")

    # Extract assessorato and risposta values for matching IDs
    true_assessorato = [reference_data[atto_id].get("assessorato") for atto_id in common_ids]
    predicted_assessorato = [answer_data[atto_id].get("assessorato") for atto_id in common_ids]

    true_risposte = [reference_data[atto_id].get("risposta", "") for atto_id in common_ids]
    predicted_risposte = [answer_data[atto_id].get("risposta", "") for atto_id in common_ids]

    if task in ["all", "multiple_choice"]:
        if any(true_assessorato) and any(predicted_assessorato):
            accuracy, precision, recall, f1_micro, f1_macro = compute_metrics(true_assessorato, predicted_assessorato)

            print("Metrics for the multiple choice task")
            print(f"Comparing {len(predicted_assessorato)} elements:")
            print(f"  Accuracy: {accuracy:.4f}")

            # TODO: De-comment the following lines if interested in other metrics.
            # print(f"  Precision: {precision:.4f}")
            # print(f"  Recall: {recall:.4f}")
            # print(f"  F1 Micro: {f1_micro:.4f}")
            # print(f"  F1 Macro: {f1_macro:.4f}")

    if task in ["all", "generation"]:
        if any(true_risposte) and any(predicted_risposte):
            rouge1_score = compute_rouge(true_risposte, predicted_risposte)
            print("\nMetrics for the generation task")
            print(f"  ROUGE-1 Score: {rouge1_score:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare 'assessorato' and 'risposta' fields in two JSONL files using matching 'numero_atto'.")
    parser.add_argument("reference_file", help="Path to the original JSONL file.")
    parser.add_argument("answer_file", help="Path to the modified JSONL file.")
    parser.add_argument("task", choices=["all", "generation", "multiple_choice"], help="Specify the task to compute metrics for.")
    args = parser.parse_args()

    main(args.reference_file, args.answer_file, args.task)

# example:
# python scorer.py reference_file.jsonl answer_file.jsonl all
