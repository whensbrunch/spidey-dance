import subprocess


subprocess.run('ssh -i ~/.ssh/david-IAM-keypair.pem ubuntu@ec2-54-173-213-151.compute-1.amazonaws.com "cd ~/workspace/pix2pixHD;./scripts/test_spidey.sh"', shell=True)
subprocess.run([
    'ssh',
    '-i', '~/.ssh/david-IAM-keypair.pem',
    'ubuntu@ec2-54-173-213-151.compute-1.amazonaws.com',
    '"cd ~/workspace/pix2pixHD;./scripts/test_spidey.sh"'
])
