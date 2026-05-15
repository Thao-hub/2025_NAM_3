from __future__ import annotations

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from modules.store.models import NhanVien


DEFAULT_SOURCE_DIR = Path(r"D:\Py\employee_images")


class Command(BaseCommand):
    help = "Import avatar images and assign them to employees in order."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            default=str(DEFAULT_SOURCE_DIR),
            help="Directory containing employee avatar images.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=1000,
            help="Maximum number of employees to update.",
        )
        parser.add_argument(
            "--start-index",
            type=int,
            default=1,
            help="Starting image index. employee_<start-index>.jpg will be used first.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the import without copying files or saving database changes.",
        )

    def handle(self, *args, **options):
        source_dir = Path(options["source_dir"]).expanduser()
        limit = options["limit"]
        start_index = options["start_index"]
        dry_run = options["dry_run"]

        if limit <= 0:
            raise CommandError("--limit must be greater than 0.")
        if start_index <= 0:
            raise CommandError("--start-index must be greater than 0.")
        if not source_dir.exists() or not source_dir.is_dir():
            raise CommandError(f"Source directory does not exist: {source_dir}")

        employees = list(
            NhanVien.objects.select_related("cua_hang")
            .order_by("pk")[:limit]
        )
        if not employees:
            raise CommandError("No employees found. Seed or create employees first.")

        dest_dir = Path(settings.MEDIA_ROOT) / "avatar" / "employees"
        copied = 0
        updated = 0

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)

        for offset, employee in enumerate(employees):
            image_index = start_index + offset
            source_file = source_dir / f"employee_{image_index}.jpg"

            if not source_file.exists():
                self.stdout.write(
                    self.style.WARNING(f"Skip employee #{employee.pk}: missing {source_file.name}")
                )
                continue

            relative_avatar = Path("avatar") / "employees" / source_file.name
            target_file = Path(settings.MEDIA_ROOT) / relative_avatar

            if not dry_run and not target_file.exists():
                shutil.copy2(source_file, target_file)
                copied += 1
            elif target_file.exists():
                copied += 1

            avatar_name = relative_avatar.as_posix()
            if employee.avatar.name != avatar_name:
                employee.avatar.name = avatar_name
                updated += 1
                if not dry_run:
                    employee.save(update_fields=["avatar"])

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Previewed' if dry_run else 'Imported'} avatars for {updated} employees; "
                f"{copied} image files available in media."
            )
        )

