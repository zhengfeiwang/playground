import pytest
from unittest.mock import MagicMock, patch
from swe.tools.mimir import Mimir, WorkItem


@pytest.fixture
def mock_env_vars(monkeypatch: pytest.MonkeyPatch):
    """Fixture to set up environment variables."""
    monkeypatch.setenv("AZURE_DEVOPS_PAT", "fake_pat")
    monkeypatch.setenv("AZURE_DEVOPS_ORGANIZATION", "fake_org")
    monkeypatch.setenv("AZURE_DEVOPS_PROJECT", "fake_project")


@pytest.fixture
def mock_client() -> MagicMock:
    """Fixture to mock the Azure DevOps client."""
    return MagicMock()


@pytest.fixture
def mimir_instance(mock_env_vars, mock_client: MagicMock) -> Mimir:
    """Fixture to create a Mimir instance with a mocked client."""
    with patch("swe.tools.mimir.Mimir._get_client", return_value=mock_client):
        return Mimir()


class TestWorkItem:
    def test_work_item_from_rest_object(self) -> None:
        """Test the WorkItem dataclass transformation."""
        rest_work_item = MagicMock(
            id=12345,
            fields={
                "System.Title": "Sample Work Item",
                "System.AssignedTo": {"displayName": "Jane Smith"},
                "System.Description": "Sample description.",
            },
        )

        work_item = WorkItem.from_rest_object(rest_work_item)

        assert work_item.id == 12345
        assert work_item.title == "Sample Work Item"
        assert work_item.assigned_to == "Jane Smith"
        assert work_item.description == "Sample description."



class TestMimir:
    def test_get_work_item_success(self, mimir_instance: Mimir, mock_client: MagicMock) -> None:
        """Test successful retrieval of a work item."""
        mock_client.get_work_item.return_value = MagicMock(
            id=5394169,
            fields={
                "System.Title": "Test Work Item",
                "System.AssignedTo": {"displayName": "John Doe"},
                "System.Description": "This is a test work item.",
            },
        )

        work_item = mimir_instance.get_work_item(5394169)

        assert work_item.id == 5394169
        assert work_item.title == "Test Work Item"
        assert work_item.assigned_to == "John Doe"
        assert work_item.description == "This is a test work item."

    def test_get_work_item_missing_fields(self, mimir_instance: Mimir, mock_client: MagicMock) -> None:
        """Test retrieval of a work item with missing fields."""
        mock_client.get_work_item.return_value = MagicMock(
            id=5394169,
            fields={
                "System.Title": "Test Work Item",
            },
        )

        work_item = mimir_instance.get_work_item(5394169)

        assert work_item.id == 5394169
        assert work_item.title == "Test Work Item"
        assert work_item.assigned_to == "Unassigned"
        assert work_item.description == "No description available"
