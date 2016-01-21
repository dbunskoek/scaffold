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
@click.option('--project-version', prompt='Project version',
              default='1.0.0')
@click.option('--project-description', prompt='Project description',
              default='')
@click.option('--force-delete', is_flag=True, default=False,
              help='Force delete the output directory')
def scaffold(template_dir, output_dir,
             project_name, project_slug,
             project_version,
             project_description,
             force_delete):
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
        'project_version': project_version,
        'project_description': project_description,
    }

    if not os.path.exists(template_dir):
        raise click.ClickException(
            'Template directory cannot be found: {template_dir}'.format(**context)
        )

    # remove output directory
    if os.path.exists(output_dir):
        if force_delete or click.confirm('The output directory will be deleted. Are you sure?', abort=True):
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
            # store if last character is newline
            with open(output_file, 'r') as fh:
                fh.seek(-1, os.SEEK_END)
                last_character_is_newline = (fh.read() == '\n')
                fh.close()
            template = env.get_template(output_file.replace(output_dir, '', 1))
            with open(output_file, 'wb') as fh:
                fh.write(template.render(context))
                # restore newline character, Jinja seems to lose it
                if last_character_is_newline:
                    fh.write('\n')
                fh.close()


if __name__ == '__main__':
    scaffold()
