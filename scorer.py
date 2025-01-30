import json
import argparse
import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from evaluate import load
from sonar.inference_pipelines.text import TextToEmbeddingModelPipeline
from sonar.models.blaser.loader import load_blaser_model

if torch.cuda.is_available():
    device = torch.device("cuda")
    dtype = torch.float16

def load_data_with_ids(file_path):
    """Load 'numero_atto', 'assessorato', and 'risposta' fields from a JSONL file."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = {
            json.loads(line)["numero_atto"]: {
                "assessorato": json.loads(line).get("assessorato"),
                "risposta": json.loads(line).get("risposta", "")
            }
            for line in f
        }
    return data

def compute_metrics(true_values, predicted_values):
    """Compute metrics between true and predicted assessorato values."""
    accuracy = accuracy_score(true_values, predicted_values)
    precision = precision_score(true_values, predicted_values, average='weighted', zero_division=0)
    recall = recall_score(true_values, predicted_values, average='weighted', zero_division=0)
    f1_micro = f1_score(true_values, predicted_values, average='micro', zero_division=0)
    f1_macro = f1_score(true_values, predicted_values, average='macro', zero_division=0)
    
    return accuracy, precision, recall, f1_micro, f1_macro

def compute_rouge(reference_risposte, predicted_risposte):
    """Compute average ROUGE-1 scores between true and predicted 'risposta' values."""
    rouge_scorer = load("rouge", keep_in_memory=True)
    rouge_scores = [
        rouge_scorer.compute(predictions=[predicted], references=[reference])["rouge1"]
        for predicted, reference in zip(predicted_risposte, reference_risposte)
    ]
    return sum(rouge_scores) / len(rouge_scores) if rouge_scores else 0.0

def compute_bertscore(reference_risposte, predicted_risposte):
    """Compute BERTScore for the generated 'risposta' values."""
    bertscore_scorer = load("bertscore")
    bertscore_results = bertscore_scorer.compute(predictions=predicted_risposte, references=reference_risposte, lang="it")
    return sum(bertscore_results["f1"]) / len(bertscore_results["f1"]) if bertscore_results["f1"] else 0.0

def compute_blaser(reference_risposte, predicted_risposte):
    """Compute BLASER score for the generated 'risposta' values. https://github.com/facebookresearch/SONAR for intallation"""
    blaser_model = load_blaser_model("blaser_2_0_qe").to(device).eval()
    text_embedder = TextToEmbeddingModelPipeline(encoder="text_sonar_basic_encoder", tokenizer="text_sonar_basic_encoder", device=device)
    
    blaser_scores = []
    for ref, pred in zip(reference_risposte, predicted_risposte):
        ref_embs = text_embedder.predict([ref], source_lang="ita_Latn").to(device)
        pred_embs = text_embedder.predict([pred], source_lang="ita_Latn").to(device)
        blaser_scores.append(blaser_model(src=ref_embs, mt=pred_embs).item())
    
    return sum(blaser_scores) / len(blaser_scores) if blaser_scores else 0.0

def main(reference_file, answer_file, task):
    reference_data = load_data_with_ids(reference_file)
    answer_data = load_data_with_ids(answer_file)
    
    common_ids = set(reference_data.keys()).intersection(set(answer_data.keys()))
    if not common_ids:
        raise ValueError("No matching 'numero_atto' IDs found between the two files.")
    
    true_assessorato = [reference_data[atto_id].get("assessorato") for atto_id in common_ids]
    predicted_assessorato = [answer_data[atto_id].get("assessorato") for atto_id in common_ids]

    true_risposte = [reference_data[atto_id].get("risposta", "") for atto_id in common_ids]
    predicted_risposte = [answer_data[atto_id].get("risposta", "") for atto_id in common_ids]

    if task in ["all", "multiple_choice"]:
        if any(true_assessorato) and any(predicted_assessorato):
            accuracy, precision, recall, f1_micro, f1_macro = compute_metrics(true_assessorato, predicted_assessorato)
            print("Mutiple-Choice metrics. 'assessorato' comparison")
            print(f"Comparing {len(predicted_assessorato)} elements:")
            print(f"  Accuracy: {accuracy:.4f}")
    
    if task in ["all", "generation"]:
        if any(true_risposte) and any(predicted_risposte):
            print("Generation metrics. 'risposta' comparison")
            print(f"computing ROUGE-1 Score...")
            rouge1_score = compute_rouge(true_risposte, predicted_risposte)
            print(f"computing BERT Score F1...")
            bertscore_f1 = compute_bertscore(true_risposte, predicted_risposte)
            print(f"computing BLASER Score...")
            blaser_score = compute_blaser(true_risposte, predicted_risposte)
            print("\nMetrics for 'risposta' comparison")
            print(f"  Average ROUGE-1 Score: {rouge1_score:.4f}")
            print(f"  Average BERT Score F1: {bertscore_f1:.4f}")
            print(f"  Average BLASER Score: {blaser_score:.4f}")
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare 'assessorato' and 'risposta' fields in two JSONL files using matching 'numero_atto'.")
    parser.add_argument("reference_file", help="Path to the original JSONL file.")
    parser.add_argument("answer_file", help="Path to the modified JSONL file.")
    parser.add_argument("task", choices=["all", "generation", "multiple_choice"], help="Specify the task to compute metrics for.")
    args = parser.parse_args()

    main(args.reference_file, args.answer_file, args.task)

# example:
# python scorer.py reference_file.jsonl answer_file.jsonl all
