# Formulasi Matematika & Evaluasi Statistik Sistem UlasRasa

Dokumen ini mendokumentasikan formulasi matematis untuk kalkulasi metrik diagnostik dapur (*Kitchen Health Score*) dan evaluasi performa model klasifikasi aspek sentimen (*Aspect-Based Sentiment Analysis* / ABSA) pada proyek UlasRasa.

---

## 1. Formulasi Kitchen Health Score (KHS)

*Kitchen Health Score* (KHS) mengukur kesehatan operasional dapur secara menyeluruh berbasis agregasi sentimen ulasan pelanggan pada 5 aspek kualitas:
$$\mathcal{A} = \{\text{Rasa}, \text{Porsi}, \text{Harga}, \text{Kemasan}, \text{Pelayanan}\}$$

### A. Tingkat Kepuasan per Aspek ($S_k$)
Untuk setiap aspek $k \in \mathcal{A}$, kepuasan pelanggan dihitung dengan menimbang sentimen positif penuh, sentimen netral separuh, dan sentimen negatif:

$$
\begin{aligned}
S_k &= \frac{N_k^+ + 0.5 \cdot N_k^0}{N_k^+ + N_k^0 + N_k^-} \times 100\%
\end{aligned}
$$

di mana:
- $\displaystyle N_k^+$ = jumlah ulasan positif pada aspek $k$.
- $\displaystyle N_k^0$ = jumlah ulasan netral pada aspek $k$.
- $\displaystyle N_k^-$ = jumlah ulasan negatif pada aspek $k$.

### B. Skor Komposit Terbobot (Overall KHS)
Skor komposit keseluruhan dihitung menggunakan kombinasi linier terbobot:

$$
\begin{aligned}
\text{KHS} &= \sum_{k=1}^5 w_k \cdot S_k
\end{aligned}
$$

dengan vektor bobot prioritas industri F&B:
$$
\begin{aligned}
\mathbf{w} &= [w_{\text{rasa}}=0.35, \, w_{\text{porsi}}=0.20, \, w_{\text{kemasan}}=0.15, \, w_{\text{harga}}=0.15, \, w_{\text{pelayanan}}=0.15] \\
\sum_{k=1}^5 w_k &= 1.0
\end{aligned}
$$

### C. Klasifikasi Status Operasional Dapur
- **Optimal / Prima**: $\displaystyle \text{KHS} \ge 80\%$
- **Waspada / Perhatian**: $\displaystyle 65\% \le \text{KHS} < 80\%$
- **Kritis / Audit Darurat**: $\displaystyle \text{KHS} < 65\%$

---

## 2. Formulasi Metrik Evaluasi Model NLP (ABSA)

Karena distribusi kelas ulasan restoran mengalami ketimpangan ekstrem (*severe class imbalance* di mana kelas positif mendominasi >70%), akurasi mentah (*accuracy*) mengalami *accuracy paradox*. Model dievaluasi menggunakan *Macro-Averaged F1-Score*.

### A. Precision & Recall per Kelas $c \in \{\text{Negatif}, \text{Netral}, \text{Positif}\}$

$$
\begin{aligned}
\text{Precision}_c &= \frac{TP_c}{TP_c + FP_c} \\
\text{Recall}_c &= \frac{TP_c}{TP_c + FN_c}
\end{aligned}
$$

### B. F1-Score per Kelas $c$

$$
\begin{aligned}
F1_c &= 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}
\end{aligned}
$$

### C. Macro-F1 per Aspek

$$
\begin{aligned}
\text{Macro-F1}_k &= \frac{1}{3} \sum_{c \in \{\text{Neg}, \text{Net}, \text{Pos}\}} F1_c
\end{aligned}
$$

### D. Overall Benchmark Macro-F1

$$
\begin{aligned}
\text{Overall Macro-F1} &= \frac{1}{5} \sum_{k=1}^5 \text{Macro-F1}_k
\end{aligned}
$$

---

## 3. Loss Function Multi-Task IndoBERT

Optimasi serentak 5 classification head linier di atas representasi token `[CLS]` encoder IndoBERT ($h_{\text{CLS}} \in \mathbb{R}^{768}$) menggunakan *Multi-Task Cross-Entropy Loss*:

$$
\begin{aligned}
\mathcal{L}_{\text{total}} &= \sum_{k=1}^5 \mathcal{L}_{\text{CE}}^{(k)} \\
&= - \sum_{k=1}^5 \sum_{c=1}^3 y_{k, c} \log(\hat{y}_{k, c})
\end{aligned}
$$
