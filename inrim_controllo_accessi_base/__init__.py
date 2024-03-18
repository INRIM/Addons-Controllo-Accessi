def post_init_hook(env):
    try:
        it = env.ref('base.lang_it')
        lang_id = env['base.language.install'].create({
            'lang_ids': it.ids,
            'overwrite': True
        })
        lang_id.lang_install()
        for user in env['res.users'].search([]):
            user.write({
                'lang': it.code
            })
    except:
        pass