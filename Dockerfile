# This is a PRP->Braingeneers image which should later be extended to
# PRP->Braingeneers->WetAI

FROM gitlab-registry.nrp-nautilus.io/prp/jupyter-stack/prp

RUN sudo apt-get update && sudo apt-get install -y \
    glances \
    wget \
    curl \
    ncdu \
    ffmpeg \
    rclone \
    awscli \
    hdf5-tools \
    time

# The ADD command below downloads the latest commit information. If it has changed since the last build
# the following layers will not be cached, if it hasn't changed the following layers will rebuild.
ADD "https://api.github.com/repos/braingeneers/braingeneerspy/commits?per_page=1" /tmp/latest_braingeneers_commit
RUN python -m pip install --force-reinstall --no-cache-dir git+https://github.com/braingeneers/braingeneerspy.git#egg=braingeneerspy[analysis]

# Additional (optional) python packages
RUN python -m pip install --no-cache-dir \
    pyyaml \
    dash \
    nptyping

ENV ENDPOINT=https://s3-west.nrp-nautilus.io

ENTRYPOINT []
COPY ./stim_builder_plotly.py /home/jovyan/stim_builder_plotly.py
COPY ./stim_builder.py /home/jovyan/stim_builder.py
COPY ./assets /home/jovyan/assets
COPY ./aws_helper.py /home/jovyan/aws_helper.py

USER root
CMD ["python", "/home/jovyan/stim_builder_plotly.py"]
#CMD ["python", "/home/jovyan/stim_builder_plotly.py"]