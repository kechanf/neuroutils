import importlib


def test_subpackages_importable() -> None:
    modules = [
        "neuroutils.io",
        "neuroutils.morphometrics",
        "neuroutils.transforms",
        "neuroutils.validation",
        "neuroutils.visualization",
    ]
    for module in modules:
        assert importlib.import_module(module)
