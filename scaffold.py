#!/usr/bin/env python

import os
import sys
import shutil
import click
import jinja2

from utils import slugify, jinjago


@click.command()
@click.argument('template-dir', default='./template', required=False)
@click.argument('output-dir', default='./output', required=False)
@click.option('--project-name', prompt='Project name',
              default='Project name',
              help='Human readable project name, used for titles and docs.')
@click.option('--project-slug', prompt='Project slug',
              default=click.pass_context(lambda ctx: slugify(ctx.params['project_name'])),
              help='Project slug, used in paths, filenames, etc.')
def scaffold(template_dir, output_dir, project_name, project_slug):
    """
    \b
    TEMPLATE_DIR         Template directory [default: ./template]
    OUTPUT_DIR           Output directory [default: ./output]
    """
    if not os.path.isabs(template_dir):
        template_dir = os.path.join(os.getcwd(), template_dir)
    template_dir = os.path.abspath(template_dir)  # trim trailing path separator

    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)
    output_dir = os.path.abspath(output_dir)  # trim trailing path separator

    context = {
        'template_dir': template_dir,
        'output_dir': output_dir,
        'project_name': project_name,
        'project_slug': project_slug,
    }

    if not os.path.exists(template_dir):
        raise click.ClickException(
            'Template directory cannot be found: {template_dir}'.format(**context)
        )

    # remove output directory - TODO: should be behind a flag
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # copy directories and files
    for root, directories, filenames in list(os.walk(template_dir)):
        for directory in directories:
            src = os.path.join(root, directory)
            dst = jinjago(os.path.join(src.replace(template_dir, output_dir, 1)), context)
            if not os.path.exists(dst):
                os.makedirs(dst)
            shutil.copystat(src, dst)

        for filename in filenames:
            src = os.path.join(root, filename)
            dst = jinjago(os.path.join(src.replace(template_dir, output_dir, 1)), context)
            shutil.copy2(src, dst)

    # run all output files through jinja
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(output_dir))
    for root, directories, filenames in list(os.walk(output_dir)):
        for filename in filenames:
            output_file = os.path.join(root, filename)
            template = env.get_template(output_file.replace(output_dir, '', 1))
            with open(output_file, 'wb') as fh:
                fh.write(template.render(context))


if __name__ == '__main__':
    scaffold()
