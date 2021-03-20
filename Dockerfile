# Using Python Slim-Buster
FROM biansepang/weebproject:buster

# Clone repo and prepare working directory
RUN git clone -b master https://github.com/BianSepang/WeebProject /home/weebproject/ \
    && chmod 777 /home/weebproject \
    && mkdir /home/weebproject/bin/

WORKDIR /home/weebproject/

# Finalization
CMD ["python3","-m","userbot"]
