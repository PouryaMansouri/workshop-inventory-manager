"""
CSV Import Service for bulk ItemInstance creation.
"""
import csv
from io import StringIO
from typing import Dict, List, Tuple
from django.db import transaction
from apps.inventory.models import Product, ItemInstance, Location


class CSVImportService:
    """Service for importing ItemInstances from CSV files."""
    
    @staticmethod
    def parse_csv(csv_content: str) -> List[Dict[str, str]]:
        """
        Parse CSV content into list of dictionaries.
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            List of dictionaries with keys: product_sku, serial_number, location
        """
        reader = csv.DictReader(StringIO(csv_content))
        rows = []
        
        for row in reader:
            rows.append({
                'product_sku': row.get('product_sku', '').strip(),
                'serial_number': row.get('serial_number', '').strip(),
                'location': row.get('location', '').strip(),
            })
        
        return rows
    
    @staticmethod
    def validate_row(row: Dict[str, str], row_number: int) -> Tuple[bool, str]:
        """
        Validate a single CSV row.
        
        Args:
            row: Dictionary with product_sku, serial_number, location
            row_number: Row number for error reporting
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields
        if not row['product_sku']:
            return False, f"Row {row_number}: product_sku is required"
        
        if not row['serial_number']:
            return False, f"Row {row_number}: serial_number is required"

        if not row['location']:
            return False, f"Row {row_number}: location is required"
        
        # Check if product exists
        try:
            Product.objects.get(sku_code=row['product_sku'])
        except Product.DoesNotExist:
            return False, f"Row {row_number}: Product with SKU '{row['product_sku']}' not found"
        
        # Check if serial number already exists
        if ItemInstance.objects.filter(serial_number=row['serial_number']).exists():
            return False, f"Row {row_number}: Serial number '{row['serial_number']}' already exists"
        
        if not Location.objects.filter(name=row['location']).exists():
            return False, f"Row {row_number}: Location '{row['location']}' not found"
        
        return True, ""
    
    @staticmethod
    @transaction.atomic
    def import_items(csv_content: str) -> Dict[str, any]:
        """
        Import ItemInstances from CSV content.
        
        CSV Format:
            product_sku,serial_number,location
            COL-WRN-001,12345,Main Warehouse
            COL-WRN-001,12346,Shelf A
        
        Args:
            csv_content: CSV file content as string
            
        Returns:
            Dictionary with import results:
            {
                'success': True/False,
                'created_count': int,
                'error_count': int,
                'errors': List[str],
                'created_items': List[ItemInstance]
            }
        """
        result = {
            'success': True,
            'created_count': 0,
            'error_count': 0,
            'errors': [],
            'created_items': []
        }
        
        try:
            rows = CSVImportService.parse_csv(csv_content)
        except Exception as e:
            result['success'] = False
            result['errors'].append(f"CSV parsing error: {str(e)}")
            return result
        
        if not rows:
            result['success'] = False
            result['errors'].append("CSV file is empty or invalid")
            return result
        
        # Validate all rows first
        for idx, row in enumerate(rows, start=2):  # Start from 2 (header is row 1)
            is_valid, error_msg = CSVImportService.validate_row(row, idx)
            if not is_valid:
                result['errors'].append(error_msg)
                result['error_count'] += 1
        
        # If there are validation errors, don't import anything
        if result['error_count'] > 0:
            result['success'] = False
            return result
        
        # Import all rows
        for idx, row in enumerate(rows, start=2):
            try:
                product = Product.objects.get(sku_code=row['product_sku'])
                
                # Get location if provided
                location = None
                if row['location']:
                    location = Location.objects.get(name=row['location'])
                
                # Create ItemInstance
                item = ItemInstance.objects.create(
                    product=product,
                    serial_number=row['serial_number'],
                    location=location,
                    status='available'
                )
                
                result['created_items'].append(item)
                result['created_count'] += 1
                
            except Exception as e:
                result['errors'].append(f"Row {idx}: {str(e)}")
                result['error_count'] += 1
                result['success'] = False
                # The decorator's atomic block must roll back earlier rows too.
                transaction.set_rollback(True)
                result['created_count'] = 0
                result['created_items'] = []
                break
        
        return result
    
    @staticmethod
    def generate_import_report(result: Dict[str, any]) -> str:
        """
        Generate a human-readable import report.
        
        Args:
            result: Import result dictionary from import_items()
            
        Returns:
            Formatted report string
        """
        report_lines = []
        
        if result['success']:
            report_lines.append(f"✅ Import successful!")
            report_lines.append(f"Created {result['created_count']} items")
        else:
            report_lines.append(f"❌ Import failed")
            report_lines.append(f"Created: {result['created_count']}")
            report_lines.append(f"Errors: {result['error_count']}")
            report_lines.append("")
            report_lines.append("Error details:")
            for error in result['errors']:
                report_lines.append(f"  - {error}")
        
        return "\n".join(report_lines)
