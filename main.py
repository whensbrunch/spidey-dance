"""Command line interface for Don't Make Me Dance."""

import click
import cv2
import numpy as np
import os
import shutil
import subprocess
import time


iam_key = os.environ['IAM_KEY']
pix2pixhd_root = os.environ['PIX2PIXHD_ROOT']
pix2pixhd_dns = os.environ['PIX2PIXHD_DNS']
 

# utility functions
def safe_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return None


def get_base_name(path):
    return path.split(os.sep)[-1].split('.')[0] + '.{}'


@click.group()
def cli():
    pass


@cli.command()
def detect(video):
    """Detect poses in video."""
    click.echo('Converting video to AVI...')
    safe_mkdir('data/detect/input')
    base_name = get_base_name(video) 
    subprocess.run([
        'ffmpeg',
        '-i', video,
        os.path.join('data', 'detect', 'input', base_name.format('avi'))
    ])
    click.echo('==> Done.')

    click.echo('Running pose detection using OpenPose...')
    safe_mkdir('data/detect/output')
    openpose_root = os.environ['OPENPOSE_ROOT']
    subprocess.run([
        os.path.join(openpose_root, 'build', 'examples', 'openpose', 'openpose.bin'),
        '--video', os.path.join('.', 'data', 'detect', 'input', base_name.format('avi')),
        '--write_video', os.path.join('.', 'data', 'detect', 'output', base_name.format('avi')),
        '--disable_blending',
        '--display', '0',
        '--model_folder', os.path.join(openpose_root, 'models')
    ])
    click.echo('==> Done.')

    click.echo('Converting video back to MP4...')
    subprocess.run([
        'ffmpeg',
        '-i', os.path.join('.', 'data', 'detect', 'output', base_name.format('avi')),
        os.path.join('.', 'data', 'detect', 'output', base_name.format('mp4'))
    ])
    click.echo('==> Done.')


@cli.command()
@click.option('--count', default=-1, help='Number of frames to extract.')
def extract(video, count):
    """Extract frames from video."""
    safe_mkdir('data/extract/poses')
    safe_mkdir('data/extract/original')

    # Extract frames from pose video
    base_name = get_base_name(video) 
    cap = cv2.VideoCapture(os.path.join('data', 'detect', 'output', base_name.format('mp4')))
    num_frames = count if count > 0 else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    click.echo(f'Extracting {num_frames} frames from pose video...')

    processed = 0
    while (True):
        if processed >= num_frames:
            break

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Save resulting frame
        cv2.imwrite(f'data/extract/poses/{str(processed).zfill(10)}.jpg', frame)
        processed += 1

    click.echo('==> Done.')

    # Extract frames from original video
    cap = cv2.VideoCapture(video)
    num_frames = count if count > 0 else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    click.echo(f'Extracting {num_frames} frames from original video...')

    processed = 0
    while (True):
        if processed >= num_frames:
            break

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Save resulting frame
        cv2.imwrite(f'data/extract/original/{str(processed).zfill(10)}.jpg', frame)
        processed += 1

    click.echo('==> Done.')


@cli.command()
def resize():
    """Resize images for input to model."""
    safe_mkdir('data/resize/poses')
    safe_mkdir('data/resize/original')

    click.echo('Resizing images...')
    # Resize originals
    for filename in os.listdir('data/extract/original'):
        img = cv2.imread(os.path.join('data/extract/original', filename))
        if img is not None:
            img = cv2.resize(img, (1024, 512))
            cv2.imwrite(os.path.join('data/resize/original', filename), img)

    # Resize pose images
    for filename in os.listdir('data/extract/poses'):
        img = cv2.imread(os.path.join('data/extract/poses', filename))
        if img is not None:
            img = cv2.resize(img, (1024, 512))
            cv2.imwrite(os.path.join('data/resize/poses', filename), img)

    click.echo('==> Done.')


