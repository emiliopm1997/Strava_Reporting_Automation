# Dockerfile generated from its corresponding template and keys
# Base image for the container
FROM continuumio/miniconda3

WORKDIR /src


# Setup basic conda environment
ENV CONDA_ENVIRONMENT py_env
COPY environment.yml .
RUN conda env create --file environment.yml && \
    echo "source activate ${CONDA_ENVIRONMENT}"  > ~/.bashrc && \
    conda clean --all -y
ENV PATH /opt/conda/envs/${CONDA_ENVIRONMENT}/bin:$PATH

# For Makefiles
RUN apt-get update && apt-get install -y make

# Install main package
RUN rm -rf /src/*

# Copy all contents
WORKDIR /home
COPY . /home
# RUN mkdir -p inputs logs outputs
CMD [ "bash"]

###############################