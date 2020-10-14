#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#endif

#include "rs232.h"
typedef unsigned char BYTE;

int laser_on(int cport_nr) {
    BYTE send_1[7] = { 0x55, 0xaa, 0x05, 0x04, 0x00, 0x01, 0x00 };
    send_1[6] = send_1[2] + send_1[3] + send_1[4] + send_1[5];
    RS232_SendBuf(cport_nr, send_1, 7);
    Sleep(1000);

    BYTE send_2[7] = { 0x55, 0xaa, 0x05, 0x05, 0x00, 0x01, 0x00 };
    send_2[6] = send_2[2] + send_2[3] + send_2[4] + send_2[5];
    RS232_SendBuf(cport_nr, send_2, 7);
    Sleep(1000);

    BYTE send_3[7] = { 0x55, 0xaa, 0x05, 0x06, 0x00, 0x01, 0x00 };
    send_3[6] = send_3[2] + send_3[3] + send_3[4] + send_3[5];
    RS232_SendBuf(cport_nr, send_3, 7);
    Sleep(1000);

    return 0;
}

int laser_off(int cport_nr) {
    
    BYTE send_1[7] = { 0x55, 0xaa, 0x05, 0x04, 0x00, 0x00, 0x00 };
    send_1[6] = send_1[2] + send_1[3] + send_1[4] + send_1[5];
    RS232_SendBuf(cport_nr, send_1, 7);
    Sleep(1000);

    BYTE send_2[7] = { 0x55, 0xaa, 0x05, 0x05, 0x00, 0x00, 0x00 };
    send_2[6] = send_2[2] + send_2[3] + send_2[4] + send_2[5];
    RS232_SendBuf(cport_nr, send_2, 7);
    Sleep(1000);

    BYTE send_3[7] = { 0x55, 0xaa, 0x05, 0x06, 0x00, 0x00, 0x00 };
    send_3[6] = send_3[2] + send_3[3] + send_3[4] + send_3[5];
    RS232_SendBuf(cport_nr, send_3, 7);
    Sleep(1000);

    return 0;
}

int laser_power_change(int laser_power1, int laser_power2, int laser_power3, int cport_nr) {
    if (laser_power1 > 100 || laser_power1 < 0) {
        printf("check laser power\n");
        return -1;
    }
    else if (laser_power2 > 100 || laser_power2 < 0) {
        printf("check laser power\n");
        return -1;
    }
    else if (laser_power3 > 100 || laser_power3 < 0) {
        printf("check laser power\n");
        return -1;
    }
    else {
        BYTE send_1[7] = { 0x55, 0xaa, 0x05, 0x00, 0x00, 0x00, 0x00};
        send_1[4] = 0x00;
        send_1[5] = (BYTE)laser_power1;
        send_1[6] = send_1[2] + send_1[3] + send_1[4] + send_1[5];
        RS232_SendBuf(cport_nr, send_1, 7);
        Sleep(1000);

        BYTE send_2[7] = { 0x55, 0xaa, 0x05, 0x01, 0x00, 0x00, 0x00 };
        send_2[4] = 0x00;
        send_2[5] = (BYTE)laser_power2;
        send_2[6] = send_2[2] + send_2[3] + send_2[4] + send_2[5];
        RS232_SendBuf(cport_nr, send_2, 7);
        Sleep(1000);

        BYTE send_3[7] = { 0x55, 0xaa, 0x05, 0x02, 0x00, 0x00, 0x00 };
        send_3[4] = 0x00;
        send_3[5] = (BYTE)laser_power3;
        send_3[6] = send_3[2] + send_3[3] + send_3[4] + send_3[5];
        RS232_SendBuf(cport_nr, send_3, 7);
        Sleep(1000);

        return 0;
    }
}

int main(int argc, char *argv[]){
    if (argc == 6) {
        int cport_nr = atoi(argv[1]);   
        int bdrate = atoi(argv[2]); 
        int laser1_power = atoi(argv[3]);
        int laser2_power = atoi(argv[4]);
        int laser3_power = atoi(argv[5]);
        
        char mode[] = { '8','N','1', 0 };
        printf("Try to connect laser\n");
        if (RS232_OpenComport(cport_nr, bdrate, mode, 0)) {
            printf("Can not open comport\n");
            return -1;
        }
        printf("Success to connect laser\n");
        
        laser_off(cport_nr);
        laser_on(cport_nr);
        laser_power_change(laser1_power, laser2_power, laser3_power, cport_nr);
        return 0;
    }
    else {
        return -1;
    }
}