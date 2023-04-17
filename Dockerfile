FROM test-jupyter-lab:latest
COPY /mnt/c/Users/ferbs/Documents/Programing_Projects/MineSweeper /root/home/git
WORKDIR /root/home/git

COPY requirements.txt /root/home/git
RUN apt-get update
RUN apt install python3-tk


RUN apt install -y git
RUN pip install -r requirements.txt



EXPOSE 8888