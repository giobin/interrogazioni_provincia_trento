Questo README descrive i task di multiple choice e generazione ideati sul dataset di interrogazioni della provincia di Trento.  

## Contenuto della cartella "dataset"

La cartella `dataset` contiene 4 files: 

- `train_set_interrogazioni_trento.jsonl` (1264 elementi)
- `validation_set_interrogazioni_trento.jsonl` (500 elementi)
- `test_set_interrogazioni_trento.jsonl` (750 elementi)
- `test_ XVII_legislatura.jsonl` (239 elementi)

Ogni riga dei file è un sample in formato JSON. Qui di seguito un esempio:

```json
{"anno": 2023,
"numero_atto": "3003270",
"data_atto": "2023-12-01T00:00:00",
"materia": "4.8.3. Inquinamento",
"oggetto": "Sollecitare l'APPA a monitorare l'inquinamento elettromagnetico diffondendo i dati raccolti",
"primo_firmatario": "Coppola Lucia",
"url_domanda": "https://www.consiglio.provincia.tn.it/doc/IDAP_1777156.pdf",
"url_risposta": "https://www.consiglio.provincia.tn.it/doc/IDAP_1778107.pdf",
"domanda": "# CONSIGLIO DELLA PROVINCIA AUTONOMA DI TRENTO\n\n Gruppo Alleanza Verdi e Sinistra\n\nTrento, 1 dicembre 2023\n\nPer\n\nPresidente del Consiglio Provinciale\n\nSEDE\n\nInterrogazione a risposta scritta n. 04\n\n# Monitorare l’inquinamento elettromagnetico\n\n Diversi cittadini residenti a Trento, nella zona circostante la rotonda di via Maccani,\n\n ...",
"risposta": "**Assessorato all’agricoltura, promozione dei prodotti trentini,**\n**ambiente, difesa idrogeologica e enti locali**\n\nVia Vannetti n. 32 - 38122 Trento\n**T +39 0461 492605**\n**pec  ass.agriamb.entilocali@pec.provincia.tn.it**\n**@   ass.agriamb.entilocali@provincia.tn.it**\n\nPreg.mo Signore\nClaudio Soini\nPresidente del Consiglio della\nProvincia autonoma di Trento\n\ne, p. c. Gent.ma Signora\nLucia Coppola\nConsigliere provinciale\nGruppo consiliare\nGruppo Alleanza Verdi e Sinistra\n\nPreg.mo Signore\nMaurizio Fugatti\nPresidente della Provincia autonoma\ndi Trento\n\nL O R O  S E D I\n\n ...",
"assessorato": "assessorato all’agricoltura promozione dei prodotti trentini ambiente difesa idrogeologica e enti locali"}
```

## Test set XVII legislatura
Il file "test_ XVII_legislatura.jsonl" contiene solo interrogazioni dal 30 Novembre 2023 in poi (i.e. XVII legislatura). Il campo `assessorato` viene estratto dal campo `risposta` e può contenere solo un elemento preso dalla seguente lista che si riferisce ai ruoli della legislatura XVII:

Ruoli legislatura XVII:
```bash
presidente  
assessorato all’istruzione, cultura e sport, politiche per la famiglia, per i giovani e le pari opportunità  
assessorato all’artigianato, commercio, turismo, foreste, caccia e pesca  
assessorato all’urbanistica, energia e trasporti  
assessorato alle politiche per la casa, patrimonio, demanio e promozione della conoscenza dell’autonomia  
assessorato allo sviluppo economico, lavoro, università e ricerca  
assessorato alla salute, politiche sociali e cooperazione  
assessorato all’agricoltura, promozione dei prodotti trentini, ambiente, difesa idrogeologica e enti locali
```

## Dataset interrogazioni trento
Per i file "<test/validation/train>_interrogazioni_trento.jsonl" il campo `assessorato` è estratto dal campo `risposta`, il quale a sua volta è il testo contenuto nel file `risposta.pdf` del dataset originale. A differenza di "test_ XVII_legislatura.jsonl", in questo caso gli assessorati possono avere valori che provengono da tutte le legislature. Per semplicità li organizziamo nei seguenti mini-cluster:

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

Il task consiste nello scegliere il campo `assessorato` dato in input al modello (e.g. LLM) il campo `domanda`. 

Nel caso del test set "test_ XVII_legislatura.jsonl" le possibili scelte sono gli 8 ruoli della legislatura XVII (scritti sopra).

Nel caso dei set "valid/test_set_interrogazioni_trento.jsonl" ci sono 10 possibilità. Oltre all'assessorato corretto, ci sono 9 distrattori scelti randomicamente tra quelli elencati nei mini-cluster, pescando al più un solo elemento da ognuno dei mini-cluster.

Valutazione:
Lo scorer `scorer.py` permette di ottenere le metriche di valutazione e si aspetta due file in input:
- `reference_file`: il file con le gold labels, tipicamente il test set stesso. Il file deve essere in formato `.jsonl` e avere la stessa struttura presentata precedentemente.
- `answer_file`: il file con le scelte del modello. Lo scorer compara il campo `assessorato` di ogni elemento di questo file con il campo `assessorato` del `reference_file` per calcolare le metriche del task multiple choice (Accuracy, ...). 
- `task`: `multiple_choice`.

## TASK GENERAZIONE

Il task consiste nel generare una `risposta` dato in input al modello LLM il campo `domanda`.

Valutazione:
Lo scorer `scorer.py` permette di ottenere le metriche di valutazione e si aspetta due file in input:
- `reference_file`: il file con le gold labels, tipicamente il test set stesso. Il file deve essere in formato `.jsonl` e avere la stessa struttura presentata precedentemente.
- `answer_file`: il file con gli output generati dal modello. Lo scorer compara il campo `risposta` di ogni elemento di questo file con il campo `risposta` del `reference_file` per calcolare le metriche del task genrativo (BLEU, BLEU-Score, ...). 
- `task`: `multiple_choice`.

---
## SCORER

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
