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
export OPENPOSE_ROOT
export IAM_KEY
export PIX2PIXHD_DNS
export PIX2PIXHD_ROOT
```

