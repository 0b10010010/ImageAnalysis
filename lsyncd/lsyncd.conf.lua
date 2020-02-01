settings {
    logfile = "/var/log/lsyncd/lsyncd.log",
    statusFile = "/var/log/lsyncd/lsyncd.status"
}

sync {
    default.rsync,
    source="/home/odroid/Desktop/Capture#1",
    target="spykat@192.168.15.102:/home/spykat/Desktop/imgTargetDir",
    delay = 2,
    rsync = {
        archive = true,
        compress = true
    }
}
