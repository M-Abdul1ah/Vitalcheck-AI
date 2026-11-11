"""
DermaVC-Net in the app: our own skin-photo model (EfficientNetB0, fine-tuned in PyTorch, seed 7).

Input : the cleaned JPEG from vision_agent.prepare_image
Output: top-3 possible matches with calibrated probabilities, a confidence verdict,
        a melanoma warning flag, and an optional Grad-CAM heatmap.

Safe by design:
- It never diagnoses. Results are "possible matches".
- Probabilities are calibrated with temperature scaling (training/results/final_policy.json).
- Below min_confidence the app says "unclear, please see a doctor".
- If the melanoma probability reaches melanoma_threshold, a warning is shown even when another class is on top.
- torch / torchvision are imported only when needed, so the app and the tests work without them.
"""
import importlib.util
import io
import json
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.getenv("SKIN_MODEL_PATH", str(ROOT / "models" / "C_effnet_finetune_seed7.pt")))
CLASSES_PATH = ROOT / "training" / "classes.json"
POLICY_PATH = ROOT / "training" / "results" / "final_policy.json"
MODEL_REPO = os.getenv("SKIN_MODEL_REPO", "").strip()          # Hugging Face model repo, for example "your-name/dermavc-net"
MODEL_FILE = os.getenv("SKIN_MODEL_FILE", "C_effnet_finetune_seed7.pt")
MODEL_NAME = "DermaVC-Net v1.0 (EfficientNetB0, seed 7)"

IMG_SIZE = int(os.getenv("SKIN_IMG_SIZE", "224"))
RESIZE_MODE = os.getenv("SKIN_RESIZE_MODE", "squash")       # "squash" = Resize(224,224); "crop" = Resize(256) + CenterCrop(224)
MEAN, STD = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)    # ImageNet statistics

DEFAULT_CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
DEFAULT_POLICY = {"temperature": 1.7557951211929321, "melanoma_threshold": 0.25, "min_confidence": 0.5}

# code -> (English name, Urdu name)
LABELS = {
    "akiec": ("Actinic keratosis (sun-damaged skin patch)", "ایکٹینک کیراٹوسس (سورج سے متاثر جلد کا دھبہ)"),
    "bcc": ("Basal cell carcinoma (a type of skin cancer)", "بیسل سیل کارسنوما (جلد کے کینسر کی ایک قسم)"),
    "bkl": ("Benign keratosis-like lesion", "بے ضرر کیراٹوسس نما نشان"),
    "df": ("Dermatofibroma (harmless firm bump)", "ڈرموٹوفائبروما (بے ضرر سخت گانٹھ)"),
    "mel": ("Melanoma (a serious type of skin cancer)", "میلانوما (جلد کے کینسر کی ایک سنگین قسم)"),
    "nv": ("Common mole (melanocytic nevus)", "عام تل (میلانوسائٹک نیووس)"),
    "vasc": ("Vascular lesion (blood vessel mark)", "خون کی نالیوں کا نشان"),
}
MOLE_CODES = {"mel", "nv", "akiec", "bcc", "bkl"}   # classes where the ABCDE mole advice applies


class SkinModelError(Exception):
    """The photo model could not be loaded or run."""


