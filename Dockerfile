FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:dd8f-main

RUN apt-get update -y && \
    apt-get install -y software-properties-common && \
    apt-get install -y wget lftp sshpass

# The following lines are needed to ensure your build environement works
# correctly with latch.
RUN python3 -m pip install --upgrade latch
COPY wf /root/wf
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
WORKDIR /root

