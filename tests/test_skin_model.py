import json
import sys
import types

import pytest

from src import skin_model as sm

CLASSES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
POLICY = {"temperature": 1.0, "melanoma_threshold": 0.25, "min_confidence": 0.5}


def logits_for(top_code, strength=5.0, mel=0.0):
    v = [0.0] * 7
    v[CLASSES.index(top_code)] = strength
    v[CLASSES.index("mel")] = max(v[CLASSES.index("mel")], mel)
    return v


def test_softmax_sums_to_one_and_temperature_softens():
    p1 = sm.softmax([4.0, 1.0, 0.0], 1.0)
    p2 = sm.softmax([4.0, 1.0, 0.0], 2.0)
    assert abs(sum(p1) - 1) < 1e-9 and abs(sum(p2) - 1) < 1e-9
    assert p2[0] < p1[0]


def test_top3_sorted_and_named():
    r = sm.interpret(logits_for("nv"), CLASSES, POLICY)
    probs = [t["probability"] for t in r["top"]]
    assert len(r["top"]) == 3 and probs == sorted(probs, reverse=True)
    assert r["top"][0]["code"] == "nv" and "mole" in r["top"][0]["label_en"].lower()


def test_confident_when_top_probability_high():
    assert sm.interpret(logits_for("nv", 6.0), CLASSES, POLICY)["confident"] is True


def test_unclear_when_flat():
    r = sm.interpret([0.1, 0.0, 0.2, 0.0, 0.1, 0.3, 0.0], CLASSES, POLICY)
    assert r["confident"] is False


def test_melanoma_flag_even_if_other_class_on_top():
    # nv on top, but melanoma probability is still above 0.25
    r = sm.interpret([0, 0, 0, 0, 2.2, 2.8, 0], CLASSES, POLICY)
    assert r["top"][0]["code"] == "nv"
    assert r["mel_probability"] >= 0.25 and r["melanoma_flag"] is True


def test_no_melanoma_flag_for_clear_vascular():
    r = sm.interpret(logits_for("vasc", 8.0), CLASSES, POLICY)
    assert r["melanoma_flag"] is False and r["mole_advice"] is False


def test_mole_advice_for_nevus():
    assert sm.interpret(logits_for("nv", 6.0), CLASSES, POLICY)["mole_advice"] is True


def test_wrong_output_count_raises():
    with pytest.raises(sm.SkinModelError):
        sm.interpret([0.0, 1.0], CLASSES, POLICY)


def test_labels_cover_every_class_in_classes_json():
    for code in sm.load_classes():
        assert code in sm.LABELS and all(sm.LABELS[code])


def test_policy_matches_final_policy_json():
    data = json.loads(sm.POLICY_PATH.read_text(encoding="utf-8"))
    pol = sm.load_policy()
    assert pol["temperature"] == pytest.approx(data["temperature"])
    assert pol["melanoma_threshold"] == pytest.approx(data["melanoma_threshold"])
    assert pol["min_confidence"] == pytest.approx(data["min_confidence"])


def test_not_available_without_model_file(monkeypatch, tmp_path):
    monkeypatch.setattr(sm, "MODEL_PATH", tmp_path / "missing.pt")
    assert sm.is_available() is False
    assert "not found" in sm.why_unavailable()


def test_load_missing_file_raises_clear_error(tmp_path):
    try:
        import torch, torchvision  # noqa: F401
    except Exception:
        pytest.skip("torch / torchvision not usable here")
    with pytest.raises(sm.SkinModelError):
        sm.SkinModel(tmp_path / "missing.pt")


def _fake_hub(tmp_path, cached=False):
    calls = []

    def fake_download(repo_id, filename, token=None, local_files_only=False):
        calls.append(local_files_only)
        if local_files_only and not cached:
            raise FileNotFoundError("not cached")
        f = tmp_path / "downloaded.pt"
        f.write_bytes(b"x")
        return str(f)

    mod = types.ModuleType("huggingface_hub")
    mod.hf_hub_download = fake_download
    mod.constants = types.SimpleNamespace(HF_HUB_OFFLINE=True)
    return mod, calls


def test_downloads_from_hub_when_local_file_missing(monkeypatch, tmp_path):
    mod, calls = _fake_hub(tmp_path)
    monkeypatch.setitem(sys.modules, "huggingface_hub", mod)
    monkeypatch.setattr(sm, "MODEL_PATH", tmp_path / "missing.pt")
    monkeypatch.setattr(sm, "MODEL_REPO", "user/dermavc-net")
    path = sm.resolve_model_path()
    assert path.name == "downloaded.pt" and calls == [True, False]
    assert mod.constants.HF_HUB_OFFLINE is True          # offline setting restored after the download


def test_uses_hub_cache_without_network(monkeypatch, tmp_path):
    mod, calls = _fake_hub(tmp_path, cached=True)
    monkeypatch.setitem(sys.modules, "huggingface_hub", mod)
    monkeypatch.setattr(sm, "MODEL_PATH", tmp_path / "missing.pt")
    monkeypatch.setattr(sm, "MODEL_REPO", "user/dermavc-net")
    sm.resolve_model_path()
    assert calls == [True]


def test_local_file_wins_over_hub(monkeypatch, tmp_path):
    local = tmp_path / "local.pt"
    local.write_bytes(b"x")
    monkeypatch.setattr(sm, "MODEL_REPO", "user/dermavc-net")
    assert sm.resolve_model_path(local) == local


def test_no_local_file_and_no_repo_gives_clear_error(monkeypatch, tmp_path):
    monkeypatch.setattr(sm, "MODEL_PATH", tmp_path / "missing.pt")
    monkeypatch.setattr(sm, "MODEL_REPO", "")
    with pytest.raises(sm.SkinModelError):
        sm.resolve_model_path()


def test_available_when_repo_is_set_even_without_local_file(monkeypatch, tmp_path):
    monkeypatch.setattr(sm, "MODEL_PATH", tmp_path / "missing.pt")
    monkeypatch.setattr(sm, "_torch_installed", lambda: True)
    monkeypatch.setattr(sm, "MODEL_REPO", "")
    assert sm.is_available() is False
    monkeypatch.setattr(sm, "MODEL_REPO", "user/dermavc-net")
    assert sm.is_available() is True
