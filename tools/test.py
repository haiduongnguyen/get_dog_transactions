
from time import sleep
import logging


if __name__ == '__main__':
    print("Start program")
    logging.info("Start")
    for i in range(10):
        print(i)
        logging.info(i)
    logging.info("end")
    sleep(3000)
    
    
    
    
    
    
    