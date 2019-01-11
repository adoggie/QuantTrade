docker run --name kungfu -v /home/scott/kf:/home/kf --privileged --ulimit memlock=-1 --net=host -td taurusai/kungfu-devel /usr/sbin/init
