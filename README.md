# Internet Time Machine on Raspberry Pi

Bring your vintage computers online with archived websites from the past! This project sets up a Raspberry Pi as a transparent HTTP proxy that serves historical pages from the Wayback Machine automatically, using just an Ethernet connection—no setup needed on the client side.

---

##  Features

- Transparent HTTP proxy via [WaybackProxy](https://github.com/richardg867/WaybackProxy)
- Automatically intercepts and time-travels HTTP requests
- Rotary encoder lets you change the browsing date
- DHCP + DNS redirection using `dnsmasq`
- Real-time clock keeps time across reboots
- OLED display (optional) shows the active date

---

## Hardware Requirements

- Raspberry Pi 4 or later (2 NICs recommended: built-in + USB Ethernet)
- Rotary encoder (e.g., KY-040)
- OLED display (SSD1306 or SH1106, optional)
- Real-Time Clock module (e.g., DS3231)
- Retro computer with Ethernet

---

## Software Setup

### 1. Install dependencies

```bash
sudo apt update && sudo apt install -y dnsmasq iptables python3 python3-pip git
pip3 install flask requests
```

### 2. Clone WaybackProxy

```bash
git clone https://github.com/richardg867/WaybackProxy.git
cd WaybackProxy
```

Edit `config.json` to set the initial date and mode:

```json
{
  "DATE": "20030601",
  "TOLERANCE": 60,
  "MODE": "transparent"
}
```

Run the proxy on port 80:

```bash
sudo python3 waybackproxy.py
```

### 3. Enable IP forwarding

```bash
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

Add to `/etc/sysctl.conf`:

```
net.ipv4.ip_forward=1
```

### 4. Set up iptables (replace `eth1` and `eth0` with your interfaces)

```bash
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo iptables -t nat -A PREROUTING -i eth1 -p tcp --dport 80 -j REDIRECT --to-port 80
```

To make persistent:

```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
```

### 5. Configure dnsmasq

Edit `/etc/dnsmasq.conf`:

```conf
interface=eth1
dhcp-range=192.168.2.2,192.168.2.254,12h
address=/#/192.168.2.1
```

Restart dnsmasq:

```bash
sudo systemctl restart dnsmasq
```

---

##  Rotary Encoder (Optional Date Control)

Use a Python script with `RPi.GPIO` or `gpiozero` to read encoder position and update the `config.json` date. You can then restart the proxy to apply changes.

---

##  Testing

1. Connect retro computer via Ethernet to Pi's `eth1`
2. Power on Pi and retro machine
3. Open a browser and try `http://google.com` or other HTTP sites
4. The Pi will serve archived versions closest to the selected date

---

## HTTPS Notice

This setup transparently supports **HTTP only**. HTTPS requests cannot be intercepted without breaking encryption. Stick to HTTP-capable sites or archived pages with HTTP fallback.

---

## Future Improvements

- Use OLED display to show selected date
- Add hardware buttons to jump to preset years
- Implement modem emulation for dial-up retro gear

---

## Credits

- [WaybackProxy](https://github.com/richardg867/WaybackProxy) by RichardG867
- Inspiration: [I Made an Internet Time Machine](https://www.youtube.com/watch?v=0OB1g8CUdbA)
- Chatgpt
---

Happy time traveling! 

