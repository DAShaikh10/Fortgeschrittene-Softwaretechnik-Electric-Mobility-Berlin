"""
Unit Tests for logging_config module.

Test categories:
- setup_logging function tests
- get_logger function tests
"""

# pylint: disable=redefined-outer-name

import logging
import sys

from unittest.mock import Mock, patch

from src.shared.infrastructure import logging_config


class TestSetupLogging:
    """Test setup_logging function."""

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_with_default_level(self, mock_basic_config):
        """Test that setup_logging uses INFO level by default."""
        logging_config.setup_logging()

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.INFO

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_with_custom_level(self, mock_basic_config):
        """Test that setup_logging accepts custom logging level."""
        logging_config.setup_logging(level=logging.DEBUG)

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.DEBUG

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_with_warning_level(self, mock_basic_config):
        """Test that setup_logging works with WARNING level."""
        logging_config.setup_logging(level=logging.WARNING)

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.WARNING

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_configures_format(self, mock_basic_config):
        """Test that setup_logging configures the correct format."""
        logging_config.setup_logging()

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_configures_date_format(self, mock_basic_config):
        """Test that setup_logging configures the correct date format."""
        logging_config.setup_logging()

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["datefmt"] == "%Y-%m-%d %H:%M:%S"

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_uses_stdout_handler(self, mock_basic_config):
        """Test that setup_logging uses StreamHandler with stdout."""
        logging_config.setup_logging()

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        handlers = call_kwargs["handlers"]
        assert len(handlers) == 1
        assert isinstance(handlers[0], logging.StreamHandler)
        assert handlers[0].stream is sys.stdout

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_can_be_called_multiple_times(self, mock_basic_config):
        """Test that setup_logging can be called multiple times."""
        logging_config.setup_logging()
        logging_config.setup_logging(level=logging.DEBUG)

        assert mock_basic_config.call_count == 2

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_with_error_level(self, mock_basic_config):
        """Test that setup_logging works with ERROR level."""
        logging_config.setup_logging(level=logging.ERROR)

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.ERROR

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_with_critical_level(self, mock_basic_config):
        """Test that setup_logging works with CRITICAL level."""
        logging_config.setup_logging(level=logging.CRITICAL)

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.CRITICAL


class TestGetLogger:
    """Test get_logger function."""

    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_returns_logger_instance(self, mock_get_logger):
        """Test that get_logger returns a logger instance."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        result = logging_config.get_logger("test_module")

        assert result is mock_logger
        mock_get_logger.assert_called_once_with("test_module")

    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_with_different_names(self, mock_get_logger):
        """Test that get_logger works with different module names."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        logging_config.get_logger("module1")
        logging_config.get_logger("module2")
        logging_config.get_logger("module3")

        assert mock_get_logger.call_count == 3
        mock_get_logger.assert_any_call("module1")
        mock_get_logger.assert_any_call("module2")
        mock_get_logger.assert_any_call("module3")

    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_with_dunder_name(self, mock_get_logger):
        """Test that get_logger works with __name__ pattern."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        result = logging_config.get_logger("src.shared.infrastructure.logging_config")

        assert result is mock_logger
        mock_get_logger.assert_called_once_with("src.shared.infrastructure.logging_config")

    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_with_empty_string(self, mock_get_logger):
        """Test that get_logger handles empty string."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        result = logging_config.get_logger("")

        assert result is mock_logger
        mock_get_logger.assert_called_once_with("")

    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_returns_same_logger_for_same_name(self, mock_get_logger):
        """Test that get_logger returns the same logger for the same name."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        logger1 = logging_config.get_logger("test")
        logger2 = logging_config.get_logger("test")

        assert logger1 is logger2
        assert mock_get_logger.call_count == 2


class TestLoggingConfigIntegration:
    """Integration tests for logging_config module."""

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_setup_and_get_logger_workflow(self, mock_get_logger, mock_basic_config):
        """Test complete workflow of setup and getting logger."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        # Setup logging
        logging_config.setup_logging(level=logging.DEBUG)

        # Get logger
        logger = logging_config.get_logger("test_module")

        # Verify setup was called
        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]
        assert call_kwargs["level"] == logging.DEBUG

        # Verify logger was retrieved
        mock_get_logger.assert_called_once_with("test_module")
        assert logger is mock_logger

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_multiple_loggers_after_setup(self, mock_get_logger, mock_basic_config):
        """Test getting multiple loggers after setup."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        # Setup once
        logging_config.setup_logging()

        # Get multiple loggers
        logger1 = logging_config.get_logger("module1")
        logger2 = logging_config.get_logger("module2")
        logger3 = logging_config.get_logger("module3")

        # Verify setup called once
        mock_basic_config.assert_called_once()

        # Verify all loggers retrieved
        assert mock_get_logger.call_count == 3
        assert logger1 is mock_logger
        assert logger2 is mock_logger
        assert logger3 is mock_logger

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    @patch("src.shared.infrastructure.logging_config.logging.getLogger")
    def test_get_logger_without_setup(self, mock_get_logger, mock_basic_config):
        """Test that get_logger can be called without setup_logging."""
        mock_logger = Mock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        # Get logger without calling setup_logging
        logger = logging_config.get_logger("test")

        # Verify logger was retrieved
        mock_get_logger.assert_called_once_with("test")
        assert logger is mock_logger

        # Verify setup was not called
        mock_basic_config.assert_not_called()

    @patch("src.shared.infrastructure.logging_config.logging.basicConfig")
    def test_setup_logging_configurations_are_correct(self, mock_basic_config):
        """Test that all configuration parameters are correct."""
        logging_config.setup_logging(level=logging.INFO)

        mock_basic_config.assert_called_once()
        call_kwargs = mock_basic_config.call_args[1]

        # Verify all expected parameters
        assert "level" in call_kwargs
        assert "format" in call_kwargs
        assert "datefmt" in call_kwargs
        assert "handlers" in call_kwargs

        # Verify their values
        assert call_kwargs["level"] == logging.INFO
        assert call_kwargs["format"] == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert call_kwargs["datefmt"] == "%Y-%m-%d %H:%M:%S"
        assert len(call_kwargs["handlers"]) == 1
        assert isinstance(call_kwargs["handlers"][0], logging.StreamHandler)
