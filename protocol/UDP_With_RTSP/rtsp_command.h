#ifndef _RTSP_COMMAND_H_
#define _RTSP_COMMAND_H_ 

#ifdef __cplusplus
extern "C" 
{
#endif

typedef struct rtsp_command_t {
  char *accept;
  char *authorization;
  char *range;
  char *session;
  char *transport;
  char *x_RegionID;
  char *x_Info;
  int serviceGroupID;
  int scale; 
  int speed;
}rtsp_command_t;

/*----------------------------------------------------------
	cmd_nameΪrtsp������, ��setup, play, option��
	cmdΪrtsp������������ֶ�, ����Ҫ���͵����ݸ���ֵ
	track_name����setupʱָ��track
	buffer�����뱣֤�㹻��	
----------------------------------------------------------*/
int rtsp_send_cmd (const char *cmd_name, rtsp_client_t *client, rtsp_command_t *cmd, const char* track_name);


#ifdef __cplusplus
}
#endif

#endif