@cli.command()
def transfer():
    """Transfer motion to Spiderman."""
    click.echo('Copying images to pix2pixHD server...')
    iam_key = os.environ['IAM_KEY']
    pix2pixhd_root = os.environ['PIX2PIXHD_ROOT']
    pix2pixhd_dns = os.environ['PIX2PIXHD_DNS']
    subprocess.run([
        'scp',
        '-i', iam_key,
        '-r',
        'data/resize/poses/.',
        pix2pixhd_dns + ':' + os.path.join(pix2pixhd_root, 'datasets', 'spidey', 'test_A')
    ])
    click.echo('==> Done.')

    click.echo('Rendering Spiderman...')
    subprocess.run(f'ssh -i {iam_key} {pix2pixhd_dns} "cd {pix2pixhd_root};./scripts/test_spidey.sh"', shell=True)
    click.echo('==> Done.')

    click.echo('Moving images back...')
    safe_mkdir('data/transfer')
    subprocess.run([
        'scp',
        '-i', iam_key,
        '-r',
        pix2pixhd_dns + ':' + os.path.join(pix2pixhd_root, 'results', 'spidey', 'test_latest', 'images', '*synth*'),
        'data/transfer'
    ])
    click.echo('==> Done.')


@cli.command()
def rename():
    """Rename synthesized images produced by pix2pixHD."""
    click.echo('Renaming images in ./data/transfer...')
    for filename in os.listdir('./data/transfer'):
        if filename.endswith('jpg'):
            os.rename('./data/transfer/' + filename, './data/transfer/' + filename[:10] + '.jpg')
    click.echo('Done.') 


@cli.command()
def combine():
    """Combine original and synthesized images."""
    click.echo('Combining images in ./data/resize/original with images in ./data/transfer...')
    safe_mkdir('data/combine')
    for filename in os.listdir('./data/resize/original'):
        # load image
        img = cv2.imread(os.path.join('./data/resize/original', filename))

        # find sibling
        sibling_path = os.path.join('./data/transfer', filename)
        if os.path.exists(sibling_path):
            sibling = cv2.imread(sibling_path)

            # combine
            combined = np.concatenate([img, sibling], axis=1)

            # save
            combined_path = os.path.join('./data/combine', filename)
            cv2.imwrite(combined_path, combined)


@cli.command()
def gif(name):
    """Make gif from folder of images."""
    click.echo('Creating gif...')
    subprocess.run([
        'convert', '-delay', '3', 'data/combine/*.jpg', name.format('gif')
    ])
    click.echo('==> Done.')


@cli.command()
def cleanup():
    """Remove intermediate data files."""
    shutil.rmtree('./data')  # remove local data folder
    subprocess.run(
        f'ssh -i {iam_key} {pix2pixhd_dns} "cd {pix2pixhd_root};rm -r results/spidey"', 
        shell=True)


@cli.command()
@click.pass_context
@click.option('--video', default='./data/detect/input/example.mp4',
              help='Path to video.')
def run(ctx, video):
    """Generate motion transfer video."""
    # Run through each step
    times = {}

    start = lap = time.time()
    ctx.invoke(detect, video)
    times['detect'] = time.time() - lap

    lap = time.time()
    ctx.invoke(extract, video)
    times['extract'] = time.time() - lap

    lap = time.time()
    ctx.invoke(resize)
    times['resize'] = time.time() - lap 

    lap = time.time()
    ctx.invoke(transfer)
    times['transfer'] = time.time() - lap

    lap = time.time()
    ctx.invoke(rename)
    times['rename'] = time.time() - lap
 
    lap = time.time()
    ctx.invoke(combine)
    times['combine'] = time.time() - lap

    lap = time.time()
    name = get_base_name(video)
    ctx.invoke(gif, name)
    times['gif'] = time.time() - lap

    lap = time.time()
    ctx.invoke(cleanup)
    times['cleanup'] = time.time() - lap
 
    end = time.time()
    times['total'] = end - start

    # Time profiling
    for k, v in times.items():
        click.echo(f'==> {k} time: {v:.1f}s')


if __name__ == '__main__':
    cli()
