"""Window-level AF detectors operating on 60-beat RR windows.

* ClassicalLR  – logistic regression on three classical irregularity features
                 (normalised RMSSD, Shannon entropy, turning-point ratio; cf. Dash et al. 2009).
* GBMDetector  – LightGBM on 16 RR-interval features (conventional ML baseline).
* RRNet        – 1-D CNN + bidirectional GRU on the raw RR sequence (deep baseline in the
                 spirit of ArNet/ArNet2; re-implemented, not the original code/weights).
All return P(AF | window) in [0, 1].
"""
from __future__ import annotations
import time
import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from ..preprocessing.features import FEATURE_NAMES


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class ClassicalLR:
    name = "Classical-LR"
    FEATS = [FEATURE_NAMES.index(f) for f in ("nrmssd", "shannon", "tpr")]

    def __init__(self, seed=0):
        self.seed = seed

    def fit(self, X, rr, y, Xv=None, rrv=None, yv=None):
        self.sc = StandardScaler().fit(X[:, self.FEATS])
        self.m = LogisticRegression(max_iter=2000, random_state=self.seed).fit(self.sc.transform(X[:, self.FEATS]), y)
        return self

    def predict(self, X, rr):
        return self.m.predict_proba(self.sc.transform(X[:, self.FEATS]))[:, 1]

    def n_params(self):
        return len(self.FEATS) + 1


class GBMDetector:
    name = "LightGBM"

    def __init__(self, seed=0, n_estimators=400):
        import lightgbm as lgb
        self.m = lgb.LGBMClassifier(n_estimators=n_estimators, learning_rate=0.05, num_leaves=31,
                                    subsample=0.8, subsample_freq=1, colsample_bytree=0.8,
                                    random_state=seed, n_jobs=4, verbose=-1)

    def fit(self, X, rr, y, Xv=None, rrv=None, yv=None):
        if Xv is not None:
            import lightgbm as lgb
            self.m.fit(X, y, eval_set=[(Xv, yv)], callbacks=[lgb.early_stopping(50, verbose=False)])
        else:
            self.m.fit(X, y)
        return self

    def predict(self, X, rr):
        return self.m.predict_proba(X)[:, 1]

    def n_params(self):
        # number of tree nodes as a size proxy
        d = self.m.booster_.dump_model()
        return int(sum(t["num_leaves"] * 2 - 1 for t in d["tree_info"]))


class _RRNetModule(nn.Module):
    def __init__(self, ch=32, hid=32):
        super().__init__()
        def blk(i, o):
            return nn.Sequential(nn.Conv1d(i, o, 5, padding=2), nn.BatchNorm1d(o), nn.ReLU())
        self.c1, self.c2, self.c3 = blk(2, ch), blk(ch, ch), blk(ch, ch)
        self.gru = nn.GRU(ch, hid, batch_first=True, bidirectional=True)
        self.head = nn.Sequential(nn.Linear(4 * hid, 32), nn.ReLU(), nn.Dropout(0.2), nn.Linear(32, 1))

    def forward(self, x):                       # x: (B, 2, W)
        h = self.c1(x); h = h + self.c2(h); h = h + self.c3(h)
        o, _ = self.gru(h.transpose(1, 2))      # (B, W, 2*hid)
        z = torch.cat([o.mean(1), o.max(1).values], 1)
        return self.head(z).squeeze(1)


def _rr_input(rr):
    """Per-window normalisation: log RR minus window mean, and successive differences (s)."""
    lr = np.log(rr.astype(np.float32))
    a = lr - lr.mean(1, keepdims=True)
    d = np.diff(rr, axis=1, prepend=rr[:, :1]).astype(np.float32)
    return np.stack([a * 5.0, d * 5.0], 1).astype(np.float32)


class RRNet:
    name = "RRNet"

    def __init__(self, seed=0, epochs=12, batch=512, lr=1e-3, patience=3, log=None):
        self.seed, self.epochs, self.batch, self.lr, self.patience, self.log = seed, epochs, batch, lr, patience, log
        self.history = []

    def fit(self, X, rr, y, Xv=None, rrv=None, yv=None):
        torch.manual_seed(self.seed); np.random.seed(self.seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
        dev = get_device(); self.dev = dev
        self.net = _RRNetModule().to(dev)
        opt = torch.optim.AdamW(self.net.parameters(), lr=self.lr, weight_decay=1e-4)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, self.epochs)
        Xt = torch.from_numpy(_rr_input(rr)); yt = torch.from_numpy(y.astype(np.float32))
        lossf = nn.BCEWithLogitsLoss()
        g = torch.Generator().manual_seed(self.seed)
        best, best_state, bad = np.inf, None, 0
        for ep in range(self.epochs):
            self.net.train(); t0 = time.time(); tot = 0.0
            perm = torch.randperm(len(Xt), generator=g)
            for i in range(0, len(Xt), self.batch):
                b = perm[i:i + self.batch]
                opt.zero_grad()
                loss = lossf(self.net(Xt[b].to(dev)), yt[b].to(dev))
                loss.backward(); opt.step(); tot += loss.item() * len(b)
            sched.step()
            vl = np.nan
            if rrv is not None:
                p = np.clip(self.predict(None, rrv), 1e-6, 1 - 1e-6)
                vl = float(-np.mean(yv * np.log(p) + (1 - yv) * np.log(1 - p)))
            self.history.append(dict(epoch=ep + 1, train_loss=tot / len(Xt), val_loss=vl, sec=time.time() - t0))
            if self.log:
                self.log(f"    RRNet seed={self.seed} epoch {ep+1} train={tot/len(Xt):.4f} val={vl:.4f} ({time.time()-t0:.0f}s)")
            if rrv is not None:
                if vl < best - 1e-4:
                    best, bad = vl, 0
                    best_state = {k: v.detach().clone() for k, v in self.net.state_dict().items()}
                else:
                    bad += 1
                    if bad >= self.patience:
                        break
        if best_state is not None:
            self.net.load_state_dict(best_state)
        return self

    @torch.no_grad()
    def predict(self, X, rr):
        self.net.eval()
        x = torch.from_numpy(_rr_input(rr))
        out = [torch.sigmoid(self.net(x[i:i + 8192].to(self.dev))).cpu().numpy() for i in range(0, len(x), 8192)]
        return np.concatenate(out)

    def n_params(self):
        return int(sum(p.numel() for p in self.net.parameters()))


DETECTORS = {"Classical-LR": ClassicalLR, "LightGBM": GBMDetector, "RRNet": RRNet}
