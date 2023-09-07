"""Test models."""
from __future__ import annotations

import datetime
import uuid
from _decimal import Decimal
from enum import auto, Enum
from typing import Literal

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    AwareDatetime,
    BaseModel,
    constr,
    Field,
    FutureDate,
    FutureDatetime,
    HttpUrl,
    Json,
    NaiveDatetime,
    PastDate,
    PastDatetime,
    PositiveInt,
    StrictBool,
    NegativeInt,
    NonPositiveInt,
    NonNegativeInt,
    StrictInt,
    PositiveFloat,
    NegativeFloat,
    NonPositiveFloat,
    NonNegativeFloat,
    StrictFloat,
    FiniteFloat,
    StrictBytes,
    StrictStr,
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    Base64Bytes,
    Base64Str,
    PostgresDsn,
    CockroachDsn,
    AmqpDsn,
    RedisDsn,
    MongoDsn,
    KafkaDsn,
    MySQLDsn,
    MariaDBDsn,
    EmailStr,
    NameEmail,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
)
from pydantic_extra_types.color import Color
from pydantic_extra_types.payment import PaymentCardBrand, PaymentCardNumber
from pydantic_extra_types.routing_number import ABARoutingNumber


class Flavor(Enum):
    """Flavor options."""

    MOCHA = "mocha"
    VANILLA = "vanilla"
    PEPPERMINT = "peppermint"


class Numbers(Enum):
    """Number options."""

    ONE = auto()
    TWO = auto()
    THREE = auto()


class Primitives(BaseModel):
    int_field: int
    float_field: float
    str_field: str
    bool_field: bool
    bytes_field: bytes
    none_field: None


class PythonTypes(BaseModel):
    str_enum: Flavor
    num_enum: Numbers
    date: datetime.date
    time: datetime.time
    datetime_field: datetime.datetime
    timedelta: datetime.timedelta
    uuid_field: uuid.UUID
    decimal: Decimal


class Defaults(BaseModel):
    str_field: str = "1"
    int_field: int = 1
    float_field: float = 1.0
    bool_true: bool = True
    bool_false: bool = False
    list_field: list[str] | None = None


class Constantly(BaseModel):
    const_str_field: Literal["Cat."]
    const_num_field: Literal[3]
    const_none_field: Literal[None]
    const_true_field: Literal[True]
    const_false_field: Literal[False]


class VanillaModel(BaseModel):
    bool_field: bool


class RecursiveModel(BaseModel):
    child: RecursiveModel | None = None


class CollectionsModel(BaseModel):
    list_field: list
    list_str: list[str]
    list_list: list[list]
    list_list_int: list[list[int]]
    list_model: list[VanillaModel]
    list_model_or_model: list[VanillaModel | RecursiveModel]
    list_union: list[str | int]
    list_dict: list[dict]
    list_dict_str: list[dict[str, str]]
    list_dict_int_keys: list[dict[int, str]]
    tuple_field: tuple
    tuple_str: tuple[str]
    tuple_tuple: tuple[tuple]
    tuple_tuple_int: tuple[tuple[int]]
    tuple_model: tuple[VanillaModel]
    tuple_union: tuple[str | int]
    tuple_int_str_none: tuple[int, str, None]
    set_str: set[str]
    set_union: set[str | int]
    dict_field: dict
    dict_str: dict[str, str]
    dict_dict: dict[str, dict]
    dict_int_keys: dict[int, str]
    dict_model: dict[str, VanillaModel]
    dict_model_or_model: dict[str, VanillaModel | RecursiveModel]
    dict_union: dict[str, str | int]
    dict_list: dict[str, list[int]]


class ConstrainedCollections(BaseModel):
    list_min: list = Field(min_items=5)
    list_max: list[str] = Field(max_items=7)
    list_min_max: list[str] = Field(min_items=5, max_items=7)


class PydanticTypes(BaseModel):
    strict_bool: StrictBool
    positive_int: PositiveInt
    negative_int: NegativeInt
    non_positive_int: NonPositiveInt
    non_negative_int: NonNegativeInt
    strict_int: StrictInt
    positive_float: PositiveFloat
    negative_float: NegativeFloat
    non_positive_float: NonPositiveFloat
    non_negative_float: NonNegativeFloat
    strict_float: StrictFloat
    finite_float: FiniteFloat
    strict_bytes: StrictBytes
    strict_str: StrictStr
    uuid1: UUID1
    uuid3: UUID3
    uuid4: UUID4
    uuid5: UUID5
    base64bytes: Base64Bytes
    base64str: Base64Str
    str_constraints_strip_whitespace: constr(strip_whitespace=True)
    str_constraints_to_upper: constr(to_upper=True)
    str_constraints_to_lower: constr(to_lower=True)
    str_constraints_strict: constr(strict=True)
    str_constraints_min_length: constr(min_length=10)
    str_constraints_max_length: constr(max_length=1)
    json_field: Json
    past_date: PastDate
    future_date: FutureDate
    aware_datetime: AwareDatetime
    naive_datetime: NaiveDatetime
    past_datetime: PastDatetime
    future_datetime: FutureDatetime


class PydanticNetworkTypes(BaseModel):
    any_url: AnyUrl
    any_http_url: AnyHttpUrl
    http_url: HttpUrl
    postgres_dsn: PostgresDsn
    cockroach_dsn: CockroachDsn
    amqp_dsn: AmqpDsn
    redis_dsn: RedisDsn
    mongo_dsn: MongoDsn
    kafka_dsn: KafkaDsn
    mysql_dsn: MySQLDsn
    mariadb_dsn: MariaDBDsn
    email_str: EmailStr
    name_email: NameEmail
    ipv_any_address: IPvAnyAddress
    ipv_any_interface: IPvAnyInterface
    ipv_any_network: IPvAnyNetwork


class PydanticExtra(BaseModel):
    color: Color
    payment_card_brand: PaymentCardBrand
    payment_card_number: PaymentCardNumber
    aba_routing_number: ABARoutingNumber


class RefModel(BaseModel):
    flavor: Flavor
    numbers: Numbers
    primitives: Primitives
    python_types: PythonTypes
    defaults: Defaults
    constantly: Constantly
    vanilla_model: VanillaModel
    recursive_model: RecursiveModel
    collections_model: CollectionsModel
    constrained_collections: ConstrainedCollections
    pydantic_types: PydanticTypes
    pydantic_network_types: PydanticNetworkTypes
    pydantic_extra: PydanticExtra
