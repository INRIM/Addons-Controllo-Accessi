import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Rename ca_persona.display_name column to complete_name.

    The stored computed field ``display_name`` has been renamed to
    ``complete_name`` (res.partner-like pattern) so that it can be listed
    in ``_rec_names_search`` without recursing into
    ``_search_display_name``. Renaming the column preserves the data and
    avoids a full recompute.
    """
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ca_persona' AND column_name = 'display_name'
    """)
    has_old = bool(cr.fetchone())
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'ca_persona' AND column_name = 'complete_name'
    """)
    has_new = bool(cr.fetchone())

    if has_old and not has_new:
        _logger.info(
            "Renaming column ca_persona.display_name to complete_name")
        cr.execute(
            "ALTER TABLE ca_persona RENAME COLUMN display_name TO complete_name")
    else:
        _logger.info(
            "Skipping rename ca_persona.display_name -> complete_name "
            "(display_name exists: %s, complete_name exists: %s)",
            has_old, has_new,
        )
