import click
import cv2
import os
import subprocess


@click.group()
def cli():
    pass

@cli.command()
@click.option('--video', default='./data/detect/input/example.mp4',
              help='Path to video.')
def detect(video):
    """Detect poses in video."""
    click.echo('(1/7) Converting video to AVI...')
    base_name = video.split(os.sep)[-1].split('.')[0] + '.{}'
    subprocess.run([
        'ffmpeg',
        '-i', video,
        os.path.join('data', 'detect', 'input', base_name.format('avi'))
    ])
    click.echo('==> Done.')

    click.echo('(2/7) Running pose detection using OpenPose...')
    subprocess.run([
        '/Users/davidfstevens/insight/openpose/build/examples/openpose/openpose.bin',
        '--video', os.path.join('.', 'data', 'detect', 'input', base_name.format('avi')),
        '--write_video', os.path.join('.', 'data', 'detect', 'output', base_name.format('avi')),
        '--disable_blending',
        '--display', '0',
        '--model_folder', '/Users/davidfstevens/insight/openpose/models'
    ])
    click.echo('==> Done.')

    click.echo('(3/7) Converting video back to MP4...')
    subprocess.run([
        'ffmpeg',
        '-i', os.path.join('.', 'data', 'detect', 'output', base_name.format('avi')),
        os.path.join('.', 'data', 'detect', 'output', base_name.format('mp4'))
    ])
    click.echo('==> Done.')


@cli.command()
@click.option('--count', default=-1, help='Number of frames to extract.')
def extract(count):
    """Extract frames from video."""
    cap = cv2.VideoCapture('data/detect/output/example.mp4')
    num_frames = count if count > 0 else int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    click.echo(f'(4/7) Extracting {num_frames} frames from video...')

    processed = 0
    while (True):
        if processed >= num_frames:
            break

        # Capture frame-by-frame
        ret, frame = cap.read()

        # Save resulting frame
        cv2.imwrite(f'data/extract/{str(processed).zfill(10)}.jpg', frame)
        processed += 1

    click.echo('==> Done.')

@cli.command()
def resize():
    """Resize images for input to model."""
    click.echo('(5/7) Resizing images...')
    for filename in os.listdir('data/extract'):
        img = cv2.imread(os.path.join('data/extract', filename))
        if img is not None:
            img = cv2.resize(img, (1024, 512))
            cv2.imwrite(os.path.join('data/resize', filename), img)
    click.echo('==> Done.')

@cli.command()
def transfer():
    """Transfer motion to Spiderman."""
    click.echo('Copying images to pix2pixHD server...')
    subprocess.run([
        'scp',
        '-i', 'david-IAM-keypair.pem',
        '-r',
        'data/resize/*',
        'ubuntu@ec2-54-173-213-151.compute-1.amazonaws.com:~/workspace/pix2pixHD/datasets/spidey/test_A'
    ])
    click.echo('==> Done.')

    click.echo('(6/7) Rendering Spiderman...')
    # TODO: change 300, remove reference to keypair, remove reference to IP
    subprocess.run([
        'ssh',
        '-i', '"david-IAM-keypair.pem"',
        'ubuntu@ec2-54-173-213-151.compute-1.amazonaws.com',
        '"cd ~/workspace/pix2pixHD && python test.py --name spidey --no_instance --dataroot ./datasets/spidey --label_nc 0 --no_flip --how_many 300"'
    ])
    click.echo('==> Done.')

    click.echo('Moving images back...')
    subprocess.run([
        'scp',
        '-i', '"david-IAM-keypair.pem"',
        '-r',
        'ubuntu@ec2-54-173-213-151.compute-1.amazonaws.com:~/workspace/pix2pixHD/results/spidey/test_latest/images/*synth*',
        'data/transfer'
    ])
    click.echo('==> Done.')


@cli.command()
def gif():
    """Make gif from folder of images."""
    click.echo('(7/7) Creating gif...')
    # TODO: change reference to example
    subprocess.run([
        'convert', '-delay', '3', 'data/transfer/*.jpg', 'example.gif'
    ])
    click.echo('==> Done.')

@cli.command()
def run():
    """Generate motion transfer video."""

    detect()
    extract()
    resize

    click.echo(f'Finished in {end - start:.1f} seconds.')

if __name__ == '__main__':
    cli()