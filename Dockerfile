# Using Python Slim-Buster
FROM biansepang/weebproject:buster

# Clone repo and prepare working directory
RUN git clone -b staging https://github.com/BianSepang/WeebProject /home/weebproject/ \
    && chmod 777 /home/weebproject \
    && mkdir /home/weebproject/bin/

# Copies config.env (if exists)
COPY ./sample_config.env ./config.env* /home/weebproject/

# Setup Working Directory
WORKDIR /home/weebproject/

# Finalization
CMD ["python3","-m","userbot"]
