# Using Groovy
FROM biansepang/weebproject:groovy

# Clone repo and prepare working directory
RUN git clone -b master https://github.com/BianSepang/WeebProject /home/weebproject/
RUN mkdir /home/weebproject/bin/
WORKDIR /home/weebproject/

# Make open port TCP
EXPOSE 80 443

# Finalization
CMD ["python3","-m","userbot"]
