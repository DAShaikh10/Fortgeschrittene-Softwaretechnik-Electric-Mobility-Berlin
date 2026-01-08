"""
Unit Tests for InvalidGeoLocationError Exception.

Test categories:
- Exception creation and initialization
- Exception inheritance
- Exception raising and catching
- Message handling
- String representation
"""

import pytest

from src.shared.domain.exceptions import InvalidGeoLocationError


class TestInvalidGeoLocationErrorCreation:
    """Test exception creation and initialization."""

    def test_create_exception_with_default_message(self):
        """Test creating exception with default message."""
        exception = InvalidGeoLocationError()

        assert exception.message == "Invalid geo location data"
        assert str(exception) == "Invalid geo location data"

    def test_create_exception_with_custom_message(self):
        """Test creating exception with custom message."""
        custom_message = "Boundary data cannot be None"
        exception = InvalidGeoLocationError(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message

    def test_create_exception_with_empty_message(self):
        """Test creating exception with empty message."""
        exception = InvalidGeoLocationError("")

        assert exception.message == ""
        assert str(exception) == ""

    def test_create_exception_with_multiline_message(self):
        """Test creating exception with multiline message."""
        multiline_message = "Geo Location validation failed:\n- Boundary is None\n- Invalid format"
        exception = InvalidGeoLocationError(multiline_message)

        assert exception.message == multiline_message
        assert str(exception) == multiline_message


class TestInvalidGeoLocationErrorInheritance:
    """Test exception inheritance and type checking."""

    def test_exception_inherits_from_value_error(self):
        """Test that InvalidGeoLocationError inherits from ValueError."""
        exception = InvalidGeoLocationError()

        assert isinstance(exception, ValueError)

    def test_exception_inherits_from_exception(self):
        """Test that InvalidGeoLocationError inherits from Exception."""
        exception = InvalidGeoLocationError()

        assert isinstance(exception, Exception)

    def test_exception_is_base_exception(self):
        """Test that InvalidGeoLocationError inherits from BaseException."""
        exception = InvalidGeoLocationError()

        assert isinstance(exception, BaseException)

    def test_exception_type_check(self):
        """Test exception type check."""
        exception = InvalidGeoLocationError("Test message")

        assert type(exception).__name__ == "InvalidGeoLocationError"


class TestInvalidGeoLocationErrorRaising:
    """Test exception raising and catching."""

    def test_raise_exception_with_default_message(self):
        """Test raising exception with default message."""
        with pytest.raises(InvalidGeoLocationError):
            raise InvalidGeoLocationError()

    def test_raise_exception_with_custom_message(self):
        """Test raising exception with custom message."""
        custom_message = "Boundary cannot be empty"

        with pytest.raises(InvalidGeoLocationError):
            raise InvalidGeoLocationError(custom_message)

    def test_catch_as_value_error(self):
        """Test catching InvalidGeoLocationError as ValueError."""
        with pytest.raises(ValueError):
            raise InvalidGeoLocationError("Test error")

    def test_catch_as_exception(self):
        """Test catching InvalidGeoLocationError as Exception."""
        with pytest.raises(Exception):
            raise InvalidGeoLocationError("Test error")

    def test_exception_message_in_traceback(self):
        """Test that exception message appears in error info."""
        custom_message = "Invalid WKT format provided"

        with pytest.raises(InvalidGeoLocationError, match=custom_message):
            raise InvalidGeoLocationError(custom_message)

    def test_exception_with_regex_match(self):
        """Test exception message with regex pattern matching."""
        with pytest.raises(InvalidGeoLocationError, match=r"Geo Location.*cannot be None"):
            raise InvalidGeoLocationError("Geo Location boundary cannot be None or empty")


class TestInvalidGeoLocationErrorMessageAttribute:
    """Test message attribute access and manipulation."""

    def test_message_attribute_accessible(self):
        """Test that message attribute is accessible."""
        exception = InvalidGeoLocationError("Test message")

        assert hasattr(exception, "message")
        assert exception.message == "Test message"

    def test_message_attribute_with_special_characters(self):
        """Test message with special characters."""
        special_message = "Invalid data: @#$%^&*()"
        exception = InvalidGeoLocationError(special_message)

        assert exception.message == special_message

    def test_message_attribute_with_unicode(self):
        """Test message with unicode characters."""
        unicode_message = "Invalid géo locatión: 位置"
        exception = InvalidGeoLocationError(unicode_message)

        assert exception.message == unicode_message

    def test_message_attribute_with_numbers(self):
        """Test message with numbers."""
        message_with_numbers = "Invalid boundary: expected 4 points, got 2"
        exception = InvalidGeoLocationError(message_with_numbers)

        assert exception.message == message_with_numbers


class TestInvalidGeoLocationErrorStringRepresentation:
    """Test string representation and formatting."""

    def test_str_representation_default_message(self):
        """Test str() with default message."""
        exception = InvalidGeoLocationError()

        assert str(exception) == "Invalid geo location data"

    def test_str_representation_custom_message(self):
        """Test str() with custom message."""
        custom_message = "Boundary data validation failed"
        exception = InvalidGeoLocationError(custom_message)

        assert str(exception) == custom_message

    def test_repr_representation(self):
        """Test repr() representation."""
        exception = InvalidGeoLocationError("Test error")

        repr_str = repr(exception)
        assert "InvalidGeoLocationError" in repr_str or "Test error" in repr_str

    def test_exception_args_attribute(self):
        """Test that exception args tuple contains message."""
        message = "Custom error message"
        exception = InvalidGeoLocationError(message)

        assert message in exception.args


class TestInvalidGeoLocationErrorComparison:
    """Test exception comparison and equality."""

    def test_two_exceptions_with_same_message(self):
        """Test two exceptions with same message."""
        exception1 = InvalidGeoLocationError("Same message")
        exception2 = InvalidGeoLocationError("Same message")

        assert exception1.message == exception2.message
        assert str(exception1) == str(exception2)

    def test_two_exceptions_with_different_messages(self):
        """Test two exceptions with different messages."""
        exception1 = InvalidGeoLocationError("Message 1")
        exception2 = InvalidGeoLocationError("Message 2")

        assert exception1.message != exception2.message
        assert str(exception1) != str(exception2)


class TestInvalidGeoLocationErrorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_exception_with_very_long_message(self):
        """Test exception with very long message."""
        long_message = "Invalid geo location data: " + "x" * 1000
        exception = InvalidGeoLocationError(long_message)

        assert len(exception.message) > 1000
        assert exception.message == long_message

    def test_exception_with_none_like_string(self):
        """Test exception with 'None' as string."""
        exception = InvalidGeoLocationError("None")

        assert exception.message == "None"
        assert exception.message is not None

    def test_exception_message_with_quotes(self):
        """Test exception message containing quotes."""
        message_with_quotes = 'Boundary "polygon" is invalid'
        exception = InvalidGeoLocationError(message_with_quotes)

        assert exception.message == message_with_quotes

    def test_exception_message_with_newlines(self):
        """Test exception message with newline characters."""
        message_with_newlines = "Error occurred:\nLine 1\nLine 2"
        exception = InvalidGeoLocationError(message_with_newlines)

        assert "\n" in exception.message
        assert exception.message == message_with_newlines


class TestInvalidGeoLocationErrorUsageScenarios:
    """Test real-world usage scenarios."""

    def test_exception_in_validation_context(self):
        """Test exception in typical validation context."""

        def validate_boundary(boundary):
            if boundary is None:
                raise InvalidGeoLocationError("Geo Location boundary cannot be None or empty.")
            return True

        with pytest.raises(InvalidGeoLocationError, match="cannot be None or empty"):
            validate_boundary(None)

    def test_exception_in_processing_context(self):
        """Test exception in data processing context."""

        def process_wkt(wkt_string):
            if not wkt_string or not isinstance(wkt_string, str):
                raise InvalidGeoLocationError("Invalid WKT format provided")
            return wkt_string

        with pytest.raises(InvalidGeoLocationError, match="Invalid WKT format"):
            process_wkt("")

    def test_exception_chaining(self):
        """Test exception can be chained with other exceptions."""

        def outer_function():
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise InvalidGeoLocationError("Wrapped error") from e

        with pytest.raises(InvalidGeoLocationError) as exc_info:
            outer_function()

        assert exc_info.value.message == "Wrapped error"
        assert exc_info.value.__cause__ is not None

    def test_multiple_exceptions_raised(self):
        """Test raising multiple exceptions in sequence."""
        exceptions_raised = []

        for i in range(3):
            try:
                raise InvalidGeoLocationError(f"Error {i}")
            except InvalidGeoLocationError as e:
                exceptions_raised.append(e.message)

        assert len(exceptions_raised) == 3
        assert exceptions_raised[0] == "Error 0"
        assert exceptions_raised[1] == "Error 1"
        assert exceptions_raised[2] == "Error 2"

    def test_exception_with_formatted_message(self):
        """Test exception with formatted message."""
        postal_code = "10115"
        message = f"Invalid boundary for postal code: {postal_code}"

        with pytest.raises(InvalidGeoLocationError):
            raise InvalidGeoLocationError(message)
