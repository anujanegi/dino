#!/bin/bash

# DiNo cli installer

# Base Variables
SUDO="sudo"
MPI_USER="mpiuser"
MPI_PASS="password"

LOG=$(mktemp)
log_def='[.]'
log_ok="\e[32m[ok]\e[0m"
log_error="\e[31m[error]\e[0m"

# requirements
packages="openssh-server nfs-kernel-server nfs-common"
python_packages="mpi4py flask requests click"

# Welcome screen
print_head(){
  cat<<EO
   ┌─────────────────────────────────────────────────────┐
   │                      DiNo                           │
   │                 DIstributed NOdes                   │
   │              << MPI for everyone >>                 │
   └─────────────────────────────────────────────────────┘
EO
}

# Check permissions and distro
check_viability(){
  if [ "$EUID" -ne 0 ]
    then echo "This script requires $SUDO. Please run as root or use $SUDO."
    exit
  fi

  [[ ! -e /etc/debian_version ]] && {
    echo  "dinocli is only available for debian based distros for now"
    exit 1
  }
}


# Log generation and handling
run_and_log(){
  $1 &> ${LOG} && {
    _log_def=$log_ok
  } || {
    _log_def=$log_error
    exit_=1
  }
  echo -e "${_log_def} ${2}"
  [[ $exit_ ]] && { echo -e "\t -> ${_log_def} $3";  exit; }
}

# Installs mpich2
install_mpich2(){
  wget -P pwd http://www.mpich.org/static/downloads/3.2.1/mpich-3.2.1.tar.gz
  tar -xzf mpich2-1.4.tar.gz
  cd mpich2-1.4
  ./configure --disable-fortran
  make; $SUDO make install
}

# Checks if mpich2 is installed
check_mpich2(){
  if !(which mpiexec); then
    install_mpich2
  fi
}

# Checks if mpi user exists and creates one if not
create_user(){
  id -u $MPI_USER > /dev/null 2>&1
  if [[ $? -eq 0 ]] ; then
    echo "$MPI_USER already exists..."
  else
    $SUDO adduser --disabled-login -gecos "" ${MPI_USER}
    echo -e "${MPI_PASS}\n${MPI_PASS}" | $SUDO passwd ${MPI_USER}
    return 0
  fi
}

# Logs in MPI_USER
login_user(){
  su - $MPI_USER
  return 0
}

# Setup shared directory
setup_cloud(){
  mkdir /home/$MPI_USER/cloud
  cat '/home/mpiuser/cloud *(rw,sync,no_root_squash,no_subtree_check    )' >> /etc/exports
  exportfs -a
  $SUDO service nfs-kernel-server restart
}


# Creates ssh keys
create_keys(){
  ssh-keygen -b 2048 -t rsa -N "" -q -f /home/$MPI_USER/.ssh/id_rsa
  eval `ssh-agent`
  ssh-add /home/$MPI_USER/.ssh/id_rsa
}


# Copies DiNo files
copy_files(){
  $SUDO mkdir /home/mpiuser/dino
  $SUDO mkdir /home/mpiuser/dino
  $SUDO cp -r * /home/mpiuser/dino
}

# Creates symbolic link
create_symbolic_link(){
  $SUDO mkdir /home/mpiuser/dino
  $SUDO mkdir /home/mpiuser/dino
  $SUDO cp -r * /home/mpiuser/dino
}

# Instals packages and python dependencies
install_packages(){
  $SUDO apt-get install -y ${packages}
  $SUDO pip3 install ${python_packages}
  return 0
}

echo "Logging enabled on ${LOG}"


print_head
# Check permissions and distro
check_viability
# Check if mpich2 installed
check_mpich2
# Check and create MPI user if does not exist
create_user
# Login user
# login_user
# Copy DiNo files
copy_files
# Create symbolic links
# create_symbolic_link
# Install packages
run_and_log install_packages "Installing packages $packages" "Something went wrong, please look at the log file"
# Create ssh keys
create_keys
# Setting up NFS
setup_cloud
