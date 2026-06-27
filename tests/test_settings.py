"""
Settings store tests — covers load/save/merge/defaults.
"""
import sys, os, json, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _fresh_store(tmp_dir):
    """Return a fresh SettingsStore backed by tmp_dir (no singleton state)."""
    import data.settings_store as mod
    mod._DATA_DIR = tmp_dir
    mod._SETTINGS_PATH = os.path.join(tmp_dir, "settings.json")
    mod.SettingsStore._instance = None
    from data.settings_store import SettingsStore
    return SettingsStore()


def test_defaults_load_when_no_file():
    tmp = tempfile.mkdtemp()
    try:
        store = _fresh_store(tmp)
        assert store.appearance["font_size"] == 14
        assert store.appearance["zoom"] == 1.0
        assert len(store.agents) == 5
        assert store.global_cfg["inter_agent_delay"] == 2.0
    finally:
        shutil.rmtree(tmp)


def test_save_creates_file():
    tmp = tempfile.mkdtemp()
    try:
        store = _fresh_store(tmp)
        store.save()
        assert os.path.exists(os.path.join(tmp, "settings.json"))
    finally:
        shutil.rmtree(tmp)


def test_save_and_reload_roundtrip():
    tmp = tempfile.mkdtemp()
    try:
        store = _fresh_store(tmp)
        store.appearance["font_size"] = 18
        store.appearance["zoom"] = 1.25
        store.agents[0]["name"] = "Chaos Agent"
        store.save()

        import data.settings_store as mod
        mod.SettingsStore._instance = None
        from data.settings_store import SettingsStore
        store2 = SettingsStore()
        assert store2.appearance["font_size"] == 18
        assert store2.appearance["zoom"] == 1.25
        assert store2.agents[0]["name"] == "Chaos Agent"
    finally:
        shutil.rmtree(tmp)


def test_deep_merge_preserves_unset_keys():
    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "settings.json")
        with open(path, "w") as f:
            json.dump({"appearance": {"font_size": 20}}, f)
        store = _fresh_store(tmp)
        assert store.appearance["font_size"] == 20
        assert store.appearance["zoom"] == 1.0        # default preserved
        assert store.appearance["font_family"] == "Roboto"  # default preserved
    finally:
        shutil.rmtree(tmp)


def test_five_agent_slots():
    import data.settings_store as mod
    mod.SettingsStore._instance = None
    from data.settings_store import SettingsStore
    store = SettingsStore()
    assert len(store.agents) == 5
    for i, agent in enumerate(store.agents):
        assert "id" in agent
        assert "name" in agent
        assert "color" in agent
        assert "source" in agent
        assert "temperature" in agent


def test_import_settings_panel():
    from ui.settings_panel import SettingsPanel
