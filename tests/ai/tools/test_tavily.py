import pytest
from unittest.mock import Mock

from app.ai.tools.tavily import TavilyTool

def test_tavily_search():
    mock_client = Mock()

    mock_client.search.return_value = {
        "results": [
            {
                "title": "Python 3.14 Released",
                "url": "https://www.python.org",
                "content": "Python 3.14 introduces new features.",
            }
        ]
    }

    tool = TavilyTool(client=mock_client)

    result = tool.execute(query="Python 3.14 news")

    assert "Python 3.14 Released" in result
    assert "https://www.python.org" in result

    mock_client.search.assert_called_once_with(
        query="Python 3.14 news"
    )

@pytest.mark.parametrize(
    "query",
    ["", "   ", None, 123],
)
def test_tavily_rejects_invalid_query(query):
    mock_client = Mock()
    tool = TavilyTool(client=mock_client)

    with pytest.raises(ValueError, match="Search query is required"):
        tool.execute(query=query)

    mock_client.search.assert_not_called()    