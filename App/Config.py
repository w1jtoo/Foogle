class Config:
    # TODO Connect serialization using Yaml
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_date_base_name(self) -> str:
        return "foogletempbase.db"

    