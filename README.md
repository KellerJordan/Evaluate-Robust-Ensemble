# Evaluate-Robust-Ensemble

This code evaluates the Robust Ensemble technique proposed by Fort et al. (2024) using
a transfer attack from a standard ensemble.
This attack reduces the robust accuracy of the Robust Ensemble from ~75% to ~14%.


`python evaluate_defense.py`

```
Training 10 models for use in standard and robust ensemblees...
100%|█████████████████████████| 10/10 [00:40<00:00,  4.08s/it]

Generating first batch of adversarial examples using PGD against the robust ensemble...
100%|███████████████████████| 100/100 [00:04<00:00, 20.39it/s]
Accuracy on first batch of adversarial examples:
Robust ensemble: tensor(0.7500)
Standard ensemble: tensor(0.7560)

Generating second batch of adversarial examples using PGD against the standard ensemble...
100%|███████████████████████| 100/100 [00:04<00:00, 21.36it/s]
Accuracy on second batch of adversarial examples:
Robust ensemble: tensor(0.1460)
Standard ensemble: tensor(0.1480)
```

