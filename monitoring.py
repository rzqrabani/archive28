import pandas as pd
import serial
import time
import speedtest

def read_hwinfo_data():
    start_time = time.time()
    # Baca file CSV dengan encoding yang sesuai
    df = pd.read_csv(r'D:\esp32\monitoring.csv', encoding='ISO-8859-1')

    # Nama kolom sesuai dengan data CSV yang diberikan
    cpu_temp = df['CPU Package [°C]'].iloc[-1]  # Mengambil suhu CPU
    cpu_usage = df['Total CPU Usage [%]'].iloc[-1]  # Mengambil penggunaan CPU
    gpu_temp = df['GPU Temperature [°C]'].iloc[-1]  # Mengambil suhu GPU
    gpu_usage = df['GPU Core Load [%]'].iloc[-1]  # Mengambil penggunaan GPU
    ram_usage = df['Physical Memory Load [%]'].iloc[-1]  # Mengambil penggunaan RAM

    print(f"Data read time: {time.time() - start_time:.2f} seconds")
    return cpu_temp, cpu_usage, gpu_temp, gpu_usage, ram_usage

def get_download_speed():
    start_time = time.time()
    # Mengukur kecepatan download menggunakan speedtest-cli
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Konversi ke Mbps
    print(f"Speedtest time: {time.time() - start_time:.2f} seconds")
    return round(download_speed, 2)

def format_data(cpu_temp, cpu_usage, gpu_temp, gpu_usage, ram_usage, download_speed, display_mode):
    
    width = 16

    if display_mode == "cpu_gpu":
        cpu_usage_text = f"CPU: {cpu_temp}C {cpu_usage}%".ljust(width)
        gpu_usage_text = f"GPU: {gpu_temp}C {gpu_usage}%".ljust(width)
        return cpu_usage_text, gpu_usage_text

    elif display_mode == "ram_net":
        ram_line = f"RAM: {ram_usage}%".ljust(width)
        net_line = f"NET: {download_speed} Mbps".ljust(width)
        return ram_line, net_line

def send_data_to_esp32():
    # Koneksi ke ESP32 via serial dengan baud rate 9600
    esp32_port = 'COM3'  # Sesuaikan dengan port COM yang Anda gunakan
    baud_rate = 9600  # Ubah baud rate ke 9600
    ser = serial.Serial(esp32_port, baud_rate, timeout=1)

    # Initialisasi waktu untuk perhitungan
    last_update_time = time.time()
    display_mode = "cpu_gpu"

    try:
        while True:
            current_time = time.time()
            
            # Update data setiap 3 detik
            if current_time - last_update_time >= 3:
                # Update data
                start_time = time.time()
                cpu_temp, cpu_usage, gpu_temp, gpu_usage, ram_usage = read_hwinfo_data()
                download_speed = get_download_speed()

                # Format data untuk LCD
                line1, line2 = format_data(cpu_temp, cpu_usage, gpu_temp, gpu_usage, ram_usage, download_speed, display_mode)

                # Kirimkan data ke ESP32
                send_start_time = time.time()
                ser.write((line1 + '\n').encode())
                ser.write((line2 + '\n').encode())
                send_duration = time.time() - send_start_time

                print(line1)
                print(line2)
                print(f"Data send duration: {send_duration:.2f} seconds")

                # Reset timer dan ganti mode tampilan
                last_update_time = current_time
                display_mode = "ram_net" if display_mode == "cpu_gpu" else "cpu_gpu"
            
            # Tambahkan delay kecil untuk menghindari penggunaan CPU berlebih
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Pengiriman data dihentikan.")
    finally:
        ser.close()

if __name__ == "__main__":
    send_data_to_esp32()
