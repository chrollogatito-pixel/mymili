from pathlib import Path
import shutil
import os
import sys

from django.core.management.base import BaseCommand
from django.core import management
from django.test import RequestFactory


class Command(BaseCommand):
    help = 'Renderiza vistas y recopila archivos estáticos en `dist/` para Netlify.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o', default='dist', help='Directorio de salida (por defecto: dist)'
        )

    def handle(self, *args, **options):
        # base paths
        base_dir = Path(os.getcwd())
        output = base_dir / options['output']

        # ensure output dir
        if output.exists():
            self.stdout.write(f'Removing existing output directory: {output}')
            shutil.rmtree(output)
        output.mkdir(parents=True, exist_ok=True)

        # Auto-detect URL patterns from the project's URLConf
        try:
            from django.urls import get_resolver, URLPattern, URLResolver
        except Exception as exc:
            raise RuntimeError('No se pudo importar django.urls. ¿Está Django instalado?') from exc

        resolver = get_resolver()

        def iter_patterns(patterns, prefix=''):
            for p in patterns:
                if isinstance(p, URLPattern):
                    route = prefix + str(p.pattern)
                    # skip dynamic patterns containing converters or regex groups
                    if '<' in route or '(' in route:
                        continue
                    callback = p.callback
                    yield ('/' + route.lstrip('/'), callback)
                elif isinstance(p, URLResolver):
                    new_prefix = prefix + str(p.pattern)
                    yield from iter_patterns(p.url_patterns, new_prefix)

        routes = []
        try:
            for path, view in iter_patterns(resolver.url_patterns):
                # Filter out admin and static routes
                if path.startswith('/admin') or path.startswith('/static'):
                    continue
                routes.append((path, view))
        except Exception:
            # Fallback: if anything goes wrong, try the simple amor.views import
            try:
                from amor import views as amor_views

                routes = [
                    ('/', amor_views.home),
                    ('/playlists/', amor_views.playlists),
                    ('/diary/', amor_views.diary),
                    ('/proposal/', amor_views.proposal),
                ]
            except Exception as exc:
                raise RuntimeError('No se pudo detectar rutas automáticamente y tampoco importar amor.views') from exc

        rf = RequestFactory()

        # Render each route and write to output
        for path, view in routes:
            try:
                req = rf.get(path)
                resp = view(req)
                if hasattr(resp, 'render'):
                    resp = resp.render()

                content = resp.content

                # Determine output file path
                if path == '/' or path == '':
                    out_file = output / 'index.html'
                else:
                    sub = path.strip('/')
                    out_dir = output / sub
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_file = out_dir / 'index.html'

                out_file.write_bytes(content)
                self.stdout.write(f'Wrote {out_file}')
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Skipping {path}: {exc}'))

        # Run collectstatic to gather static files into STATIC_ROOT
        self.stdout.write('Running collectstatic...')
        management.call_command('collectstatic', verbosity=0, interactive=False)

        # Copy STATIC_ROOT contents into output/static
        from django.conf import settings

        static_root = Path(settings.STATIC_ROOT)
        target_static = output / 'static'
        if static_root.exists():
            shutil.copytree(static_root, target_static)
            self.stdout.write(f'Copied static files to {target_static}')
        else:
            self.stdout.write(self.style.WARNING(f'STATIC_ROOT does not exist: {static_root}'))

        # Write a basic Netlify _redirects for SPA-like routing (optional)
        redirects = output / '_redirects'
        redirects.write_text('/*    /index.html   200\n')
        self.stdout.write(f'Wrote {redirects}')

        self.stdout.write(self.style.SUCCESS(f'Static export finished in {output}'))
