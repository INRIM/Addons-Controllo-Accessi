def check_access_permission(user):
    return (user.has_group('controllo_accessi.ca_portineria') or
            (user.has_group('controllo_accessi.ca_ru') or
             user.has_group('controllo_accessi_portale.inrim_access_portal')))