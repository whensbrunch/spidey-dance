from collections import namedtuple
import os

cfg = namedtuple('Config', [
    'iam_key',
    'pix2pixhd_root',
    'pix2pixhd_dns',
    'openpose_root',
    'detect_input',
    'detect_output',
    'extract_poses',
    'extract_original',
    'resize_poses',
    'resize_original',
    'transfer_output',
    'combine_output',
])

# Environment variables
cfg.iam_key = os.environ['IAM_KEY']
cfg.pix2pixhd_root = os.environ['PIX2PIXHD_ROOT']
cfg.pix2pixhd_dns = os.environ['PIX2PIXHD_DNS']
cfg.openpose_root = os.environ['OPENPOSE_ROOT']

# Intermediate data path variables
cfg.detect_input = 'data/detect/input'         # input to pose detector
cfg.detect_output = 'data/detect/output'       # output of pose detector
cfg.extract_poses = 'data/extract/poses'       # frames extracted from pose vid
cfg.extract_original = 'data/extract/original' # frames extracted from original
cfg.resize_poses = 'data/resize/poses'         # resized pose images
cfg.resize_original = 'data/resize/original'   # resized original images
cfg.transfer_output = 'data/transfer'          # synthesized images
cfg.combine_output = 'data/combine'            # combined images
