CITY_TO_HOTEL_CODES = {"jaipur": "1247101", "delhi": "1276403", "bangalore": "1234567"}


def resolve_hotel_codes(destination: str):
    """
    Resolves destination → hotel codes.
    Prototype implementation.
    """
    if not destination:
        return None

    return CITY_TO_HOTEL_CODES.get(destination.lower())
