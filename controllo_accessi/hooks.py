import logging

logger = logging.getLogger(__name__)


def _init_italy(env):
    logger.info("Import Geoname IT ")
    it = env.ref('base.it')
    wizard = env['city.zip.geonames.import'].create({
        'country_ids': it.ids
    })
    wizard.run_import()


def post_init_hook(env):
    logger.info("Update users lang ")
    try:
        it = env.ref('base.lang_it')
        lang_id = env['base.language.install'].create({
            'lang_ids': it.ids,
            'overwrite': True
        })
        lang_id.lang_install()
    except:
        pass
