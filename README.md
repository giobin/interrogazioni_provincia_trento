Questo README descrive i task di multiple choice e generazione ideati sul dataset di interrogazioni della provincia di Trento.  

## Contenuto della cartella "dataset"

La cartella `dataset` contiene 3 file: 

- `train_set_interrogazioni_trento.jsonl` (1264 elementi)
- `validation_set_interrogazioni_trento.jsonl` (500 elementi)
- `test_set_interrogazioni_trento.jsonl` (750 elementi)

Questi 3 file contengono elementi differenti tra di essi.  
Ogni riga dei file è un sample in formato JSON. Qui di seguito un esempio:

```json
{
    "domanda": "CONSIGLIO DELLA PROVINCIA AUTONOMA DI TRENTO\n\n ...",
    "risposta": "**Assessore all’artigianato, commercio, promozione**\n**sport e turismo**\nVia Romagnosi, 9 – 38122 TRENTO\n**T +39 0461 495929 F +39 0461 499264** ...,"
    "anno": 2021,
    "numero_atto": "1597332",
    "data_atto": "2021-04-21T00:00:00",
    "materia": "4.4. Opere pubbliche",
    "oggetto": "Tempi di presentazione dello studio di sostenibilitÃ  e di realizzazione dell'Ice rink di PinÃ¨ ...",
    "primo_firmatario": "Dallapiccola Michele",
    "url_domanda": "https://www.consiglio.provincia.tn.it/doc/IDAP_1597351.pdf",
    "url_risposta": "https://www.consiglio.provincia.tn.it/doc/IDAP_1605290.pdf",
    "assessorato": "assessorato all’artigianato, commercio, promozione sport e turismo"
}
```

In particolare il campo `assessorato` è estratto dal campo `risposta`, il quale a sua volta è il testo contenuto nel file `risposta.pdf` del dataset originale.  
Il campo `assessorato` può avere solo uno dei valori dei seguenti mini-cluster:

- **Cluster istruzione**  
    - "assessorato all’istruzione, cultura e sport, politiche per la famiglia, per i giovani e le pari opportunità"  
    - "assessorato all’istruzione, università e cultura"

- **Cluster salute**  
    - "assessorato alla salute, politiche sociali, disabilità e famiglia"  
    - "assessorato alla salute, politiche sociali e cooperazione"  
    - "assessorato alla salute, politiche sociali, disabilità e famiglia sociali"

- **Cluster enti e consiglio**  
    - "assessorato agli enti locali e rapporti con il consiglio provinciale"

- **Cluster sviluppo economico**  
    - "assessorato allo sviluppo economico, lavoro, università e ricerca"  
    - "assessorato allo sviluppo economico, lavoro, università, ricerca"  
    - "assessorato allo sviluppo economico, ricerca e lavoro"

- **Cluster artigianato**  
    - "assessorato all’artigianato, commercio, turismo, foreste, caccia e pesca"  
    - "assessorato all’artigianato, commercio, promozione sport e turismo"  
    - "assessorato all’artigianato, commercio, promozione, sport e turismo"

- **Cluster agricoltura**  
    - "assessorato all’agricoltura, foreste, turismo, promozione, caccia e pesca"  
    - "assessorato all’agricoltura, foreste, caccia e pesca"  
    - "assessorato all’agricoltura, promozione dei prodotti trentini, ambiente, difesa idrogeologica e enti locali"

- **Cluster enti locali**  
    - "assessorato agli enti locali, cooperazione internazionale, trasporti e mobilità"

- **Cluster urbanistica**  
    - "assessorato all’urbanistica, energia e trasporti"

- **Cluster politiche per la casa**  
    - "assessorato alle politiche per la casa, patrimonio, demanio e promozione della conoscenza dell’autonomia"

- **Cluster presidente**  
    - "presidente"

Si noti che alcuni assessorati hanno nomi molto simili. Non sono stati normalizzati ulteriormente per semplicità e aderenza con i file originali `.pdf` dove queste varianti esistono. Si creano quindi 10 mini-cluster in cui, ad esempio, l'assessorato alla salute può avere 3 nomi diversi.

## TASK MULTIPLE CHOICE

Il task consiste nello scegliere il campo `assessorato` tra 10 possibilità, dato in input al modello (e.g. LLM) il campo `domanda`.  
Il modello deve quindi stimare quale dei 10 assessorati prenderà in gestione la questione con più probabilità.

Tra le 10 possibilità, oltre all'assessorato corretto, ci sono 9 distrattori scelti randomicamente tra quelli elencati sopra, pescando un solo elemento da ognuno dei mini-cluster.

## TASK GENERAZIONE

Il task consiste nel generare una `risposta` dato in input al modello LLM il campo `domanda`.

---
## SCORER

Lo scorer permette di ottenere le metriche di valutazione per i due task (e.g. Accuracy, Rouge) e si aspetta due file in input:

- `reference_file`: il file con le gold labels, tipicamente il test set stesso. Il file deve essere in formato `.jsonl` e avere la stessa struttura presentata precedentemente.
- `answer_file`: il file con le scelte del modello e/o la risposta generata. Lo scorer compara il campo `assessorato` di ogni elemento di questo file con il campo `assessorato` del `reference_file` per calcolare le metriche del task multiple choice. Compara invece i campi `risposta` per valutare le metriche del task di generzione.
- `task`: il task da valutare. Le possibili scelte sono `generation`, `multiple_choice` and `all`.

Lo scorer stampa le metriche su standard output.  

`scorer.py` è stato testato con Python 3.12 e richiede la libreria **scikit-learn**.  
Per lanciare lo script esegui:

```bash
python scorer.py reference_file.jsonl answer_file.jsonl all
```

---

## BASELINES

Abbiamo calcolato alcune baselines usando due LLMs con capacità linguistiche per l'italiano:  
**`google/gemma-2-9b-it`** e **`swap-uniba/LLaMAntino-3-ANITA-8B-Inst-DPO-ITA`**.

sul task multiple choice:

| Modello                                                | Accuracy Zero-shot | Accuracy 1-shot |
|--------------------------------------------------------|--------------------|-----------------|
| swap-uniba/LLaMAntino-3-ANITA-8B-Inst-DPO-ITA          | 0.653              | 0.872           |
| google/gemma-2-9b-it                                   | 0.592              | 0.733           |
| most frequent                                          | 0.425              |                 |
| random                                                 | 0.100              |                 |

- La baseline **"most frequent"** dà come risposta l'assessorato più frequente tra gli elementi del test set.  
- La baseline **random** ha il 10% di accuracy, scegliendo randomicamente tra 10 possibilità.  

Per i modelli LLMs abbiamo usato la libreria **[lm-eval](https://github.com/EleutherAI/lm-evaluation-harness)** per ottenere l'accuracy in setting di 0 e 1-shot.  
Il prompt che abbiamo usato per il task multiple choice è:  

```plaintext
{{domanda}}


Quale assessorato meglio si addice a rispondere alla questione?
```

Per il task di generazione il prompt cha abbiamo usato è:

```plaintext
Rispondi in maniera esaustiva alla seguente interrogazione rivolta al Consiglio della Provincia Autonoma di Trento da un consigliere: '{{domanda}}'\nRisposta:
```

| Modello                                                | Rouge-1 | Rouge-2 |
|--------------------------------------------------------|---------|---------|
| swap-uniba/LLaMAntino-3-ANITA-8B-Inst-DPO-ITA          | 0.3273  | 0.0828  |
| google/gemma-2-9b-it                                   | 0.3312  | 0.0833  |
