#include <stdlib.h>
#include <stdio.h>

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include "rs232.h"
typedef unsigned char BYTE;

int laser_on(int laser_number, int cport_nr){
    if (laser_number > 3 || laser_number < 1){
        printf("check laser number\n");
        return 0;
    }
    else{
        if (laser_number == 1){
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x04, 0x00, 0x01, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }else if (laser_number == 2){
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x05, 0x00, 0x01, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }else{
            BYTE send[7] = {0x55, 0xaa, 0x05, 0x06, 0x00, 0x01, 0x00};
        	send[6] = send[2] + send[3] + send[4] + send[5];
        	char str[(sizeof send) + 1];
            memcpy(str, send, sizeof send);
            str[sizeof send] = 0;
            RS232_cputs(cport_nr, str);
        }
        return 1;
    }
}

int laser_off(int laser_number, int cport_nr){
    if (laser_number > 3 || laser_number < 1){
        printf("check laser number\n");
        return 0;
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
        return 1;
    }
}

int laser_power_change(int laser_number, int laser_power, int cport_nr){
    if (laser_number > 3 || laser_number < 1){
        printf("check laser number\n");
        return 0;
    }
    else{
        if (laser_power > 100 || laser_power < 0){
           printf("check laser power\n");
           return 0;
        }else{
            if(laser_number == 1){
                BYTE send[7] = {0x55, 0xaa, 0x05, 0x00, 0x00, 0x00, 0x00};
                send[4] = 0x00;
                send[5] = (BYTE)laser_power;
                send[6] = send[3] + send[4] +send[5];
                char str[(sizeof send) + 1];
                memcpy(str, send, sizeof send);
                str[sizeof send] = 0;
                RS232_cputs(cport_nr, str);
            }else if(laser_number == 2){
                BYTE send[7] = {0x55, 0xaa, 0x05, 0x01, 0x00, 0x00, 0x00};
                send[4] = 0x00;
                send[5] = (BYTE)laser_power;
                send[6] = send[3] + send[4] +send[5];
                char str[(sizeof send) + 1];
                memcpy(str, send, sizeof send);
                str[sizeof send] = 0;
                RS232_cputs(cport_nr, str);
            }else{
                BYTE send[7] = {0x55, 0xaa, 0x05, 0x02, 0x00, 0x00, 0x00};
                send[4] = 0x00;
                send[5] = (BYTE)laser_power;
                send[6] = send[3] + send[4] +send[5];
                char str[(sizeof send) + 1];
                memcpy(str, send, sizeof send);
                str[sizeof send] = 0;
                RS232_cputs(cport_nr, str);
            }
            return 1;
        }
    }
}


int main(){
    int cport_nr= 0;    /* /dev/ttyS0 (COM1 on windows) */
    int bdrate = 9600;  /* 9600 baud */

    char mode[]={'8','N','1',0};

    if(RS232_OpenComport(cport_nr, bdrate, mode, 0)){
        printf("Can not open comport\n");
        return(0);
    }

    return 0;
}