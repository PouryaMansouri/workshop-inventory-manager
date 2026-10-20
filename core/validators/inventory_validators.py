"""
Validators for inventory-related operations.
"""
from typing import Optional
from django.core.exceptions import ValidationError
from apps.inventory.models import ItemInstance, Product, Location


class InventoryValidators:
    """Validators for inventory operations."""
    
    @staticmethod
    def validate_serial_number_unique(serial_number: str, exclude_id: Optional[int] = None) -> None:
        """
        Validate that serial number is unique.
        
        Args:
            serial_number: Serial number to validate
            exclude_id: Optional ItemInstance ID to exclude from check (for updates)
            
        Raises:
            ValidationError: If serial number already exists
        """
        queryset = ItemInstance.objects.filter(serial_number=serial_number)
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        if queryset.exists():
            raise ValidationError(
                f"Serial number '{serial_number}' already exists."
            )
    
    @staticmethod
    def validate_barcode_unique(barcode: str, exclude_id: Optional[int] = None) -> None:
        """
        Validate that barcode is unique.
        
        Args:
            barcode: Barcode to validate
            exclude_id: Optional ItemInstance ID to exclude from check
            
        Raises:
            ValidationError: If barcode already exists
        """
        queryset = ItemInstance.objects.filter(barcode=barcode)
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        if queryset.exists():
            raise ValidationError(
                f"Barcode '{barcode}' already exists."
            )
    
    @staticmethod
    def validate_product_exists(product_id: int) -> Product:
        """
        Validate that product exists.
        
        Args:
            product_id: Product ID to validate
            
        Returns:
            Product object if exists
            
        Raises:
            ValidationError: If product doesn't exist
        """
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError(
                f"Product with ID {product_id} does not exist."
            )
    
    @staticmethod
    def validate_product_by_sku(sku_code: str) -> Product:
        """
        Validate that product exists by SKU code.
        
        Args:
            sku_code: SKU code to validate
            
        Returns:
            Product object if exists
            
        Raises:
            ValidationError: If product doesn't exist
        """
        try:
            return Product.objects.get(sku_code=sku_code)
        except Product.DoesNotExist:
            raise ValidationError(
                f"Product with SKU '{sku_code}' does not exist."
            )
    
    @staticmethod
    def validate_location_exists(location_id: int) -> Location:
        """
        Validate that location exists.
        
        Args:
            location_id: Location ID to validate
            
        Returns:
            Location object if exists
            
        Raises:
            ValidationError: If location doesn't exist
        """
        try:
            return Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            raise ValidationError(
                f"Location with ID {location_id} does not exist."
            )
    
    @staticmethod
    def validate_location_by_name(location_name: str) -> Location:
        """
        Validate that location exists by name.
        
        Args:
            location_name: Location name to validate
            
        Returns:
            Location object if exists
            
        Raises:
            ValidationError: If location doesn't exist
        """
        try:
            return Location.objects.get(name=location_name)
        except Location.DoesNotExist:
            raise ValidationError(
                f"Location '{location_name}' does not exist."
            )
    
    @staticmethod
    def validate_item_exists(item_id: int) -> ItemInstance:
        """
        Validate that item instance exists.
        
        Args:
            item_id: ItemInstance ID to validate
            
        Returns:
            ItemInstance object if exists
            
        Raises:
            ValidationError: If item doesn't exist
        """
        try:
            return ItemInstance.objects.select_related('product').get(id=item_id)
        except ItemInstance.DoesNotExist:
            raise ValidationError(
                f"Item with ID {item_id} does not exist."
            )
    
    @staticmethod
    def validate_item_status(item: ItemInstance, allowed_statuses: list) -> None:
        """
        Validate that item has one of the allowed statuses.
        
        Args:
            item: ItemInstance to validate
            allowed_statuses: List of allowed status values
            
        Raises:
            ValidationError: If item status is not in allowed list
        """
        if item.status not in allowed_statuses:
            raise ValidationError(
                f"Item status must be one of {allowed_statuses}, "
                f"but is currently '{item.status}'."
            )
    
    @staticmethod
    def validate_minimum_stock(minimum_stock: int) -> None:
        """
        Validate minimum stock value.
        
        Args:
            minimum_stock: Minimum stock value to validate
            
        Raises:
            ValidationError: If minimum stock is invalid
        """
        if minimum_stock < 0:
            raise ValidationError(
                "Minimum stock cannot be negative."
            )
    
    @staticmethod
    def validate_sku_format(sku_code: str) -> None:
        """
        Validate SKU code format.
        
        Expected format: PREFIX-CATEGORY-ID. New products use PRD as prefix;
        existing workshop-prefixed SKUs remain valid.
        
        Args:
            sku_code: SKU code to validate
            
        Raises:
            ValidationError: If SKU format is invalid
        """
        if not sku_code:
            raise ValidationError("SKU code cannot be empty.")
        
        parts = sku_code.split('-')
        if len(parts) != 3:
            raise ValidationError(
                f"SKU code '{sku_code}' has invalid format. "
                "Expected format: PREFIX-CATEGORY-ID"
            )
        
        prefix, category_code, item_id = parts
        
        if not prefix or not category_code or not item_id:
            raise ValidationError(
                "SKU code parts cannot be empty."
            )
        
        if not item_id.isdigit():
            raise ValidationError(
                f"SKU code ID part '{item_id}' must be numeric."
            )
    
    @staticmethod
    def validate_serial_number_format(serial_number: str) -> None:
        """
        Validate serial number format.
        
        Args:
            serial_number: Serial number to validate
            
        Raises:
            ValidationError: If serial number is invalid
        """
        if not serial_number:
            raise ValidationError("Serial number cannot be empty.")
        
        if len(serial_number) > 100:
            raise ValidationError(
                "Serial number cannot exceed 100 characters."
            )
    
    @staticmethod
    def validate_location_change(item: ItemInstance, new_location: Location) -> None:
        """
        Validate that location change is allowed.
        
        Args:
            item: ItemInstance to move
            new_location: New location
            
        Raises:
            ValidationError: If location change is not allowed
        """
        # Items that are checked out cannot change location
        if item.status == 'checked_out':
            raise ValidationError(
                "Cannot change location of checked out item. "
                "Please return the item first."
            )
        
        # Items that are lost cannot change location
        if item.status == 'lost':
            raise ValidationError(
                "Cannot change location of lost item."
            )
    
    @staticmethod
    def validate_bulk_operation(items: list, max_items: int = 100) -> None:
        """
        Validate bulk operation constraints.
        
        Args:
            items: List of items for bulk operation
            max_items: Maximum number of items allowed in bulk operation
            
        Raises:
            ValidationError: If bulk operation constraints are violated
        """
        if not items:
            raise ValidationError(
                "No items selected for bulk operation."
            )
        
        if len(items) > max_items:
            raise ValidationError(
                f"Bulk operation limited to {max_items} items. "
                f"You selected {len(items)} items."
            )
    
    @staticmethod
    def validate_product_consumable_flag(product: Product, is_consumable: bool) -> None:
        """
        Validate that product consumable flag change is allowed.
        
        Args:
            product: Product to validate
            is_consumable: New consumable flag value
            
        Raises:
            ValidationError: If change is not allowed
        """
        # If changing from non-consumable to consumable
        if not product.is_consumable and is_consumable:
            # Check if there are any checked out items
            checked_out_count = ItemInstance.objects.filter(
                product=product,
                status='checked_out'
            ).count()
            
            if checked_out_count > 0:
                raise ValidationError(
                    f"Cannot mark product as consumable. "
                    f"There are {checked_out_count} items currently checked out."
                )
