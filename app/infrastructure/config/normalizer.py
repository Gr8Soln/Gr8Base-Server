from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def normalize_database_url(database_url: str) -> str:
    """Normalize DB URLs so asyncpg-compatible options are used.

    Some managed Postgres providers expose libpq-style query params like
    `sslmode` and `channel_binding`. SQLAlchemy asyncpg expects asyncpg-style
    arguments, so we rewrite/remove incompatible options.
    """
    if not database_url:
        return database_url

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)

    parts = urlsplit(database_url)

    # Only apply normalization for asyncpg URLs.
    if "asyncpg" not in (parts.scheme or ""):
        return database_url

    sslmode_to_ssl = {
        "disable": "disable",
        "allow": "allow",
        "prefer": "prefer",
        "require": "require",
        "verify-ca": "verify-ca",
        "verify-full": "verify-full",
    }

    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    normalized_pairs = []
    has_ssl = False

    for key, value in query_pairs:
        if key == "ssl":
            has_ssl = True
            normalized_pairs.append((key, value))
            continue

        if key == "sslmode":
            if not has_ssl:
                normalized_pairs.append(("ssl", sslmode_to_ssl.get(value, "require")))
                has_ssl = True
            continue

        # libpq-specific option that asyncpg does not accept.
        if key == "channel_binding":
            continue

        normalized_pairs.append((key, value))

    normalized_query = urlencode(normalized_pairs, doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, normalized_query, parts.fragment))
