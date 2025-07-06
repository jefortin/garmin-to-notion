from src.core.notion import NotionDatabase, NotionDatabaseColumn
from ._database_schema import DatabaseSchemaFactory, NotionDatabaseSchema, NotionColumnSchema
from ._interface import DatabaseValidationError, INotionDatabaseValidator
from ..._synchronization_plan import SynchronizationPlan


class NotionDatabaseValidatorV1(INotionDatabaseValidator):
    """
    First iteration of the INotionDatabaseValidator implementation.
    Validates that a Notion database matches the expected schema by checking:
        - The Notion database's name matches the expected name.
        - The Notion database contains all the required columns.
        - The types of the Notion database columns are compatible with those of the configured synchronized fields.
    """

    def __init__(self, database_schema_factory: DatabaseSchemaFactory):
        self.__database_schema_factory = database_schema_factory

    def validate_database(
        self,
        database: NotionDatabase,
        synchronization_plan: SynchronizationPlan,
    ) -> list[DatabaseValidationError]:
        """
        Validates that a Notion database matches the expected schema.
        Returns a list of validation errors if the database does not match the schema.
        If no errors are returned, the Notion database can be considered compatible with the specification.
        """

        database_schema = self.__database_schema_factory.create(
            synchronization_plan.notion_database_name,
            synchronization_plan.synchronized_fields,
        )

        if validation_errors := self.__check_if_database_name_valid(database, database_schema):
            # Early exit here. Since the name is not correct, we can't assume that this is the intended database.
            return [validation_errors]

        if validation_errors := self.__check_column_schemas_are_valid(database.properties, database_schema.columns):
            return validation_errors

        return []

    @staticmethod
    def __check_if_database_name_valid(
        database: NotionDatabase,
        database_schema: NotionDatabaseSchema,
    ) -> DatabaseValidationError | None:
        """
        Checks if the name of the database matches the expected name.
        Returns a validation error if the names do not match.
        """
        if database_schema.name not in database.names:
            return DatabaseValidationError(
                message=(
                    f"Database names are [{', '.join(database.names)}]', "
                    f"which doesn't match the expected name: {database_schema.name}. "
                    "Double-check the database ID or rename the database."
                )
            )

        return None

    @staticmethod
    def __check_column_schemas_are_valid(
        database_columns: list[NotionDatabaseColumn],
        column_schemas: list[NotionColumnSchema],
    ) -> list[DatabaseValidationError] | None:
        """
        Validates that the columns in the database match the expected schema.
        Returns a validation error for every missing column or invalid column.
        """
        validation_errors = []

        for column_schema in column_schemas:
            matching_column = next(
                (
                    column
                    for column in database_columns
                    if column.name == column_schema.name
                ),
                None,
            )

            if matching_column is None:
                validation_errors.append(
                    DatabaseValidationError(message=f"Column '{column_schema.name}' does not exist in the database.")
                )
                continue  # Further validation is not required since the column does not exist.

            if matching_column.type not in column_schema.valid_types:
                valid_type_list = ', '.join((valid_type.value for valid_type in column_schema.valid_types))
                validation_errors.append(
                    DatabaseValidationError(
                        message=(
                            f"Column '{column_schema.name}' is of type '{matching_column.type.value}', "
                            f"but should be one of: {valid_type_list}."
                        )
                    )
                )

        return validation_errors
