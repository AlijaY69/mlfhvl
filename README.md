# Machine Learning for Human Vision & Language (INFOMLHVL) — Utrecht University

Coursework from the MSc AI course *Machine Learning for Human Vision and Language* (Utrecht University, 2025). The models here are implemented from scratch — the recurrent cell, the GloVe objective, convolution and pooling in raw NumPy — and then used as **behavioural probes**: the question is not only whether a model performs the task, but whether its predictions track known patterns of human processing difficulty.

Notebooks are three-person group work with Konstantinos Mereos and Yifan Zhou.

---

## `assignment_2b_group_38_(1).ipynb` — Recurrent models and human sentence processing

**The task is prediction, not labelling.** The model predicts the part-of-speech tag of the *upcoming* word from left context only. This is deliberately harder than standard POS tagging (98–99% accuracy, bidirectional context, tag assigned to the word you can already see) and the difficulty is the point: human readers also predict upcoming material rather than waiting for it, so a model built this way is a candidate account of reading, not a tagger.

**Implementations.**
- `MySRN` — an Elman network written out by hand: the three linear transformations, a `step` function computing hidden and output states from the previous hidden state, and a `forward` that iterates it over a sequence.
- `FastSRN` — the same computation through `torch.nn.RNN`, verified against the hand-written version on a toy input.
- `LSTMPredTag` — unidirectional LSTM, deliberately not bidirectional, since right context would defeat the prediction framing.

Input is 300-dimensional spaCy static vectors with tokenisation forced to match the corpus segmentation; sequences are batched via a custom `Dataset` and a `pad_sequence` collate function; the loss ignores padding.

**Baselines and accuracy.** Most-frequent-tag 0.145, unigram-on-previous-word 0.373. The SRN reaches ≈0.443 validation accuracy and the LSTM ≈0.478 before overfitting; the best configuration (2-layer LSTM, hidden 1024, stopped at 4 epochs) reaches 0.491. The notebook argues explicitly why the ceiling here is far below a normal tagger's, and the loss curves show validation loss rising while training loss falls.

**Surprisal as the behavioural measure.** Surprisal is read off the model's log-probability for the *true* tag, then aggregated per tag and compared against per-tag accuracy — the two rank tags consistently, which is the sanity check that the measure means what it should. Base-form verbs are the most predictable (0.70 mean surprisal, 84% accuracy); possessive pronouns are the least (3.83, 4%), because they occupy exactly the slot determiners occupy and left context cannot separate them.

**Garden-path sentences.** Five pairs, each a garden-path sentence and a minimally different disambiguated control, with surprisal compared at the specific word where human readers are known to slow down. The models reproduce the effect at four of the five target words, strongly at two of them, and reverse it at one. The LSTM's effects are consistently larger than the SRN's — stronger expectations, therefore a bigger violation when they break.

**Centre embedding.** Depths 0 through 3, each paired with a version where the matrix verb is deleted, testing whether the model is surprised by the *absence* of the verb it should still be expecting. The LSTM holds the expectation through depth 2 and collapses at depth 3; the SRN fails from depth 1. Humans degrade sharply past one level of embedding, so where the two architectures diverge is exactly where at most one of them can still be a candidate account of the human data.

---

## `solutions_merged_(1).ipynb` — GloVe from scratch

**Corpus.** A word–word co-occurrence matrix over the Harry Potter books, ~4,485-word vocabulary after frequency cutoff.

**Implementation, following the original paper.** Co-occurrence counts to conditional probabilities; the probe ratio *P(k|i)/P(k|j)* that motivates the whole model; the weighting function; the least-squares objective written in matrix form rather than looped pointwise; and the model itself as an `nn.Module` wrapping four embedding tables (word vectors, context vectors, and both bias terms), trained with Adam for 300 epochs.

**Validation.** Cosine similarity and nearest-neighbour retrieval, plus the word-analogy task implemented under two different formulations — the standard vector-offset criterion and an alternative that scores candidates by how closely the *difference* vectors align. The two are compared directly rather than assumed equivalent.

The interpretation sections separate **similarity** from **relatedness** and are explicit that most retrieved neighbours are the latter, holding only inside this corpus: the model recovers narrative co-occurrence structure, not general semantics. A worked case: probing the paper's own `solid` / `gas` / `water` / `fashion` example against `ice` and `steam` reproduces the paper's ratios for two probe words and *reverses* one, traceable to a single sentence in the source text plus the smoothing constant. Domain and corpus size, not the algorithm, produce the difference.

### Recovering an undocumented pipeline (task c9)

Worth pulling out separately. We were given the finished co-occurrence matrix and a few hints, and asked to reconstruct the procedure that produced it — the counting scheme, the frequency cutoff, and the window size were all withheld.

The approach: build the pipeline, then use element-wise agreement against the reference matrix as the objective, sweeping candidate parameters. The cutoff was recovered by matching vocabulary membership exactly; the window size by maximising matrix agreement. The decisive find was diagnostic rather than parametric — spurious numeric tokens in the vocabulary turned out to be chapter markers embedded in the source text, which had to be preserved as segment boundaries (so that the last word of one chapter does not co-occur with the first of the next) while being excluded from the vocabulary itself. Several plausible counting schemes were tried and rejected against the reference. The final version is fully vectorised and runs in under four seconds.

We recovered the vocabulary exactly and got close on the counts without reproducing the reference matrix bit-for-bit; the notebook says so rather than claiming a match.

---

## From-scratch vision components

Standalone scripts from the same course, MNIST throughout:

- **`exercise_two.py`** — convolution, ReLU, max-pooling, standardisation, a fully-connected layer, and softmax, implemented in NumPy with **no loops over pixels**. The convolution builds the flat index array for every sliding window at once (row offsets, column offsets, and channel offsets composed into a single gather) and reduces the whole operation to one matrix multiply against reshaped kernels. Pooling uses the same indexing trick.
  > Known issue: `maxpool` refers to an undefined name in its body and will not run as written.
- **`cnn.py`** — Keras convolutional model (two conv layers, max-pool, dropout at two rates), with accuracy and loss curves and a held-out test evaluation.
- **`main.py`** — a dense baseline for the same task, as the comparison point for the convolutional model.

---

## Running

The notebooks were written in Google Colab and run there without setup; both download their data in the first cells. Locally:

```bash
pip install torch numpy pandas matplotlib spacy nltk tqdm scikit-learn tensorflow
python -m spacy download en_core_web_lg
jupyter notebook
```

The recurrent-models notebook is slow on CPU (roughly 15 minutes per training run) and fast on GPU.

## Contributions

Ali Kodratallah Ostowar, Konstantinos Mereos, Yifan Zhou. Each member worked through all exercises independently before comparing, then split the merge of three separate notebooks into one; for the GloVe assignment I merged the Dense Vectors sections.

## AI use

In line with the UU AI Index: AI assistance was used for debugging, clarifying Python and preprocessing concepts, and cross-checking results. Model implementations, analysis, and written interpretation are the authors' own.

## Author

Ali Kodratallah Ostowar — MSc Artificial Intelligence & MSc Neuroscience and Cognition, Utrecht University
[a.k.ostowar@students.uu.nl](mailto:a.k.ostowar@students.uu.nl)
