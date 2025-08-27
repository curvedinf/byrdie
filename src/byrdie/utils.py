import datetime

# A mapping from Django field types to Python types for Pydantic
FIELD_TYPE_MAPPING = {
    'AutoField': int,
    'BigAutoField': int,
    'CharField': str,
    'IntegerField': int,
    'PositiveIntegerField': int,
    'FloatField': float,
    'BooleanField': bool,
    'DateField': datetime.date,
    'DateTimeField': datetime.datetime,
    'EmailField': str,
    'URLField': str,
    'TextField': str,
    'ForeignKey': int,  # By default, we'll expose the foreign key ID
    'OneToOneField': int,
}
