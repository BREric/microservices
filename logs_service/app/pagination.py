from flask import request

def paginate(query, default_limit=10, default_page=1):
    try:
        limit = int(request.args.get('limit', default_limit))
        page = int(request.args.get('page', default_page))
    except ValueError:
        limit = default_limit
        page = default_page

    # Asegurarse de que `page` y `limit` son válidos
    if page < 1:
        page = 1
    if limit < 1:
        limit = default_limit

    return query.skip((page - 1) * limit).limit(limit)