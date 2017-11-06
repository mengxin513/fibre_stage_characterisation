import time

start = time.time()

while time.time() - start < 100:
    time.sleep(2)
    print time.time()-start
    