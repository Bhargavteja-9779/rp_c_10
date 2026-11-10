"""Two-state hidden Markov model over window sequences, vectorised across sequences.

States: 0 = non-AF, 1 = AF. Emissions are FIXED class-conditional likelihoods of the
detector's score (estimated on held-out calibration patients). Patient-adaptive variant:
per-patient MAP-EM re-estimation of the initial distribution and transition matrix with
Dirichlet (Beta) priors centred on the source (calibration) dynamics.
"""
from __future__ import annotations
import numpy as np

EPS = 1e-300


def pad_sequences(values: np.ndarray, seq_index: np.ndarray, n_seq: int):
    """values: (N, ...) ordered within each sequence; seq_index: (N,) in [0, n_seq).
    Returns padded (S, T, ...) array, lengths (S,), and (S,T) -> flat index map (-1 for pad)."""
    order = np.argsort(seq_index, kind="stable")
    si = seq_index[order]
    lengths = np.bincount(si, minlength=n_seq)
    T = int(lengths.max())
    starts = np.concatenate([[0], np.cumsum(lengths)[:-1]])
    pos = np.arange(len(si)) - starts[si]
    idx = -np.ones((n_seq, T), dtype=np.int64)
    idx[si, pos] = order
    return idx, lengths


def forward_backward(E: np.ndarray, L: np.ndarray, A: np.ndarray, pi: np.ndarray):
    """E: (S,T,2) emission likelihoods (pad entries ignored); L: (S,) lengths;
    A: (S,2,2) transition matrices; pi: (S,2). Returns gamma (S,T,2), xi_sum (S,2,2), loglik (S,)."""
    S, T, _ = E.shape
    alpha = np.zeros((S, T, 2)); c = np.ones((S, T))
    a = pi * E[:, 0]
    c[:, 0] = a.sum(1) + EPS; alpha[:, 0] = a / c[:, 0, None]
    for t in range(1, T):
        act = t < L
        a = np.einsum("si,sij->sj", alpha[:, t - 1], A) * E[:, t]
        ct = a.sum(1) + EPS
        alpha[:, t] = np.where(act[:, None], a / ct[:, None], alpha[:, t - 1])
        c[:, t] = np.where(act, ct, 1.0)
    beta = np.ones((S, T, 2))
    xi = np.zeros((S, 2, 2))
    for t in range(T - 2, -1, -1):
        act = (t + 1) < L
        b = np.einsum("sij,sj->si", A, E[:, t + 1] * beta[:, t + 1]) / c[:, t + 1, None]
        beta[:, t] = np.where(act[:, None], b, 1.0)
        x = alpha[:, t, :, None] * A * (E[:, t + 1] * beta[:, t + 1])[:, None, :] / c[:, t + 1, None, None]
        xi += np.where(act[:, None, None], x, 0.0)
    gamma = alpha * beta
    gamma /= gamma.sum(-1, keepdims=True) + EPS
    loglik = np.log(c).sum(1)
    return gamma, xi, loglik, alpha


def ffbs(alpha: np.ndarray, L: np.ndarray, A: np.ndarray, n_samples: int, rng: np.random.Generator):
    """Forward-filtering backward-sampling. Returns sampled states (K,S,T) as int8."""
    S, T, _ = alpha.shape
    K = n_samples
    Z = np.zeros((K, S, T), dtype=np.int8)
    last = np.clip(L - 1, 0, T - 1)
    p1 = alpha[np.arange(S), last, 1]
    z = (rng.random((K, S)) < p1[None]).astype(np.int8)
    Z[:, np.arange(S), last] = z
    for t in range(T - 2, -1, -1):
        act = t < (L - 1)  # positions before last valid
        nxt = Z[:, :, t + 1]
        # P(z_t = 1 | z_{t+1}, y_{1:t}) ∝ alpha_t(1) A[1, z_{t+1}]
        A_to = np.take_along_axis(A[None, :, :, :].repeat(K, 0), nxt[:, :, None, None].repeat(2, 2).astype(np.int64), axis=3)[..., 0]  # (K,S,2)
        w = alpha[None, :, t, :] * A_to
        pr = w[..., 1] / (w.sum(-1) + EPS)
        draw = (rng.random((K, S)) < pr).astype(np.int8)
        Z[:, :, t] = np.where(act[None], draw, Z[:, :, t])
    return Z


class BurdenHMM:
    def __init__(self, kappa: float | None = 10.0, max_iter: int = 50, tol: float = 1e-6):
        """kappa=None -> fixed source dynamics (no adaptation); kappa=0 -> MLE adaptation."""
        self.kappa, self.max_iter, self.tol = kappa, max_iter, tol

    def fit_source(self, y: np.ndarray, seq_index: np.ndarray):
        """Source transition matrix and initial distribution from labelled calibration sequences."""
        same = np.r_[False, seq_index[1:] == seq_index[:-1]]
        prev, cur = y[:-1][same[1:]], y[1:][same[1:]]
        C = np.ones((2, 2))
        np.add.at(C, (prev, cur), 1)
        self.A_src = C / C.sum(1, keepdims=True)
        first = y[~same]
        self.pi_src = np.bincount(first, minlength=2).astype(float) + 1.0
        self.pi_src /= self.pi_src.sum()
        return self

    def infer(self, E_flat: np.ndarray, seq_index: np.ndarray, patient_of_seq: np.ndarray, n_patients: int,
              n_samples: int = 0, rng=None):
        """E_flat: (N,2) emission likelihoods ordered within sequences. Returns gamma_flat (N,),
        per-patient A (P,2,2), and optional posterior state samples mapped to flat (K,N)."""
        n_seq = int(seq_index.max()) + 1
        idx, L = pad_sequences(E_flat, seq_index, n_seq)
        E = np.where(idx[..., None] >= 0, E_flat[np.clip(idx, 0, None)], 1.0)
        Ap = np.repeat(self.A_src[None], n_patients, 0)
        pip = np.repeat(self.pi_src[None], n_patients, 0)
        prev_ll = -np.inf
        for it in range(self.max_iter if self.kappa is not None else 1):
            A = Ap[patient_of_seq]; pi = pip[patient_of_seq]
            gamma, xi, ll, alpha = forward_backward(E, L, A, pi)
            if self.kappa is None:
                break
            Xi = np.zeros((n_patients, 2, 2)); np.add.at(Xi, patient_of_seq, xi)
            G0 = np.zeros((n_patients, 2)); np.add.at(G0, patient_of_seq, gamma[:, 0])
            Ap = Xi + self.kappa * self.A_src[None]
            Ap = (Ap + 1e-12) / (Ap + 1e-12).sum(-1, keepdims=True)
            pip = G0 + self.kappa * self.pi_src[None]
            pip = (pip + 1e-12) / (pip + 1e-12).sum(-1, keepdims=True)
            tot = ll.sum()
            if abs(tot - prev_ll) < self.tol * max(1.0, abs(tot)):
                break
            prev_ll = tot
        A = Ap[patient_of_seq]; pi = pip[patient_of_seq]
        gamma, xi, ll, alpha = forward_backward(E, L, A, pi)
        g = np.zeros(len(E_flat)); m = idx >= 0
        g[idx[m]] = gamma[..., 1][m]
        samples = None
        if n_samples:
            Z = ffbs(alpha, L, A, n_samples, rng or np.random.default_rng(0))
            samples = np.zeros((n_samples, len(E_flat)), dtype=np.int8)
            samples[:, idx[m]] = Z[:, m]
        self.A_patient_ = Ap
        return g, samples
