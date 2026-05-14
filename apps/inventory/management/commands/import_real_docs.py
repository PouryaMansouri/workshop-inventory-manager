"""Management command to bootstrap inventory data from real_docs Excel files."""
from django.core.management.base import BaseCommand

from core.services.excel_import_service import ExcelImportService


class Command(BaseCommand):
    help = 'Reset operational data and import from real_docs Excel files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            default='real_docs',
            help='Path to directory containing real Excel files',
        )

    def handle(self, *args, **options):
        result = ExcelImportService.import_from_real_docs(options['path'])
        if result['success']:
            self.stdout.write(self.style.SUCCESS('Import completed successfully'))
            self.stdout.write(str(result['created_count']))
            return

        self.stdout.write(self.style.ERROR('Import failed'))
        for err in result['errors']:
            self.stdout.write(self.style.ERROR(err))
