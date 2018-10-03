"""Command line interface for Don't Make Me Dance."""

import click
import cv2
import numpy as np
import os
import shutil
import subprocess
import time

from config import cfg
 

# utility functions
def safe_mkdir(path):
    """Make all directories in a path as necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
    return None


def get_base_name(path):
    """Extract the filename with generic extension."""
    return path.split(os.sep)[-1].split('.')[0] + '.{}'


# command line tool
@click.group()
def cli():
    pass


@cli.command()
def detect(video):
    """Detect poses in video."""
    click.echo('Converting video to AVI...')
    safe_mkdir(cfg.detect_input)
    base_name = get_base_name(video) 
    subprocess.run([
        'ffmpeg',
        '-i', video,
        os.path.join(cfg.detect_input, base_name.format('avi'))
    ])
    click.echo('==> Done.')

    click.echo('Running pose detection using OpenPose...')
    safe_mkdir(cfg.detect_output)
    openpose_binary = os.path.join(
        cfg.openpose_root, 'build', 'examples', 'openpose', 'openpose.bin')
    input = os.path.join(cfg.detect_input, base_name.format('avi'))
    output = os.path.join(cfg.detect_output, base_name.format('avi'))
    model_folder = os.path.join(cfg.openpose_root, 'models')

    subprocess.run([
        openpose_binary,
        '--video', input,
        '--write_video', output,
        '--disable_blending',
        '--display', '0',
        '--model_folder', model_folder
    ])
    click.echo('==> Done.')

    # TODO: capture return code
    click.echo('Converting video back to MP4...')
    subprocess.run([
        'ffmpeg',
        '-i', os.path.join(cfg.detect_output, base_name.format('avi')),
        os.path.join(cfg.detect_output, base_name.format('mp4'))
    ])
    click.echo('==> Done.')

    return None


@cli.command()
@click.option('--count', default=-1, help='Number of frames to extract.')
def extract(video, count):
    """Extract frames from original video and pose detected video."""
    safe_mkdir(cfg.extract_poses)
    safe_mkdir(cfg.extract_original)

    # Extract frames from pose video
    base_name = get_base_name(video)
    pose_video = os.path.join(cfg.detect_output, base_name.format('mp4'))
    cap = cv2.VideoCapture(pose_video)
    num_frames = count if count > 0 else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    click.echo(f'Extracting {num_frames} frames from pose video...')
    processed = 0
    while (True):
        if processed >= num_frames:
            break

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Save resulting frame
        save_path = os.path.join(cfg.extract_poses,
                            str(processed).zfill(10) + '.jpg')
        cv2.imwrite(save_path, frame)
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
        save_path = os.path.join(cfg.extract_original,
                            str(processed).zfill(10) + '.jpg')
        cv2.imwrite(save_path, frame)
        processed += 1
    click.echo('==> Done.')

    return None


@cli.command()
def resize():
    """Resize images for input to model."""
    safe_mkdir(cfg.resize_poses)
    safe_mkdir(cfg.resize_original)

    def resize_all(input_path, output_path):
        for filename in os.listdir(input_path):
            img = cv2.imread(os.path.join(input_path, filename))
            if img is not None:
                img = cv2.resize(img, (1024, 512))
                cv2.imwrite(os.path.join(output_path, filename), img)

        return None

    click.echo('Resizing images...')
    resize_all(cfg.extract_original, cfg.resize_original)
    resize_all(cfg.extract_poses, cfg.resize_poses)
    click.echo('==> Done.')

    return None


@cli.command()
def transfer():
    """Transfer motion to Spiderman."""
    click.echo('Copying images to pix2pixHD server...')
    subprocess.run([
        'scp',
        '-i', cfg.iam_key,
        '-r',
        'data/resize/poses/.',
        cfg.pix2pixhd_dns + ':' + os.path.join(cfg.pix2pixhd_root,
                                               'datasets', 'spidey', 'test_A')
    ])
    click.echo('==> Done.')

    click.echo('Rendering Spiderman...')
    subprocess.run(
        f'ssh -i {cfg.iam_key} {cfg.pix2pixhd_dns} "cd {cfg.pix2pixhd_root};'
        f'./scripts/test_spidey.sh"',
        shell=True)
    click.echo('==> Done.')

    click.echo('Moving images back...')
    safe_mkdir(cfg.transfer_output)
    synthesized_imgs = os.path.join(cfg.pix2pixhd_root, 'results', 'spidey',
                                    'test_latest', 'images', '*synth*')
    subprocess.run([
        'scp',
        '-i', cfg.iam_key,
        '-r',
        cfg.pix2pixhd_dns + ':' + synthesized_imgs,
        cfg.transfer_output
    ])
    click.echo('==> Done.')

    return None


@cli.command()
def rename():
    """Rename synthesized images produced by pix2pixHD."""
    click.echo(f'Renaming images in {cfg.transfer_output}...')
    for filename in os.listdir(cfg.transfer_output):
        if filename.endswith('jpg'):
            os.rename(
                os.path.join(cfg.transfer_output, filename),
                os.path.join(cfg.transfer_output, filename[:10] + '.jpg')
            )
    click.echo('Done.')

    return None


@cli.command()
def combine():
    """Combine original and synthesized images."""
    click.echo(f'Combining images in {cfg.resize_original} with images in '
               f'{cfg.transfer_output}...')
    safe_mkdir(cfg.combine_output)
    for filename in os.listdir(cfg.resize_original):
        # load image
        img = cv2.imread(os.path.join(cfg.resize_original, filename))

        # find sibling
        sibling_path = os.path.join(cfg.transfer_output, filename)
        if os.path.exists(sibling_path):
            sibling = cv2.imread(sibling_path)

            # combine
            combined = np.concatenate([img, sibling], axis=1)

            # save
            combined_path = os.path.join(cfg.combine_output, filename)
            cv2.imwrite(combined_path, combined)

    return None

@cli.command()
def gif(name):
    """Make gif from folder of images."""
    click.echo('Creating gif...')
    subprocess.run([
        'convert', '-delay', '3', cfg.combine_output + '/*.jpg',
        name.format('gif')
    ])
    click.echo('==> Done.')
    return None


@cli.command()
def cleanup():
    """Remove intermediate data files."""
    # Local files
    data_dirs = [
        cfg.detect_input,
        cfg.detect_output,
        cfg.extract_poses,
        cfg.extract_original,
        cfg.resize_poses,
        cfg.resize_original,
        cfg.transfer_output,
        cfg.combine_output
    ]
    for dir in data_dirs:
        shutil.rmtree(dir)

    # Files on pix2pixHD node
    subprocess.run(
        f'ssh -i {cfg.iam_key} {cfg.pix2pixhd_dns} "cd {cfg.pix2pixhd_root};'
        f'rm -r results/spidey"',
        shell=True)

    return None


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

    return None


if __name__ == '__main__':
    cli()
