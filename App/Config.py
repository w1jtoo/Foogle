class Config:
    # TODO Connect serialization using Yaml
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_date_base_name(self) -> str:
        return "foogledatebase.db"

    def get_types(self) -> list:
        return ["text/plain"]
    
    def get_types_extention(self) -> list:
        return []