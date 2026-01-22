"""Tests for the transform module."""

import pytest

from json_mapper.transform import (
    DEFAULT_HANDLERS,
    transform_from_mapping,
)


@pytest.fixture(name="input_data")
def input_data_fixture():
    """Fixture providing sample input data for transformation tests."""
    return {
        "agency_name": "Department of Examples",
        "opportunity_id": 12345,
        "opportunity_number": "ABC-123-XYZ-001",
        "opportunity_status": "posted",
        "opportunity_title": "Research into ABC",
        "summary": {
            "applicant_types": ["state_governments", "nonprofit"],
            "archive_date": "2025-05-01",
            "award_ceiling": 100000,
            "award_floor": 10000,
            "forecasted_award_date": "2025-09-01",
            "forecasted_close_date": "2025-07-15",
            "forecasted_post_date": "2025-05-01",
        },
    }


class TestBasicTransformations:
    """Tests for basic transformation operations."""

    def test_field_extraction(self, input_data):
        """
        Test basic field extraction from input data.

        Verifies that field values can be extracted from the input data.
        """
        mapping = {"title": {"field": "opportunity_title"}}
        result = transform_from_mapping(input_data, mapping)
        assert result == {"title": "Research into ABC"}

    def test_constant_value(self, input_data):
        """
        Test setting constant values in the output.

        Verifies that constant values can be set in the output.
        """
        mapping = {"agency": "Example Agency"}
        result = transform_from_mapping(input_data, mapping)
        assert result == {"agency": "Example Agency"}

    def test_field_and_constant_combined(self, input_data):
        """
        Test combining field extraction and constant values.

        Verifies that both field values and constants can be used in the same
        transformation.
        """
        mapping = {
            "title": {"field": "opportunity_title"},
            "agency": "Example Agency",
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {
            "title": "Research into ABC",
            "agency": "Example Agency",
        }

    def test_literal_value(self, input_data):
        """
        Test handling of literal values in the mapping.

        Verifies that literal values are passed through unchanged and
        non-dictionary values are treated as literals.
        """
        mapping = {"static": 42}
        result = transform_from_mapping(input_data, mapping)
        assert result == {"static": 42}


class TestSwitchHandler:
    """Tests for the switch/match transformation handler."""

    def test_switch_with_match(self, input_data):
        """
        Test the switch transformation handler with a matching value.

        Verifies that values can be transformed based on matching conditions.
        """
        mapping = {
            "status": {
                "switch": {
                    "field": "opportunity_status",
                    "case": {
                        "forecasted": "forecasted",
                        "posted": "open",
                        "archived": "closed",
                    },
                    "default": "custom",
                },
            },
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {"status": "open"}

    def test_switch_with_nested_object(self, input_data):
        """
        Test combination of switch transformations within nested structures.

        Verifies that switch transformations can be used within nested structures
        and that constants can be used alongside switches in nested objects.
        """
        mapping = {
            "status": {
                "value": {
                    "switch": {
                        "field": "opportunity_status",
                        "case": {
                            "forecasted": "forecasted",
                            "posted": "open",
                            "archived": "closed",
                        },
                        "default": "custom",
                    },
                },
                "description": "The opportunity is currently accepting applications",
            },
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {
            "status": {
                "value": "open",
                "description": "The opportunity is currently accepting applications",
            },
        }


class TestNestedStructures:
    """Tests for transformations involving nested object structures."""

    def test_nested_object(self, input_data):
        """
        Test transformation of nested object structures.

        Verifies that nested objects can be created in the output, field values
        can be extracted from nested input paths, and constants can be used
        within nested structures.
        """
        mapping = {
            "funding": {
                "minAwardAmount": {
                    "amount": {"field": "summary.award_floor"},
                    "currency": "USD",
                },
            },
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {
            "funding": {"minAwardAmount": {"amount": 10000, "currency": "USD"}},
        }

    def test_deeply_nested_structures(self, input_data):
        """
        Test transformation with deeply nested structures.

        Verifies that the transformation system can handle deeply nested objects,
        field paths can access deeply nested values, and the structure of deeply
        nested objects is preserved.
        """
        mapping = {
            "level1": {"level2": {"val": {"field": "summary.forecasted_award_date"}}},
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {"level1": {"level2": {"val": "2025-09-01"}}}


class TestListHandling:
    """Tests for handling list fields in transformations."""

    def test_list_field_extraction(self, input_data):
        """
        Test extraction of list fields from the input data.

        Verifies that list values can be extracted from the input data and
        lists are preserved in their original form.
        """
        mapping = {"applicant_types": {"field": "summary.applicant_types"}}
        result = transform_from_mapping(input_data, mapping)
        assert result == {"applicant_types": ["state_governments", "nonprofit"]}


class TestCustomHandlers:
    """Tests for extending the transformation system with custom handlers."""

    def test_concat_handler(self, input_data):
        """
        Test custom handler for concatenating values.

        Verifies that custom handlers can be added to the transformation system,
        the concat handler can combine multiple transformed values, and the
        handler works with both field values and constants.
        """

        # Patch in a concat handler for this test
        def handle_concat(data, concat_spec):
            return "".join(
                str(transform_from_mapping(data, part)) for part in concat_spec["parts"]
            )

        DEFAULT_HANDLERS["concat"] = handle_concat

        mapping = {
            "opportunity_code": {
                "concat": {
                    "parts": [
                        {"field": "opportunity_number"},
                        "-",
                        {"field": "opportunity_id"},
                    ],
                },
            },
        }
        result = transform_from_mapping(input_data, mapping)
        assert result == {"opportunity_code": "ABC-123-XYZ-001-12345"}

    def test_type_conversion_handler(self, input_data):
        """
        Test custom handler for type conversion.

        Verifies that custom handlers can perform type conversions, the type
        handler can convert values to different types, and custom handlers can
        be passed explicitly to transform_from_mapping.
        """

        def handle_type(data, type_spec):
            value = transform_from_mapping(data, type_spec["value"])
            typ = type_spec["to"]
            if typ == "string":
                return str(value)
            elif typ == "number":
                return float(value)  # type: ignore
            return value

        handlers = {
            **DEFAULT_HANDLERS,
            "type": handle_type,
        }

        mapping = {
            "id_str": {"type": {"value": {"field": "opportunity_id"}, "to": "string"}},
        }
        result = transform_from_mapping(input_data, mapping, handlers=handlers)
        assert result == {"id_str": "12345"}


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_missing_field_returns_none(self, input_data):
        """
        Test behavior when accessing non-existent fields.

        Verifies that attempting to access a non-existent field returns None
        and the transformation continues to work even with missing fields.
        """
        mapping = {"foo": {"field": "nonexistent"}}
        result = transform_from_mapping(input_data, mapping)
        assert result == {"foo": None}
