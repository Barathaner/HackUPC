import download_util
import time

download_util.download_batch(0,5)
#process the images 
print("start processing.....")
time.sleep(1)
print("finished processing")
download_util.delete_img_folder()