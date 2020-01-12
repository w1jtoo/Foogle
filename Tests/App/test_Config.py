from App.Config import Config


def test_config_is_not_empty():
    config = Config()

    assert config.date_base_name and config.general_path and config.types
