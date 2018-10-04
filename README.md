<h1 align="center">
<p align="center"><img width=30% src="https://github.com/whensbrunch/spidey-dance/blob/master/media/Logo.png"></p>
<p align="center"><img width=60% src="https://github.com/whensbrunch/spidey-dance/blob/master/media/Dont-Make-Me-Dance.png"></p>
</h1>

<h3 align="center">Deep learning for human motion transfer.</h3>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
![Python](https://img.shields.io/badge/python-v3.6+-blue.svg)
[![GitHub Issues](https://img.shields.io/github/issues/whensbrunch/spidey-dance.svg)](https://github.com/whensbrunch/spidey-dance/issues)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Basic Overview

Using this command line tool, you can transfer movement from a source video onto an avatar of Spiderman. The pipeline is powered by deep learning models (specifically: generative adversial networks) in order to produce gifs of Spiderman in various poses. This work is based on the research paper "Everybody Dance Now".

## Requirements

This tool requires:

* 2 AWS EC2 instances (with a GPU)
* pix2pixHD
* OpenPose

## Usage

First, install spidey-dance:

```
git clone https://github.com/whensbrunch/spidey-dance.git
```

Next, set the following environment variables:

```
export OPENPOSE_ROOT=path/to/openpose
export IAM_KEY=path/to/keypair.pem 
export PIX2PIXHD_DNS=ec2_dns
export PIX2PIXHD_ROOT=path/to/pix2pixHD
```

We will need two nodes: one to run OpenPose and one to run pix2pixHD. The CLI will run from the OpenPose node and so we will need to `ssh` into the node with pix2pixHD. For this we need the User and Public DNS (ex: ubuntu@ec2-xx-xxx-xxx-xxx.compute-1.amazonaws.com).

You'll also need the `.pem` file to `ssh` into the pix2pixHD node. Set the path to this file as `IAM_KEY`.

## Getting help



## Future Directions

These are the directions I'd like to see explored in the future - if you'd like to implement any of these or have your own ideas, feel free to submit a pull request!

1. Face-specific GAN: facial realism is lacking in the current implementation. The authors of "Everybody Dance Now" use a separate GAN for the face to improve quality.

2. Image augmentation: Current training data consisted of ~30s of Spiderman video. Other researchers have had success with ~20min of natural movements. I imagine it will be difficult to procure additional Spiderman footage, so is there a way we can augment the images we have to increase the diversity of the training data?

3. Condition of the previous image: Use information from the previous frame to predict the next frame.

4. Global pose normalization: Another innovation by the author's of "Everybody Dance Now". Currently, Spiderman assumes the proportions of the source actor. We should scale the pose keypoints to return Spiderman to his original proportions.


