def test_search_parameter_forwarded(monkeypatch):
    import demo.reflex_app as ra

    called = {}

    def fake_list(session, search, sort_field, sort_desc, page, page_size, filters):
        called['search'] = search
        return {'items': [], 'total': 0, 'page': page, 'page_size': page_size}

    class FakeResource:
        @staticmethod
        def list(session, search=None, sort_field=None, sort_desc=False, page=1, page_size=20, filters=None):
            return fake_list(session, search, sort_field, sort_desc, page, page_size, filters)

    monkeypatch.setattr(ra, 'UserResource', FakeResource)

    # call the fetch helper
    res = ra.UsersState._fetch('john', 1, 20, '', False)
    assert called.get('search') == 'john'
    assert isinstance(res, dict)
