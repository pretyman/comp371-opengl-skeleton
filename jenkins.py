#!/usr/bin/env python3

# Copyright (c) 2014, Ruslan Baratov
# All rights reserved.

# https://github.com/ruslo/polly/wiki/Jenkins

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

def clear_except_download(hunter_root):
  base_dir = os.path.join(hunter_root, '_Base')
  if os.path.exists(base_dir):
    print('Clearing directory: {}'.format(base_dir))
    hunter_download_dir = os.path.join(base_dir, 'Download', 'Hunter')
    if os.path.exists(hunter_download_dir):
      shutil.rmtree(hunter_download_dir)
    for filename in os.listdir(base_dir):
      if filename != 'Download':
        to_remove = os.path.join(base_dir, filename)
        if os.name == 'nt':
          # Fix "path too long" error
          subprocess.check_call(['cmd', '/c', 'rmdir', to_remove, '/S', '/Q'])
        else:
          shutil.rmtree(to_remove)

def run():
  parser = argparse.ArgumentParser("Testing script")
  parser.add_argument(
      '--nocreate',
      action='store_true',
      help='Do not create Hunter archive (reusing old)'
  )
  parser.add_argument(
      '--all-release',
      action='store_true',
      help='Release build type for all 3rd party packages'
  )
  parser.add_argument(
      '--clear',
      action='store_true',
      help='Remove old testing directories'
  )
  parser.add_argument(
      '--clear-except-download',
      action='store_true',
      help='Remove old testing directories except `Download` directory'
  )
  parser.add_argument(
      '--verbose',
      action='store_true',
      help='Verbose output'
  )
  parser.add_argument(
      '--disable-builds',
      action='store_true',
      help='Disable building of package (useful for checking package can be loaded from cache)'
  )
  parser.add_argument(
      '--upload',
      action='store_true',
      help='Upload cache to server and run checks (clean up will be triggered, same as --clear-except-download)'
  )

  parsed_args = parser.parse_args()

  if parsed_args.upload:
    password = os.getenv('GITHUB_USER_PASSWORD')
    if password is None:
      sys.exit('Expected environment variable GITHUB_USER_PASSWORD on uploading')

  cdir = os.getcwd()
  hunter_root = cdir

  toolchain = os.getenv('TOOLCHAIN')
  if not toolchain:
    sys.exit('Environment variable TOOLCHAIN is empty')

  project_dir = os.getenv('PROJECT_DIR')
  if not project_dir:
    sys.exit('Expected environment variable PROJECT_DIR')

  # Check broken builds --
  if (project_dir == 'examples/Boost-filesystem') and (toolchain == 'analyze'):
    print('Skip (https://github.com/ruslo/hunter/issues/25)')
    sys.exit(0)

  if (project_dir == 'examples/Boost-system') and (toolchain == 'analyze'):
    print('Skip (https://github.com/ruslo/hunter/issues/26)')
    sys.exit(0)

  if (project_dir == 'examples/OpenSSL') and (toolchain == 'mingw'):
    print('Skip (https://github.com/ruslo/hunter/issues/28)')
    sys.exit(0)

  if (project_dir == 'examples/OpenSSL') and (toolchain == 'ios-7-0'):
    print('Skip (https://github.com/ruslo/hunter/issues/29)')
    sys.exit(0)

  if (project_dir == 'examples/OpenSSL') and (toolchain == 'xcode'):
    print('Skip (https://github.com/ruslo/hunter/issues/30)')
    sys.exit(0)

  ci = os.getenv('TRAVIS') or os.getenv('APPVEYOR')
  if (ci and toolchain == 'dummy'):
    print('Skip build: CI dummy (workaround)')
    sys.exit(0)
  # -- end

  verbose = True
  if (
      os.getenv('TRAVIS') and
      (project_dir == 'examples/CLAPACK') and
      (toolchain == 'xcode')
  ):
    verbose = False

  if (
      os.getenv('TRAVIS') and
      (project_dir == 'examples/GSL') and
      (toolchain == 'xcode')
  ):
    verbose = False

  project_dir = os.path.join(cdir, project_dir)
  project_dir = os.path.normpath(project_dir)

  testing_dir = os.path.join(os.getcwd(), '_testing')
  if os.path.exists(testing_dir) and parsed_args.clear:
    print('REMOVING: {}'.format(testing_dir))
    shutil.rmtree(testing_dir)
  os.makedirs(testing_dir, exist_ok=True)

  if os.name == 'nt':
    hunter_junctions = os.getenv('HUNTER_JUNCTIONS')
    if hunter_junctions:
      temp_dir = tempfile.mkdtemp(dir=hunter_junctions)
      shutil.rmtree(temp_dir)
      subprocess.check_output(
          "cmd /c mklink /J {} {}".format(temp_dir, testing_dir)
      )
      testing_dir = temp_dir

  if os.name == 'nt':
    which = 'where'
  else:
    which = 'which'

  polly_root = os.getenv('POLLY_ROOT')
  if polly_root:
    print('Using POLLY_ROOT: {}'.format(polly_root))
    build_script = os.path.join(polly_root, 'bin', 'build.py')
  else:
    build_script = subprocess.check_output(
        [which, 'build.py'], universal_newlines=True
    ).split('\n')[0]

  if not os.path.exists(build_script):
    sys.exit('Script not found: {}'.format(build_script))

  print('Testing in: {}'.format(testing_dir))
  os.chdir(testing_dir)

  args = [
      sys.executable,
      build_script,
      '--clear',
      '--config',
      'Release',
      '--toolchain',
      toolchain,
      '--home',
      project_dir
  ]

  args += ['--verbose']
  if not verbose:
    args += ['--discard', '10']
    args += ['--tail', '200']

  print('Execute command: [')
  for i in args:
    print('  `{}`'.format(i))
  print(']')

  subprocess.check_call(args)

  if parsed_args.upload:
    upload_script = os.path.join(cdir, 'maintenance', 'upload-cache-to-github.py')

    print('Uploading cache')
    subprocess.check_call([
        sys.executable,
        upload_script,
        '--username',
        'ingenue',
        '--repo-owner',
        'ingenue',
        '--repo',
        'hunter-cache',
        '--cache-dir',
        os.path.join(hunter_root, '_Base', 'Cache'),
        '--temp-dir',
        os.path.join(hunter_root, '__TEMP')
    ])

    seconds = 60
    print(
        'Wait for GitHub changes became visible ({} seconds)...'.format(seconds)
    )
    time.sleep(seconds)

    print('Run sanity build')

    clear_except_download(hunter_root)

    # Sanity check - run build again with disabled building from sources
    args = [
        sys.executable,
        build_script,
        '--clear',
        '--verbose',
        '--config',
        'Release',
        '--toolchain',
        toolchain,
        '--home',
        project_dir,
        '--fwd',
        'HUNTER_DISABLE_BUILDS=ON',
        'HUNTER_ROOT={}'.format(hunter_root),
        'TESTING_URL={}'.format(hunter_url),
        'TESTING_SHA1={}'.format(hunter_sha1)
    ]

    print('Execute command: [')
    for i in args:
      print('  `{}`'.format(i))
    print(']')

    subprocess.check_call(args)

if __name__ == "__main__":
  run()