def load_classes() -> list[str]:
    try:
        return json.loads(CLASSES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return list(DEFAULT_CLASSES)


def load_policy() -> dict:
    try:
        data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    return {k: float(data.get(k, v)) for k, v in DEFAULT_POLICY.items()}


def softmax(values: list[float], temperature: float = 1.0) -> list[float]:
    scaled = [v / temperature for v in values]
    top = max(scaled)
    exps = [math.exp(v - top) for v in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def interpret(logits: list[float], classes: list[str] | None = None, policy: dict | None = None) -> dict:
    """Turn raw model scores into the result shown to the user (pure Python, easy to test)."""
    classes = classes or load_classes()
    policy = policy or load_policy()
    if len(logits) != len(classes):
        raise SkinModelError(f"Model has {len(logits)} outputs but classes.json has {len(classes)} classes.")
    probs = softmax(list(logits), policy["temperature"])
    order = sorted(range(len(classes)), key=lambda i: probs[i], reverse=True)
    top = []
    for i in order[:3]:
        code = classes[i]
        en, ur = LABELS.get(code, (code, code))
        top.append({"code": code, "label_en": en, "label_ur": ur, "probability": round(probs[i], 4)})
    mel_p = probs[classes.index("mel")] if "mel" in classes else 0.0
    return {
        "top": top,
        "confident": top[0]["probability"] >= policy["min_confidence"],
        "min_confidence": policy["min_confidence"],
        "mel_probability": round(mel_p, 4),
        "melanoma_flag": mel_p >= policy["melanoma_threshold"],
        "mole_advice": top[0]["code"] in MOLE_CODES or mel_p >= policy["melanoma_threshold"],
        "model": MODEL_NAME,
    }


def _torch_installed() -> bool:
    return importlib.util.find_spec("torch") is not None and importlib.util.find_spec("torchvision") is not None


def is_available() -> bool:
    """True if torch + torchvision are installed and the model file is local or can be downloaded (loads nothing)."""
    return _torch_installed() and (MODEL_PATH.exists() or bool(MODEL_REPO))


def why_unavailable() -> str:
    if not MODEL_PATH.exists() and not MODEL_REPO:
        return f"Model file not found: {MODEL_PATH} (put it there, or set SKIN_MODEL_REPO to download it)"
    if not _torch_installed():
        return "torch / torchvision are not installed (pip install torch torchvision)"
    return ""


def resolve_model_path(path: Path | str | None = None) -> Path:
    """Local file first. If it is missing and SKIN_MODEL_REPO is set, download it once from Hugging Face Hub."""
    local = Path(path) if path else MODEL_PATH
    if local.exists():
        return local
    if not MODEL_REPO:
        raise SkinModelError(f"Model file not found: {local}. Put it there, or set SKIN_MODEL_REPO to download it.")
    try:
        from huggingface_hub import constants, hf_hub_download
    except Exception as e:
        raise SkinModelError(f"huggingface_hub is not available: {e}") from e
    token = os.getenv("HF_TOKEN") or None
    try:       # already in the local cache? (no network needed)
        return Path(hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, token=token, local_files_only=True))
    except Exception:
        pass
    previous = constants.HF_HUB_OFFLINE      # the app may have switched Hub access to offline mode for speed
    constants.HF_HUB_OFFLINE = False
    try:
        return Path(hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, token=token))
    except Exception as e:
        raise SkinModelError(f"Could not download {MODEL_FILE} from {MODEL_REPO}: {str(e)[:200]}") from e
    finally:
        constants.HF_HUB_OFFLINE = previous


