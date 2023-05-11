# nRF 52840 DONGLE SETUP GUIDE

## Purpose
In Ioter, OpenThread RCP is used to connect to Thread network. Therefore, it needs to insert Thread RCP firmware into the nrf52840 dongle that will be used.

## Guide to create nRF 52840 OpenThread RCP dongle
If you don't know how to insert the firmware into the dongle, this guide is helpful.
1. install 'nRF Connect for Desktop' in Window PC from [Nordic Semiconductor site](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop/Download?lang=en#infotabs)
2. execute 'nRF Connect for Desktop' 
3. install and open 'Programmer'   
![nrf_connect_for_desktop](https://github.com/Samsung/ioter/assets/110587319/fcc7e468-d4e2-4934-8b6d-4f1afddf8b6b)
5. in 'SELECT DEVICE', select the inserted nrf52840 dongle   
![download_mode](https://github.com/Samsung/ioter/assets/110587319/37977049-9d7f-4ea9-8528-30441ad2d03b)   
   > **Enter donwload mode: please press the button in red-box of upper dongle image before select device after insert a dongle*
5. in 'Add file', select RCP firmware file [ot-rcp-18b6f94.hex (RCP version 6)](ot-rcp-18b6f94.hex)
6. after then, select 'Write'   
![programmer](https://github.com/Samsung/ioter/assets/110587319/267079af-3ed9-4d26-8256-38c7b58ee55c)

7. OpenThread RCP dongle creation complete!