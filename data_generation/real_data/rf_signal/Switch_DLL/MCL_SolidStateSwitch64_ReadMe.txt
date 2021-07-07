MCL_SolidStateSwitch64.dll - 64 bit COM Object for programmers under 64 bit MS operating system

This DLL file can be used by programmers of Visual Basic,VC++,Delphi,C#
LabView or any other program that recognize 64 bit ActiveX COM DLL file.

USBDigitalSWitch64.dll file should be referenced to the program project.

The DLL file include the following Functions:

1.a int Connect(Optional *string SN)  :

SN parameter is needed in case of using more than 1 Switch Box.
SN is the Serial Number of the Switch Box and can be ignored if using only one box.

1.b int ConnectByAddress(Optional short Address)  :

Address parameter is needed if more than 1 Switch Box are connected to PC.
and you want to connect to device by Address instead of SN.
This is an alternative to option 1.a (connect by SN).

Address parameter is the Address of the Switch Box.
The address can be any integer number between 1 to 255 and can be changed by software.


2. void Disconnect()

Recommanded to Disconnect the device while end of program

3. Int GetSwitchesStatus(int StatusRet)     - StatusRet Return  with the switches status port

StatusRet - returned parameter represent the status for each switch in the box.
the LSB bit represent switch "A" then "B" etc...
for example: if StatusRet=12 ( B00001100 ) - Switch C and D are energized. all others DE-Energized.


4. int Read_ModelName(string ModelName) As Integer
The Model Name returned in ModelName parameter.

5. int Read_SN(string SN ) 
The Serial Number returned in SN parameter.




7. int Set_SP4T_COM_To( byte p )

   p should be a value between 1 to 4.
   this function set the Com to 1,2,3 ro 4 port.
   
   return 1 for success or 0 for software failure     

8. int Get_SP4T_State()
   
   this function return which port connect to Com (1-4).

   

   
9. int Set_Address(Address As Integer)   
   
   set the address of the unit. the address can be any number between 1 to 255.
   return positive number if success.
   
10. int Get_Address() 

   return the device address.
   if fail - return 0.
   
11. Int Get_Available_SN_List(string SN_List)

string SN_List is returned with all avaliable Switch Boxes connected to USB.
the function return the Number of Switch Boxes.

12. Int Get_Available_Address_List(string Add_List)

string Add_List is returned with all avaliable Switch Boxes connected to USB.
the function return the Number of Switch Boxes.   
   


    
13. GetFirmware- return the firmware of the Switch Controller.

14. GetUSBConnectionStatus - return the USB Connection Status.


     
          
15. int Send_SCPI(String SndSTR , String RetSTR)

 function recieve a SndSTR as parameter and return an "Answer" to
RetSTR. thid function return 1 for success and 0 for fail.

	


program Example in VB:

Dim sw As New USBDigitalSWitch64.USB_Digital_Switch,Status as integer
Status=sw.Connect
Status = sw.Set_SP4T_COM_To(3)
sw.Disconnect

 

program Example in Visual C++:

USBDigitalSWitch64::USB_Digital_Switch ^sw = gcnew USBDigitalSWitch64::USB_Digital_Switch();
short Status = 0;
System::String ^SN = "";
float ReadResult = 0;
Status = sw->Connect(SN);
Statuse=sw->Set_SP4T_COM_To(3)
sw->Disconnect();



      