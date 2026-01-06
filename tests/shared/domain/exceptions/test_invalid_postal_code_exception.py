"""
Unit Tests for InvalidPostalCodeError Exception.

Test categories:
- Exception creation and initialization
- Exception inheritance
- Exception raising and catching
- Message handling
- String representation
"""

import pytest

from src.shared.domain.exceptions import InvalidPostalCodeError


class TestInvalidPostalCodeErrorCreation:
    """Test exception creation and initialization."""

    def test_create_exception_with_default_message(self):
        """Test creating exception with default message."""
        exception = InvalidPostalCodeError()

        assert exception.message == "Invalid postal code"
        assert str(exception) == "Invalid postal code"

    def test_create_exception_with_custom_message(self):
        """Test creating exception with custom message."""
        custom_message = "Postal code cannot be None or empty"
        exception = InvalidPostalCodeError(custom_message)

        assert exception.message == custom_message
        assert str(exception) == custom_message

    def test_create_exception_with_empty_message(self):
        """Test creating exception with empty message."""
        exception = InvalidPostalCodeError("")

        assert exception.message == ""
        assert str(exception) == ""

    def test_create_exception_with_multiline_message(self):
        """Test creating exception with multiline message."""
        multiline_message = "Postal code validation failed:\n- Must be 5 digits\n- Must be numeric"
        exception = InvalidPostalCodeError(multiline_message)

        assert exception.message == multiline_message
        assert str(exception) == multiline_message


class TestInvalidPostalCodeErrorInheritance:
    """Test exception inheritance and type checking."""

    def test_exception_inherits_from_value_error(self):
        """Test that InvalidPostalCodeError inherits from ValueError."""
        exception = InvalidPostalCodeError()

        assert isinstance(exception, ValueError)

    def test_exception_inherits_from_exception(self):
        """Test that InvalidPostalCodeError inherits from Exception."""
        exception = InvalidPostalCodeError()

        assert isinstance(exception, Exception)

    def test_exception_is_base_exception(self):
        """Test that InvalidPostalCodeError inherits from BaseException."""
        exception = InvalidPostalCodeError()

        assert isinstance(exception, BaseException)

    def test_exception_type_check(self):
        """Test exception type check."""
        exception = InvalidPostalCodeError("Test message")

        assert type(exception).__name__ == "InvalidPostalCodeError"


class TestInvalidPostalCodeErrorRaising:
    """Test exception raising and catching."""

    def test_raise_exception_with_default_message(self):
        """Test raising exception with default message."""
        with pytest.raises(InvalidPostalCodeError) as exc_info:
            raise InvalidPostalCodeError()

        assert exc_info.value.message == "Invalid postal code"

    def test_raise_exception_with_custom_message(self):
        """Test raising exception with custom message."""
        custom_message = "Postal code must be numeric"

        with pytest.raises(InvalidPostalCodeError) as exc_info:
            raise InvalidPostalCodeError(custom_message)

        assert exc_info.value.message == custom_message
        assert str(exc_info.value) == custom_message

    def test_catch_as_value_error(self):
        """Test catching InvalidPostalCodeError as ValueError."""
        with pytest.raises(ValueError) as exc_info:
            raise InvalidPostalCodeError("Test error")

        assert isinstance(exc_info.value, InvalidPostalCodeError)

    def test_catch_as_exception(self):
        """Test catching InvalidPostalCodeError as Exception."""
        with pytest.raises(Exception) as exc_info:
            raise InvalidPostalCodeError("Test error")

        assert isinstance(exc_info.value, InvalidPostalCodeError)

    def test_exception_message_in_traceback(self):
        """Test that exception message appears in error info."""
        custom_message = "Postal code must be exactly 5 digits"

        with pytest.raises(InvalidPostalCodeError, match=custom_message):
            raise InvalidPostalCodeError(custom_message)

    def test_exception_with_regex_match(self):
        """Test exception message with regex pattern matching."""
        with pytest.raises(InvalidPostalCodeError, match=r"Postal code.*must start with"):
            raise InvalidPostalCodeError("Postal code must start with 10, 12, 13, or 14")


