#include <stdlib.h>
#include <stdio.h>

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include "rs232.h"
typedef unsigned char BYTE;

int laser_off(int laser_number, int cport_nr){
    if (laser_number > 3 || laser_number < 1){
        printf("check laser number\n");
        return -1;
    }
    else{
        if (laser_number == 1){
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x04, 0x00, 0x00, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }else if (laser_number == 2){
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x05, 0x00, 0x00, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }else{
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x06, 0x00, 0x00, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }
        return 0;
    }
}

int main(int argc, char *argv[]){
    if (argc == 4){
        int cport_nr = atoi(argv[1]);   /* /dev/ttyS0 (COM1 on windows) */
        int bdrate = atoi(argv[2]);     /* 9600 baud */
        int laser_number = atoi(argv[3]);
        char mode[]={'8','N','1',0};

        if(RS232_OpenComport(cport_nr, bdrate, mode, 0)){
            printf("Can not open comport\n");
            return -1;
        }
        int return_value = laser_off(laser_number, cport_nr);
        return return_value;
    }else{
        return -1;
    }
}