import logging

logger = logging.getLogger(__name__)


def pre_init_hook(env):
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
