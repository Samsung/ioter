# nRF 52840 DONGLE SETUP GUIDE

In ioter, OpenThread RCP is used to connect to the Thread network. Therefore, Thread RCP firmware must be loaded into the nRF52840 dongle that will be used. This guide will help you load the appropriate firmware onto your dongle.

## Create your nRF 52840 OpenThread RCP dongle
1. Install 'nRF Connect for Desktop' onto a Windows PC from the [Nordic Semiconductor site](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop/Download?lang=en#infotabs).
2. Launch 'nRF Connect for Desktop'.
3. Install and open 'Programmer' from within 'nRF Connect for Desktop'.
![nrf_connect_for_desktop](https://github.com/Samsung/ioter/assets/110587319/fcc7e468-d4e2-4934-8b6d-4f1afddf8b6b)
4. After inserting the dongle, put the nRF52840 dongle into download mode by pressing the button indicated by the red box in the image below.
![download_mode](https://github.com/Samsung/ioter/assets/110587319/37977049-9d7f-4ea9-8528-30441ad2d03b)
5. Click 'SELECT DEVICE' and select the inserted nRF52840 dongle.
6. Click 'Add file' and select the RCP firmware file [ot-rcp-18b6f94.hex (RCP version 6)](ot-rcp-18b6f94.hex).
7. Select 'Write'.
![programmer](https://github.com/Samsung/ioter/assets/110587319/267079af-3ed9-4d26-8256-38c7b58ee55c)

Your OpenThread RCP dongle creation is now complete!
