from tqdm import tqdm
import torch
from torch import nn
import torchvision.transforms as T
import torch.nn.functional as F
import airbench

CIFAR_MEAN = torch.tensor((0.4914, 0.4822, 0.4465))
CIFAR_STD = torch.tensor((0.2470, 0.2435, 0.2616))
normalize = T.Normalize(CIFAR_MEAN, CIFAR_STD)
denormalize = T.Normalize(-CIFAR_MEAN / CIFAR_STD, 1 / CIFAR_STD)

def pgd(inputs, targets, model, r=0.5, step_size=0.1, steps=100, eps=1e-5):
    delta = torch.zeros_like(inputs, requires_grad=True)
    norm_r = 4 * r # radius converted into normalized pixel space
    norm_step_size = 4 * step_size
    
    for step in tqdm(range(steps)):
    
        delta.grad = None
        output = model(inputs + delta)
        loss = F.cross_entropy(output, targets, reduction='none').sum()
        loss.backward()

        # normalize gradient
        grad_norm = delta.grad.reshape(len(delta), -1).norm(dim=1)
        unit_grad = delta.grad / (grad_norm[:, None, None, None] + eps)
    
        # take step in unit-gradient direction with scheduled step size
        delta.data -= norm_step_size * unit_grad

        # project to r-sphere
        delta_norm = delta.data.reshape(len(delta), -1).norm(dim=1)
        mask = (delta_norm > norm_r)
        delta.data[mask] = norm_r * delta.data[mask] / (delta_norm[mask, None, None, None] + eps)
        
        # project to pixel-space
        delta.data = normalize(denormalize(inputs + delta.data).clip(0, 1)) - inputs

    return delta.data

class Ensemble(nn.Module):
    """
    Standard ensemble mechanism
    """
    def __init__(self, nets):
        super().__init__()
        self.nets = nn.ModuleList(nets)
    def forward(self, x):
        xx = torch.stack([net(x) for net in self.nets])
        return xx.mean(0)

class RobustEnsemble(nn.Module):
    """
    Alternate ensembling mechanism proposed by Fort et al. (2024)
    https://arxiv.org/abs/2408.05446
    
    ...we propose a robust aggregation mechanism based on Vickrey auction that we call CrossMax...
    ...Our robust median ensemble, CrossMax, gives very non-trivial adversarial accuracy
    gains to ensembles of individually brittle models. For 𝐿∞ = 6/255, its CIFAR-10 robust accuracy is
    17-fold larger than standard ensembling... (Fort et al. 2024)
    """
    def __init__(self, nets):
        super().__init__()
        self.nets = nn.ModuleList(nets)
    def forward(self, x):
        xx = torch.stack([net(x) for net in self.nets])
        xx = xx - xx.amax(dim=2, keepdim=True)
        xx = xx - xx.amax(dim=0, keepdim=True)
        return xx.median(dim=0).values


if __name__ == '__main__':

    test_loader = airbench.CifarLoader('cifar10', train=False)

    print('Training 10 models for use in standard and robust ensemblees...')
    models = [airbench.train94(verbose=False) for _ in tqdm(range(10))]

    standard_ensemble = Ensemble(models).eval()
    robust_ensemble = RobustEnsemble(models).eval()

    print('Generating first batch of adversarial examples using PGD against the robust ensemble...')
    inputs, labels = next(iter(test_loader))
    new_labels = labels[torch.randperm(len(labels))]
    adv_delta = pgd(inputs, new_labels, robust_ensemble, r=0.5, steps=100, step_size=0.2)
    adv_inputs = inputs + adv_delta
    print('Accuracy on first batch of adversarial examples:')
    with torch.no_grad():
        print('Robust ensemble:', (robust_ensemble(adv_inputs).argmax(1) == labels).float().mean())
        print('Standard ensemble:', (standard_ensemble(adv_inputs).argmax(1) == labels).float().mean())

    print('Generating second batch of adversarial examples using PGD against the standard ensemble...')
    inputs, labels = next(iter(test_loader))
    new_labels = labels[torch.randperm(len(labels))]
    adv_delta = pgd(inputs, new_labels, standard_ensemble, r=0.5, steps=100, step_size=0.2)
    adv_inputs = inputs + adv_delta
    print('Accuracy on second batch of adversarial examples:')
    with torch.no_grad():
        print('Robust ensemble:', (robust_ensemble(adv_inputs).argmax(1) == labels).float().mean())
        print('Standard ensemble:', (standard_ensemble(adv_inputs).argmax(1) == labels).float().mean())

