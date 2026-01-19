"""
Pydantic schemas for Box validation and serialization.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from enum import Enum


class BoxSizeEnum(str, Enum):
    """Box size categories."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    XLARGE = "xlarge"
    CUSTOM = "custom"


class BoxStatusEnum(str, Enum):
    """Box status for API."""
    EMPTY = "empty"
    PACKING = "packing"
    SEALED = "sealed"
    LOADED = "loaded"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class BoxDimensions(BaseModel):
    """Box dimension specification."""
    length_cm: Decimal = Field(..., gt=0, le=200)
    width_cm: Decimal = Field(..., gt=0, le=200)
    height_cm: Decimal = Field(..., gt=0, le=200)
    
    @property
    def volume_cm3(self) -> Decimal:
        return self.length_cm * self.width_cm * self.height_cm


class BoxBase(BaseModel):
    """Base schema for box fields."""
    barcode: str = Field(..., min_length=1, max_length=100)
    order_id: int = Field(..., gt=0)
    size_category: BoxSizeEnum = Field(default=BoxSizeEnum.MEDIUM)
    dimensions: Optional[BoxDimensions] = None
    weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    max_weight_kg: Decimal = Field(default=Decimal("25.0"), gt=0)
    is_fragile: bool = Field(default=False)
    requires_refrigeration: bool = Field(default=False)
    is_stackable: bool = Field(default=True)


class BoxCreate(BoxBase):
    """Schema for creating a new box."""
    
    @field_validator("weight_kg")
    @classmethod
    def validate_weight(cls, v, info):
        max_weight = info.data.get("max_weight_kg", Decimal("25.0"))
        if v > max_weight:
            raise ValueError(f"Weight {v} exceeds maximum {max_weight}")
        return v


class BoxUpdate(BaseModel):
    """Schema for updating a box."""
    weight_kg: Optional[Decimal] = Field(default=None, ge=0)
    volume_used_cm3: Optional[Decimal] = Field(default=None, ge=0)
    status: Optional[BoxStatusEnum] = None
    sequence_index: Optional[int] = Field(default=None, ge=0)
    route_id: Optional[int] = Field(default=None, gt=0)
    is_fragile: Optional[bool] = None
    requires_refrigeration: Optional[bool] = None
    is_stackable: Optional[bool] = None


class BoxResponse(BaseModel):
    """Schema for box API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    barcode: str
    order_id: int
    route_id: Optional[int]
    size_category: str
    length_cm: Decimal
    width_cm: Decimal
    height_cm: Decimal
    weight_kg: Decimal
    max_weight_kg: Decimal
    volume_used_cm3: Decimal
    sequence_index: Optional[int]
    status: str
    is_fragile: bool
    requires_refrigeration: bool
    is_stackable: bool
    packed_at: Optional[datetime]
    loaded_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    @property
    def volume_cm3(self) -> Decimal:
        return self.length_cm * self.width_cm * self.height_cm
    
    @property
    def fill_percentage(self) -> float:
        vol = self.length_cm * self.width_cm * self.height_cm
        if vol == 0:
            return 0.0
        return float(self.volume_used_cm3 / vol * 100)


class BoxListResponse(BaseModel):
    """Paginated box list."""
    items: List[BoxResponse]
    total: int
    page: int
    page_size: int
    pages: int


class BoxSequenceUpdate(BaseModel):
    """Schema for updating box LIFO sequence."""
    box_ids: List[int] = Field(..., min_length=1)
    route_id: int = Field(..., gt=0)
    
    # Box IDs in order: first = sequence_index 1 (unload first)
    # This represents LIFO: first in list = top of stack = unload first
