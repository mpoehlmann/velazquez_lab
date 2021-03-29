# Computing Environment Tutorial
To run Python, we need to properly set up your computing environment.
What follows is an opinionated guide.

## ``conda``
### Installation
First, we will use [``conda``](https://docs.conda.io/en/latest/) to manage our enviroment and installed packages.

#### Macs 🙂
Open Terminal and run the following commands:
```bash
xcode-select --install
cd ~/Downloads
wget https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh -b -p /Applications/miniconda
```

#### Linux 😐
Open Terminal and run the following commands:
```bash
cd ~
mkdir software
cd software
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/software/miniconda
```

#### Windows 😕
When using Windows, you should install a Ubuntu (Linux) subsystem.
See the [instructions here](https://ubuntu.com/tutorials/ubuntu-on-windows#1-overview).
Then, follow the Linux instructions above.

### Creating an environment
Before we create the environment, we need to active ``conda``:
```bash
source  /Applications/miniconda/etc/profile.d/conda.sh  # Mac
source  ~/software/miniconda/etc/profile.d/conda.sh  # Linux/Windows
```

Now, let's create the environment.
Navigate to the ``velazquez_lab`` project folder and run:
```bash
conda env create --file environment.yml
```

### Activating
Edit the file ``~/.bash_profile`` and add the following line which corresponds to your operating system:
```bash
# Mac
alias setup_conda='source  /Applications/miniconda/etc/profile.d/conda.sh && conda activate labenv'

# Linux/Windows
alias setup_conda='source  ~/software/miniconda/etc/profile.d/conda.sh && conda activate labenv'
```