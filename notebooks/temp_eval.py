import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import MiniBatchDictionaryLearning, sparse_encode
from sklearn.metrics import mean_absolute_error, mean_squared_error

path = Path(r"C:\Users\camelia\Documents\letsgo\industrial-vibration-missing-data-reconstruction\data\processed\synthetic_A_sensor.csv")
df = pd.read_csv(path, sep=",", decimal=",")
if "Timestamp" in df.columns:
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], utc=True)
    df = df.sort_values("Timestamp").reset_index(drop=True)

target = "A_ACR_Mot.TV"
predictors = [col for col in df.columns if col not in {"Timestamp", target} and pd.api.types.is_numeric_dtype(df[col])]
model_df = df[["Timestamp", target] + predictors].copy().ffill().bfill()

class DictionaryReconstructor:
    def __init__(self, window_size=10, n_components=16, alpha=0.1, max_iter=500, seed=42):
        self.window_size = window_size
        self.n_components = n_components
        self.alpha = alpha
        self.max_iter = max_iter
        self.seed = seed
        self.model = None
        self.target = ""
        self.predictors = []

    def _matrix(self, data, include_target):
        cols = self.predictors + ([self.target] if include_target else [])
        matrix = []
        for end in range(self.window_size - 1, len(data)):
            block = data.iloc[end - self.window_size + 1:end + 1][cols].to_numpy(dtype=float).T
            if include_target and not np.isfinite(block).all():
                continue
            matrix.append(block.ravel())
        return np.asarray(matrix, dtype=float), []

    def fit(self, train, target, predictors):
        self.target, self.predictors = target, predictors
        samples, _ = self._matrix(train, True)
        self.model = MiniBatchDictionaryLearning(
            n_components=self.n_components,
            alpha=self.alpha,
            max_iter=self.max_iter,
            batch_size=min(256, len(samples)),
            random_state=self.seed,
        )
        self.model.fit(samples)
        return self

    def predict(self, data):
        prior = np.full(len(data), np.nan)
        variance = np.full(len(data), np.nan)
        availability = np.full(len(data), np.nan)
        dictionary = self.model.components_
        channels = len(self.predictors) + 1
        for end in range(self.window_size - 1, len(data)):
            block = data.iloc[end - self.window_size + 1:end + 1][self.predictors + [self.target]].to_numpy(dtype=float).T
            observed = np.isfinite(block)
            pred_available = observed[:-1].all(axis=1)
            availability[end] = pred_available.sum()
            if pred_available.sum() < 2:
                continue
            observed[-1, -1] = False
            flat = block.ravel()
            mask = observed.ravel()
            if not mask.any():
                continue
            coefficients = sparse_encode(flat[mask][None, :], dictionary[:, mask], algorithm="lasso_lars", alpha=self.alpha)
            reconstructed = coefficients @ dictionary
            target_index = (channels - 1) * self.window_size + self.window_size - 1
            prior[end] = reconstructed[0, target_index]
            residual = flat[mask] - reconstructed[0, mask]
            variance[end] = max(float(np.mean(residual ** 2)), 1e-6)
        return prior, variance, availability

train_size = int(len(model_df) * 0.8)
train_df = model_df.iloc[:train_size].copy()
valid_df = model_df.iloc[train_size:].copy()

rng = np.random.default_rng(42)
valid_masked = valid_df.copy()
mask_positions = rng.choice(len(valid_masked), size=max(20, len(valid_masked) // 10), replace=False)
valid_masked.loc[valid_masked.index[mask_positions], target] = np.nan

reconstructor = DictionaryReconstructor(window_size=10, n_components=16, alpha=0.1, max_iter=500, seed=42)
reconstructor.fit(train_df, target, predictors)
prior, variance, availability = reconstructor.predict(valid_masked)

masked_idx = np.where(valid_masked[target].isna())[0]
true_values = valid_df[target].to_numpy()[masked_idx]
pred_values = prior[masked_idx]
valid_predictions = np.isfinite(pred_values) & np.isfinite(true_values)
true_values = true_values[valid_predictions]
pred_values = pred_values[valid_predictions]

print("n_eval", len(true_values))
print("MAE", round(float(mean_absolute_error(true_values, pred_values)), 6))
print("RMSE", round(float(np.sqrt(mean_squared_error(true_values, pred_values))), 6))

# Abrupt-change proxy: large absolute first differences
s = model_df[target].astype(float).to_numpy()
d = np.abs(np.diff(s))
z = (d - d.mean()) / (d.std() + 1e-12)
spikes = np.where(z > 4)[0]
print("spikes_z_gt_4", len(spikes))
print("first_spikes", spikes[:10].tolist())

# Correlation with other predictors
corrs = []
for col in predictors:
    try:
        c = float(df[target].astype(float).corr(df[col].astype(float)))
    except Exception:
        continue
    corrs.append((col, c))

corrs = sorted(corrs, key=lambda x: abs(x[1]), reverse=True)
print("top_corrs", corrs[:10])
