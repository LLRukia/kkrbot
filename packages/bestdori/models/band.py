from .helpers import UnderscoreToCamelModel, ServerListType

class PartialBand(UnderscoreToCamelModel):
    band_name: ServerListType[str]
