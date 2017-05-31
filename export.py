#!/usr/bin/env python
import datetime
from jinja2 import Environment, FileSystemLoader
import markdown2
import os
import re
import shutil
import sys

reload(sys)
sys.setdefaultencoding('utf8')

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(THIS_DIR, 'docs')

class MoinArticle(object):

  def __init__(self, slug, content_moin, date_created, date_modified, source_path):
    self.source_path = source_path
    self.slug = slug
    self.content_moin = content_moin
    self.date_created = date_created
    self.date_modified = date_modified

  def GetOutputDir(self):
    return os.path.join(OUTPUT_ROOT, self.slug)

  def GetAttachmentsDir(self):
    return os.path.join(self.source_path, 'attachments')


def GetAllPages(root):
  pages = []
  for dirpath, dirnames, filenames in os.walk(root):
    for fname in dirnames:
      path = os.path.join(dirpath, fname)
      edit_log = os.path.join(path, 'edit-log')
      revisions = os.path.join(path, 'revisions')
      if os.path.exists(edit_log) and os.path.exists(revisions):
        pages.append(path)

  return pages


def ParseDateFromEditEntry(line):
  split = line.split('\t')
  time_string = split[0]
  unixtime = int(time_string) / 1e6
  return datetime.datetime.fromtimestamp(unixtime)


def GetDates(page_path):
  edit_log = os.path.join(page_path, 'edit-log')
  with open(edit_log) as f:
    lines = f.readlines()
    if not len(lines):
      # If there are no lines, there's no creation or modification date.
      return [None, None]
    created = lines[0]
    modified = lines[-1]
    return [ParseDateFromEditEntry(created), ParseDateFromEditEntry(modified)]


def GetMoinContent(page_path, use_current_file=False):
  # Parse the current file to get the right revision file.
  current = os.path.join(page_path, 'current')
  revisions_path = os.path.join(page_path, 'revisions')
  if use_current_file:
    # Get the revision number from the current file.
    with open(current) as f:
      revision = f.read()
  else:
    # Get the revision number from the last existing revision.
    revisions = os.listdir(revisions_path)
    revision = revisions[-1]

  content_path = os.path.join(revisions_path, revision)
  with open(content_path) as f:
    return ''.join(f.readlines())


def RenderArticle(moin_article):
  markdown_body = MoinToMarkdown(moin_article.content_moin)
  # Render the markdown into HTML.
  content = markdown2.markdown(markdown_body)
  # Populate the template with everything.
  env = Environment(loader=FileSystemLoader(THIS_DIR))
  template = env.get_template('page.html')
  template_vars = moin_article.__dict__
  template_vars['content'] = content
  template_vars['date_now'] = datetime.datetime.now()
  html = template.render(template_vars)
  return html


def SaveArticle(moin_article, html):
  out_dir = moin_article.GetOutputDir()
  # Make sure the directory exists.
  if not os.path.exists(out_dir):
    os.makedirs(out_dir)

  # Copy all of the attachments into that directory.
  attachments_dir = moin_article.GetAttachmentsDir()
  if os.path.exists(attachments_dir):
    CopyAttachments(attachments_dir, out_dir)

  # Write the HTML into its own directory.
  with open(os.path.join(out_dir, 'index.html'), 'w') as f:
    f.write(html.encode('utf-8'))


def SaveArticleIndex(articles):
  env = Environment(loader=FileSystemLoader(THIS_DIR))
  template = env.get_template('list.html')
  template_vars = {}
  template_vars['articles'] = articles
  template_vars['date_now'] = datetime.datetime.now()
  html = template.render(template_vars)

  index_dir = os.path.join(OUTPUT_ROOT, 'index.html')
  with open(index_dir, 'w') as f:
    f.write(html.encode('utf-8'))


def MoinToMarkdown(moin_markup):
  out = moin_markup

  # Replace URLs and attachments with markdown links.
  link = re.compile(r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)')
  out = link.sub(r'<a href="\1">\1</a>', out)

  # Replace 'attachment:foo.jpg' with actual imagery.
  attachment = re.compile(r'attachment:([\w.]*)')
  out = attachment.sub(r'<img src="\1"/>', out)

  # Replace {{{ and }}} with <pre> and </pre>.
  out = out.replace('{{{', '<pre>')
  out = out.replace('}}}', '</pre>')

  # Replace "== foo ==" with "## foo".

  return out


def CopyAttachments(from_path, to_path):
  if os.path.exists(to_path):
    shutil.rmtree(to_path)
  shutil.copytree(from_path, to_path)


def DeletePath(path):
  """Remove file or directory at path."""
  if os.path.isfile(path):
    os.unlink(path)
  else:
    shutil.rmtree(path)



if __name__ == '__main__':
  # Clean up the output directory.
  DeletePath(OUTPUT_ROOT)

  root = 'wiki.z3.ca/wiki/data/pages/'
  page_paths = GetAllPages(root)
  articles = []
  for page_path in page_paths:
    content = GetMoinContent(page_path)
    created, modified = GetDates(page_path)
    slug = os.path.basename(page_path)
    article = MoinArticle(content_moin=content, date_created=created,
        date_modified=modified, slug=slug, source_path=page_path)
    articles.append(article)

    content_html = RenderArticle(article)
    SaveArticle(article, content_html)

  SaveArticleIndex(articles)