class TestInvalidPostalCodeErrorMessageAttribute:
    """Test message attribute access and manipulation."""

    def test_message_attribute_accessible(self):
        """Test that message attribute is accessible."""
        exception = InvalidPostalCodeError("Test message")

        assert hasattr(exception, "message")
        assert exception.message == "Test message"

    def test_message_attribute_with_special_characters(self):
        """Test message with special characters."""
        special_message = "Invalid code: @#$%^&*()"
        exception = InvalidPostalCodeError(special_message)

        assert exception.message == special_message

    def test_message_attribute_with_postal_code_in_message(self):
        """Test message containing postal code value."""
        message = "Postal code must be exactly 5 digits: '123'"
        exception = InvalidPostalCodeError(message)

        assert exception.message == message
        assert "'123'" in exception.message

    def test_message_attribute_with_numbers(self):
        """Test message with numbers."""
        message_with_numbers = "Expected 5 digits, got 4"
        exception = InvalidPostalCodeError(message_with_numbers)

        assert exception.message == message_with_numbers


class TestInvalidPostalCodeErrorStringRepresentation:
    """Test string representation and formatting."""

    def test_str_representation_default_message(self):
        """Test str() with default message."""
        exception = InvalidPostalCodeError()

        assert str(exception) == "Invalid postal code"

    def test_str_representation_custom_message(self):
        """Test str() with custom message."""
        custom_message = "Postal code validation failed"
        exception = InvalidPostalCodeError(custom_message)

        assert str(exception) == custom_message

    def test_repr_representation(self):
        """Test repr() representation."""
        exception = InvalidPostalCodeError("Test error")

        repr_str = repr(exception)
        assert "InvalidPostalCodeError" in repr_str or "Test error" in repr_str

    def test_exception_args_attribute(self):
        """Test that exception args tuple contains message."""
        message = "Custom error message"
        exception = InvalidPostalCodeError(message)

        assert message in exception.args


class TestInvalidPostalCodeErrorComparison:
    """Test exception comparison and equality."""

    def test_two_exceptions_with_same_message(self):
        """Test two exceptions with same message."""
        exception1 = InvalidPostalCodeError("Same message")
        exception2 = InvalidPostalCodeError("Same message")

        assert exception1.message == exception2.message
        assert str(exception1) == str(exception2)

    def test_two_exceptions_with_different_messages(self):
        """Test two exceptions with different messages."""
        exception1 = InvalidPostalCodeError("Message 1")
        exception2 = InvalidPostalCodeError("Message 2")

        assert exception1.message != exception2.message
        assert str(exception1) != str(exception2)


class TestInvalidPostalCodeErrorEdgeCases:
    """Test edge cases and special scenarios."""

    def test_exception_with_very_long_message(self):
        """Test exception with very long message."""
        long_message = "Invalid postal code: " + "x" * 1000
        exception = InvalidPostalCodeError(long_message)

        assert len(exception.message) > 1000
        assert exception.message == long_message

    def test_exception_with_none_like_string(self):
        """Test exception with 'None' as string."""
        exception = InvalidPostalCodeError("None")

        assert exception.message == "None"
        assert exception.message is not None

    def test_exception_message_with_quotes(self):
        """Test exception message containing quotes."""
        message_with_quotes = 'Postal code "12345" is invalid'
        exception = InvalidPostalCodeError(message_with_quotes)

        assert exception.message == message_with_quotes

    def test_exception_message_with_newlines(self):
        """Test exception message with newline characters."""
        message_with_newlines = "Error occurred:\nInvalid format\nMust be numeric"
        exception = InvalidPostalCodeError(message_with_newlines)

        assert "\n" in exception.message
        assert exception.message == message_with_newlines

    def test_exception_message_with_single_quotes(self):
        """Test exception message with single quotes."""
        message = "Postal code must be numeric: '1011A'"
        exception = InvalidPostalCodeError(message)

        assert "'" in exception.message
        assert exception.message == message


