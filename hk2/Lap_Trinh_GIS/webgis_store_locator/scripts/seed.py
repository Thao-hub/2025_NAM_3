#!/usr/bin/env python
"""Simple seed helper for local development."""

import os
import subprocess
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    avatar_source = os.environ.get('EMPLOYEE_AVATAR_SOURCE', r'D:\Py\employee_images')
    repo_avatar_source = os.environ.get('REPO_EMPLOYEE_AVATAR_SOURCE', r'media\avatar\employees')
    product_image_source = os.environ.get('PRODUCT_IMAGE_SOURCE', r'D:\LT_Gis\webgis_store_locator\media\images')

    commands = [
        [sys.executable, 'manage.py', 'migrate'],
        [sys.executable, 'manage.py', 'loaddata', 'modules/store/fixtures/store_data.json'],
        [sys.executable, 'manage.py', 'seed_product_prices'],
    ]

    if os.path.isdir(product_image_source):
        commands.append(
            [
                sys.executable,
                'manage.py',
                'seed_product_images',
                '--source-dir',
                product_image_source,
            ]
        )
    else:
        print(f'Skipping product image import, source not found: {product_image_source}')

    if os.path.isdir(avatar_source):
        commands.append(
            [
                sys.executable,
                'manage.py',
                'import_employee_avatars',
                '--source-dir',
                avatar_source,
                '--limit',
                '3000',
            ]
        )
    elif os.path.isdir(repo_avatar_source):
        commands.append(
            [
                sys.executable,
                'manage.py',
                'import_employee_avatars',
                '--source-dir',
                repo_avatar_source,
                '--limit',
                '3000',
            ]
        )
    else:
        print(f'Skipping avatar import, no source found: {avatar_source} or {repo_avatar_source}')

    for cmd in commands:
        print('Running:', ' '.join(cmd))
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            return result.returncode

    print('Seed completed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
