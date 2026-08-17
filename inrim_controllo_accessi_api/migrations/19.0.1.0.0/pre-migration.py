import json
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Recover API keys from server_env_defaults into the key column.

    Up to 17.0 the project depended on ``auth_api_key_server_env``: the
    ``key`` field was env-computed and its real value lived in the sparse
    field ``x_key_env_default``, serialized inside the
    ``server_env_defaults`` column. The ``key`` column itself was never
    written.

    On 19.0 ``auth_api_key_server_env`` no longer exists, so ``key`` is a
    plain stored Char again and reads the (empty) ``key`` column: every
    API key would be lost and token authentication would break. Copy the
    values back before the module uninstall drops ``server_env_defaults``.
    """
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'auth_api_key'
          AND column_name = 'server_env_defaults'
    """)
    if not cr.fetchone():
        _logger.info(
            "Column auth_api_key.server_env_defaults not found, "
            "nothing to recover")
        return

    cr.execute("""
        SELECT id, server_env_defaults FROM auth_api_key
        WHERE (key IS NULL OR key = '')
          AND server_env_defaults IS NOT NULL
    """)
    recovered = 0
    for record_id, defaults in cr.fetchall():
        if isinstance(defaults, str):
            try:
                defaults = json.loads(defaults)
            except ValueError:
                _logger.warning(
                    "auth_api_key id %s: invalid JSON in "
                    "server_env_defaults, skipping", record_id)
                continue
        key = (defaults or {}).get('x_key_env_default')
        if not key:
            continue
        cr.execute(
            "UPDATE auth_api_key SET key = %s WHERE id = %s",
            (key, record_id),
        )
        recovered += 1
    _logger.info(
        "Recovered %s API key(s) from server_env_defaults", recovered)
