import app


def test_integrated_lab_builds():
    ui = app.build_app()
    assert ui is not None


def test_all_eight_engines_registered():
    assert len(app.ENGINES) == 9  # overview + eight engines
    assert sum(slug is not None for _, slug in app.ENGINES) == 8
