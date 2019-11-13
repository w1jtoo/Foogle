from App.Config import Config


def test_config_is_not_empty():
    config = Config()

    assert (
        config.get_date_base_name()
        and config.get_general_path()
        and config.get_types()
    )
