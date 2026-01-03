"""
Unit Tests for CSVRepository.

Test categories:
- Initialization tests
- Load CSV tests
- Separator handling tests
- Additional kwargs handling tests
"""

# pylint: disable=redefined-outer-name

from unittest.mock import patch, MagicMock

import pytest
import pandas as pd

from src.shared.infrastructure.repositories.CSVRepository import CSVRepository


# Create a concrete implementation for testing
class ConcreteCSVRepository(CSVRepository):
    """Concrete implementation of CSVRepository for testing purposes."""

    def __init__(self, file_path: str):
        """Initialize the concrete repository."""
        super().__init__(file_path)


# Test fixtures
@pytest.fixture
def sample_file_path():
    """Create a sample file path for testing."""
    return "test_data.csv"


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        'column1': [1, 2, 3],
        'column2': ['a', 'b', 'c']
    })


class TestCSVRepositoryInitialization:
    """Test initialization of CSVRepository."""

    def test_initializes_with_file_path(self, sample_file_path):
        """Test that repository initializes and stores file path."""
        repo = ConcreteCSVRepository(sample_file_path)

        # pylint: disable=protected-access
        assert repo._file_path == sample_file_path

    def test_initializes_with_different_file_paths(self):
        """Test that repository can be initialized with different file paths."""
        path1 = "data1.csv"
        path2 = "data2.csv"
        path3 = "/absolute/path/to/data.csv"

        repo1 = ConcreteCSVRepository(path1)
        repo2 = ConcreteCSVRepository(path2)
        repo3 = ConcreteCSVRepository(path3)

        # pylint: disable=protected-access
        assert repo1._file_path == path1
        assert repo2._file_path == path2
        assert repo3._file_path == path3

    def test_is_abstract_base_class(self):
        """Test that CSVRepository is an abstract base class."""
        from abc import ABC

        assert issubclass(CSVRepository, ABC)

    def test_can_instantiate_directly(self, sample_dataframe):
        """Test that CSVRepository can be instantiated directly (no abstract methods)."""
        # CSVRepository has no abstract methods, so it can be instantiated
        # This is intentional - it's a base class with concrete implementation
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.return_value = sample_dataframe
            repo = CSVRepository("test.csv")
            
            # pylint: disable=protected-access
            assert repo._file_path == "test.csv"
            result = repo._load_csv(sep=',')
            assert isinstance(result, pd.DataFrame)


class TestLoadCSV:
    """Test _load_csv method."""

    @patch('pandas.read_csv')
    def test_load_csv_calls_pandas_read_csv(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv calls pandas.read_csv with correct file path."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',')

        mock_read_csv.assert_called_once_with(sample_file_path, sep=',')
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_with_comma_separator(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv works with comma separator."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',')

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == ','
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_with_semicolon_separator(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv works with semicolon separator."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=';')

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == ';'
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_with_tab_separator(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv works with tab separator."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep='\t')

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == '\t'
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_passes_additional_kwargs(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv passes additional kwargs to pandas.read_csv."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',', encoding='utf-8', skiprows=1)

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == ','
        assert call_kwargs['encoding'] == 'utf-8'
        assert call_kwargs['skiprows'] == 1
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_with_multiple_additional_kwargs(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv handles multiple additional kwargs."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(
            sep=',',
            encoding='latin-1',
            header=0,
            index_col=0,
            na_values=['N/A', 'NULL']
        )

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == ','
        assert call_kwargs['encoding'] == 'latin-1'
        assert call_kwargs['header'] == 0
        assert call_kwargs['index_col'] == 0
        assert call_kwargs['na_values'] == ['N/A', 'NULL']
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_returns_dataframe(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv returns a pandas DataFrame."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',')

        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_with_empty_dataframe(
        self, mock_read_csv, sample_file_path
    ):
        """Test that _load_csv handles empty DataFrame."""
        empty_df = pd.DataFrame()
        mock_read_csv.return_value = empty_df
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',')

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        pd.testing.assert_frame_equal(result, empty_df)

    @patch('pandas.read_csv')
    def test_load_csv_called_multiple_times(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv can be called multiple times."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result1 = repo._load_csv(sep=',')
        result2 = repo._load_csv(sep=';')

        assert mock_read_csv.call_count == 2
        pd.testing.assert_frame_equal(result1, sample_dataframe)
        pd.testing.assert_frame_equal(result2, sample_dataframe)

    @patch('pandas.read_csv')
    def test_load_csv_preserves_file_path(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv uses the stored file path."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        repo._load_csv(sep=',')

        # Verify the file path passed to read_csv matches the stored path
        call_args = mock_read_csv.call_args[0]
        assert call_args[0] == sample_file_path

    @patch('pandas.read_csv')
    def test_load_csv_with_no_additional_kwargs(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that _load_csv works with only separator specified."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        result = repo._load_csv(sep=',')

        mock_read_csv.assert_called_once()
        call_kwargs = mock_read_csv.call_args[1]
        assert call_kwargs['sep'] == ','
        # Should only have sep in kwargs
        assert len(call_kwargs) == 1
        pd.testing.assert_frame_equal(result, sample_dataframe)


class TestCSVRepositoryIntegration:
    """Integration tests for CSVRepository."""

    @patch('pandas.read_csv')
    def test_complete_workflow(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test complete workflow of initializing and loading CSV."""
        mock_read_csv.return_value = sample_dataframe

        # Initialize repository
        repo = ConcreteCSVRepository(sample_file_path)

        # Load CSV
        result = repo._load_csv(sep=',', encoding='utf-8')

        # Verify results
        assert isinstance(result, pd.DataFrame)
        pd.testing.assert_frame_equal(result, sample_dataframe)
        mock_read_csv.assert_called_once_with(sample_file_path, sep=',', encoding='utf-8')

    @patch('pandas.read_csv')
    def test_multiple_repositories_with_different_paths(
        self, mock_read_csv, sample_dataframe
    ):
        """Test that multiple repositories can work with different file paths."""
        path1 = "data1.csv"
        path2 = "data2.csv"

        mock_read_csv.return_value = sample_dataframe

        repo1 = ConcreteCSVRepository(path1)
        repo2 = ConcreteCSVRepository(path2)

        result1 = repo1._load_csv(sep=',')
        result2 = repo2._load_csv(sep=',')

        assert mock_read_csv.call_count == 2
        # Verify each repository used its own file path
        assert mock_read_csv.call_args_list[0][0][0] == path1
        assert mock_read_csv.call_args_list[1][0][0] == path2
        pd.testing.assert_frame_equal(result1, sample_dataframe)
        pd.testing.assert_frame_equal(result2, sample_dataframe)

    @patch('pandas.read_csv')
    def test_repository_handles_different_separators_in_sequence(
        self, mock_read_csv, sample_file_path, sample_dataframe
    ):
        """Test that repository can handle different separators in sequence."""
        mock_read_csv.return_value = sample_dataframe
        repo = ConcreteCSVRepository(sample_file_path)

        # Load with different separators
        result1 = repo._load_csv(sep=',')
        result2 = repo._load_csv(sep=';')
        result3 = repo._load_csv(sep='\t')

        assert mock_read_csv.call_count == 3
        # Verify each call used the correct separator
        assert mock_read_csv.call_args_list[0][1]['sep'] == ','
        assert mock_read_csv.call_args_list[1][1]['sep'] == ';'
        assert mock_read_csv.call_args_list[2][1]['sep'] == '\t'