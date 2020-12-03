# Using Groovy
FROM biansepang/weebproject:groovy

# Clone repo and prepare working directory
RUN git clone -b master https://github.com/darulmuhibin/WeebProject /home/weebproject/
RUN mkdir /home/weebproject/bin/
WORKDIR /home/weebproject/

# Finalization
CMD ["python3","-m","userbot"]
