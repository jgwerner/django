def test_notebook_server(container, http_client):
    """Notebook server should display work directory."""
    container.run()
    resp = http_client.get('http://localhost:8080')
    resp.raise_for_status()
    assert 'Home' in resp.text