# Evaluate-CrossMax-Ensemble

This code evaluates the robust accuracy of the `CrossMax Ensemble` defense technique ([Fort et al., 2024](https://arxiv.org/abs/2408.05446)).

To avoid gradient masking effects, we evaluate the CrossMax ensemble using an attack transferred from the corresponding standard ensemble.
We find that this reduces the robust accuracy of the CrossMax Ensemble from ~77% to ~2%.


`python evaluate_defense.py`

```
Training 10 models for use in standard and CrossMax ensembles...
100%|█████████████████████████| 10/10 [00:47<00:00,  4.71s/it]
Generating first batch of adversarial examples using PGD against the CrossMax ensemble...
100%|███████████████████████| 100/100 [00:04<00:00, 20.28it/s]
Accuracy on first batch of adversarial examples:
CrossMax ensemble: tensor(0.7780)
Standard ensemble: tensor(0.7840)
Generating second batch of adversarial examples using PGD against the standard ensemble...
100%|███████████████████████| 100/100 [00:04<00:00, 21.48it/s]
Accuracy on second batch of adversarial examples:
CrossMax ensemble: tensor(0.0220)
Standard ensemble: tensor(0.0240)
```

![](imgs/fort2024a.png)
![](imgs/fort2024b.png)

Note: The reason our initial accuracy for the CrossMax ensemble (~77%) is higher than Fort et al. (2024)'s reported accuracy (~17%) is probably because we only use PGD
whereas they use a stronger APGD-T attack, which perhaps is able to somewhat compensate for the gradient masking effect.
After we get rid of the masking effect by transferring an attack from a standard ensemble, the CrossMax ensemble's accuracy falls to 2%, the same
as the standard ensemble.