class SkinModel:
    """Loads the .pt file once and predicts on photos."""

    def __init__(self, path: Path | str | None = None):
        self.path = resolve_model_path(path)
        self.classes = load_classes()
        self.policy = load_policy()
        self._load()

    # ---- loading -------------------------------------------------------------------------
    def _load(self):
        try:
            import torch
            from torchvision import models
        except Exception as e:      # ImportError, or a broken install (OSError)
            raise SkinModelError(f"torch / torchvision could not be loaded: {e}") from e
        self.torch = torch
        if not self.path.exists():
            raise SkinModelError(f"Model file not found: {self.path}")
        try:
            obj = torch.load(self.path, map_location="cpu", weights_only=True)
        except Exception:
            # A full pickled model needs weights_only=False. Only do this for our own file.
            try:
                obj = torch.load(self.path, map_location="cpu", weights_only=False)
            except Exception as e:
                raise SkinModelError(f"Could not read {self.path.name}: {e}") from e

        if isinstance(obj, torch.nn.Module):
            model = obj
        else:
            state = obj
            if isinstance(state, dict):
                for key in ("model_state_dict", "state_dict", "model", "net"):
                    if key in state and isinstance(state[key], (dict, torch.nn.Module)):
                        state = state[key]
                        break
            if isinstance(state, torch.nn.Module):
                model = state
            else:
                state = {k.removeprefix("module."): v for k, v in state.items()}
                model = models.efficientnet_b0(weights=None)
                heads = [k for k, v in state.items()
                         if k.startswith("classifier.") and k.endswith(".weight") and getattr(v, "ndim", 0) == 2]
                if heads:   # rebuild the classifier head the way it was saved (for example Dropout + Linear)
                    k = heads[-1]
                    idx, w = int(k.split(".")[1]), state[k]
                    layers = [torch.nn.Identity() for _ in range(idx)] + [torch.nn.Linear(w.shape[1], w.shape[0])]
                    model.classifier = torch.nn.Sequential(*layers)
                try:
                    model.load_state_dict(state, strict=True)
                except RuntimeError as e:
                    raise SkinModelError(
                        "The .pt file does not match torchvision EfficientNet-B0 with a 7-class head. "
                        f"Details: {str(e)[:400]}"
                    ) from e
        model.eval()
        self.model = model

    # ---- preprocessing ---------------------------------------------------------------------
    def _to_tensor(self, jpeg: bytes):
        from PIL import Image
        torch = self.torch
        img = Image.open(io.BytesIO(jpeg)).convert("RGB")
        if RESIZE_MODE == "crop":
            side = round(IMG_SIZE * 256 / 224)
            w, h = img.size
            scale = side / min(w, h)
            img = img.resize((max(side, round(w * scale)), max(side, round(h * scale))), Image.BILINEAR)
            w, h = img.size
            left, top = (w - IMG_SIZE) // 2, (h - IMG_SIZE) // 2
            img = img.crop((left, top, left + IMG_SIZE, top + IMG_SIZE))
        else:
            img = img.resize((IMG_SIZE, IMG_SIZE), Image.BILINEAR)
        data = torch.frombuffer(bytearray(img.tobytes()), dtype=torch.uint8)
        x = data.view(IMG_SIZE, IMG_SIZE, 3).permute(2, 0, 1).float() / 255.0
        mean = torch.tensor(MEAN).view(3, 1, 1)
        std = torch.tensor(STD).view(3, 1, 1)
        return ((x - mean) / std).unsqueeze(0), img

    # ---- prediction ------------------------------------------------------------------------
    def logits(self, jpeg: bytes) -> list[float]:
        x, _ = self._to_tensor(jpeg)
        with self.torch.no_grad():
            return self.model(x)[0].tolist()

    def predict(self, jpeg: bytes, heatmap: bool = True) -> dict:
        """Return interpret(...) plus an optional Grad-CAM overlay (PNG bytes) for the top class.
        The prediction never depends on the heatmap: if the heatmap fails, the result is still returned."""
        try:
            x, shown = self._to_tensor(jpeg)
            with self.torch.no_grad():
                result = interpret(self.model(x)[0].tolist(), self.classes, self.policy)
        except SkinModelError:
            raise
        except Exception as e:
            raise SkinModelError(f"Photo analysis failed: {e}") from e
        result["heatmap_png"] = None
        result["heatmap_error"] = ""
        if heatmap:
            try:
                result["heatmap_png"] = self._heatmap(x, shown)
            except Exception as e:      # the heatmap is a bonus; do not lose the prediction
                result["heatmap_error"] = str(e)[:200]
        return result

    def _heatmap(self, x, shown) -> bytes:
        torch = self.torch
        acts, grads = {}, {}
        layer = self.model.features[-1]

        def forward_hook(module, inputs, output):
            acts["a"] = output
            output.register_hook(lambda g: grads.__setitem__("g", g))   # tensor hook: safe with in-place activations

        handle = layer.register_forward_hook(forward_hook)
        try:
            with torch.enable_grad():
                out = self.model(x)
                top_idx = int(out[0].argmax())
                self.model.zero_grad(set_to_none=True)
                out[0, top_idx].backward()
        finally:
            handle.remove()
        if "g" not in grads:
            raise SkinModelError("Grad-CAM: no gradient was captured.")
        return _cam_overlay(torch, acts["a"].detach(), grads["g"].detach(), shown)


def _cam_overlay(torch, acts, grads, base_image) -> bytes:
    """Grad-CAM: highlight where the model looked. Returns PNG bytes (no numpy or matplotlib needed)."""
    from PIL import Image
    weights = grads.mean(dim=(2, 3), keepdim=True)
    cam = torch.relu((weights * acts).sum(dim=1))[0]
    cam = cam - cam.min()
    cam = cam / (cam.max() + 1e-8)
    size = base_image.size
    heat = Image.frombytes("L", tuple(cam.shape[::-1]), bytes((cam * 255).byte().flatten().tolist())).resize(size, Image.BILINEAR)
    colored = Image.new("RGB", size)
    px = []
    for v in heat.getdata():
        x = v / 255.0
        px.append((int(255 * min(1, max(0, 1.5 - abs(4 * x - 3)))),
                   int(255 * min(1, max(0, 1.5 - abs(4 * x - 2)))),
                   int(255 * min(1, max(0, 1.5 - abs(4 * x - 1))))))
    colored.putdata(px)
    out = Image.blend(base_image.convert("RGB"), colored, 0.4)
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()