class TestInvalidPostalCodeErrorUsageScenarios:
    """Test real-world usage scenarios."""

    def test_exception_in_none_validation_context(self):
        """Test exception when postal code is None."""

        def validate_postal_code(postal_code):
            if postal_code is None:
                raise InvalidPostalCodeError("Postal code cannot be None or empty.")
            return True

        with pytest.raises(InvalidPostalCodeError, match="cannot be None or empty"):
            validate_postal_code(None)

    def test_exception_in_empty_validation_context(self):
        """Test exception when postal code is empty."""

        def validate_postal_code(postal_code):
            if not postal_code or not postal_code.strip():
                raise InvalidPostalCodeError("Postal code cannot be None or empty.")
            return True

        with pytest.raises(InvalidPostalCodeError, match="cannot be None or empty"):
            validate_postal_code("")

    def test_exception_in_numeric_validation_context(self):
        """Test exception when postal code is not numeric."""

        def validate_numeric(postal_code):
            if not postal_code.isdigit():
                raise InvalidPostalCodeError(f"Postal code must be numeric: '{postal_code}'.")
            return True

        with pytest.raises(InvalidPostalCodeError, match="must be numeric: '1011A'"):
            validate_numeric("1011A")

    def test_exception_in_length_validation_context(self):
        """Test exception when postal code has wrong length."""

        def validate_length(postal_code):
            if len(postal_code) != 5:
                raise InvalidPostalCodeError(f"Postal code must be exactly 5 digits: '{postal_code}'.")
            return True

        with pytest.raises(InvalidPostalCodeError, match="must be exactly 5 digits: '123'"):
            validate_length("123")

    def test_exception_in_berlin_rule_validation_context(self):
        """Test exception when postal code doesn't follow Berlin rules."""

        def validate_berlin_rule(postal_code):
            if not postal_code.startswith(("10", "12", "13", "14")):
                raise InvalidPostalCodeError(f"Berlin postal code must start with 10, 12, 13, or 14: '{postal_code}'.")
            return True

        with pytest.raises(InvalidPostalCodeError, match="must start with 10, 12, 13, or 14: '99999'"):
            validate_berlin_rule("99999")

    def test_exception_chaining(self):
        """Test exception can be chained with other exceptions."""

        def outer_function():
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise InvalidPostalCodeError("Wrapped postal code error") from e

        with pytest.raises(InvalidPostalCodeError) as exc_info:
            outer_function()

        assert exc_info.value.message == "Wrapped postal code error"
        assert exc_info.value.__cause__ is not None

    def test_multiple_exceptions_raised_in_sequence(self):
        """Test raising multiple exceptions in sequence."""
        exceptions_raised = []

        for code in ["ABC", "123", "99999"]:
            try:
                raise InvalidPostalCodeError(f"Invalid code: {code}")
            except InvalidPostalCodeError as e:
                exceptions_raised.append(e.message)

        assert len(exceptions_raised) == 3
        assert "ABC" in exceptions_raised[0]
        assert "123" in exceptions_raised[1]
        assert "99999" in exceptions_raised[2]

    def test_exception_with_formatted_message(self):
        """Test exception with formatted message."""
        postal_code = "1011A"
        message = f"Postal code must be numeric: '{postal_code}'"

        with pytest.raises(InvalidPostalCodeError) as exc_info:
            raise InvalidPostalCodeError(message)

        assert "1011A" in exc_info.value.message
        assert "must be numeric" in exc_info.value.message

    def test_exception_in_complete_validation_workflow(self):
        """Test exception in a complete validation workflow."""

        def validate_complete(postal_code):
            if postal_code is None or not postal_code.strip():
                raise InvalidPostalCodeError("Postal code cannot be None or empty.")

            cleaned = postal_code.strip()

            if not cleaned.isdigit():
                raise InvalidPostalCodeError(f"Postal code must be numeric: '{cleaned}'.")

            if len(cleaned) != 5:
                raise InvalidPostalCodeError(f"Postal code must be exactly 5 digits: '{cleaned}'.")

            if not cleaned.startswith(("10", "12", "13", "14")):
                raise InvalidPostalCodeError(f"Berlin postal code must start with 10, 12, 13, or 14: '{cleaned}'.")

            return True

        # Test various invalid inputs
        with pytest.raises(InvalidPostalCodeError, match="cannot be None or empty"):
            validate_complete(None)

        with pytest.raises(InvalidPostalCodeError, match="must be numeric"):
            validate_complete("1011A")

        with pytest.raises(InvalidPostalCodeError, match="must be exactly 5 digits"):
            validate_complete("123")

        with pytest.raises(InvalidPostalCodeError, match="must start with 10, 12, 13, or 14"):
            validate_complete("99999")
