# mimosa-machine
A machine that is controlled with an Ikea Trådfri remote for making mimosas.
Built with Raspberry Pi, Zigbee, MQTT.

Requirements:
- Mosquitto 
- Zigbee2mqtt
- Paho server client 

Setup:
    general:
        - sudo apt-get update

    Mosquitto:
        - apt-get install mosquitto

    Zigbee2mqtt:
        - Connect CC2531 dongle
        - check that ls -l /dev/ttyACM0 exists (means that CC2531 is found as device)
        install Node.js:
            - sudo curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
            - sudo apt-get install -y nodejs git make g++ gcc
        check nodejs and npm versions (atleast v10.x and v6.x)
            - node --version
            - npm --version
        install Zigbee2mqtt
            - sudo git clone https://github.com/Koenkk/zigbee2mqtt.git /opt/zigbee2mqtt
            - sudo chown -R pi:pi /opt/zigbee2mqtt
            - cd /opt/zigbee2mqtt
            - npm install
        add the port number and network_key (if needed) to configuration.yaml:
            - sudo nano /opt/zigbee2mqtt/data/configuration.yaml
            - write: 
                server: 'mqtt://localhost:1883'
                advanced:
                    network_key: [1, 3, 5, 7, 9, 11, 13, 15, 0, 2, 4, 6, 8, 10, 12, 13]
        run it as a daemon:
            - sudo nano /etc/systemd/system/zigbee2mqtt.service
            - write: 
                [Unit]
                Description=zigbee2mqtt
                After=network.target

                [Service]
                ExecStart=/usr/bin/npm start
                WorkingDirectory=/opt/zigbee2mqtt
                StandardOutput=inherit
                StandardError=inherit
                Restart=always
                User=pi

                [Install]
                WantedBy=multi-user.target
            - save and exist
        test:
            sudo systemctl start zigbee2mqtt
            sudo journalctl -u zigbee2mqtt.service -f
        exit:
            sudo systemctl stop zigbee2mqtt
        more in the source:
            https://www.zigbee2mqtt.io/getting_started/running_zigbee2mqtt.html

    Paho:
        - pip3 install paho-mqtt

    - Run zigbee2mqtt and connect wanted devices
    - When devices are found stop the mqtt-server and modify configuration.yaml
    - Change "permit_join" to false
    - You can change the device names in "friendly_name:"
    more in the source:
        https://www.zigbee2mqtt.io/information/configuration.html

    - Upload the server.py to the rasbian
    - Check that in server.py:
        - the host and port are the same than in the configuration.yaml
        - the subscribed device names matches to the configuration.yaml's devices friendly_names
    - start zigbee2mqtt server
    - run the code:
        - python3 server.py

