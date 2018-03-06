import socket
import signal

from translation_client import translation_client

DEFAULT_SRC_LANG = u'en'
DEFAULT_TARGET_LANG = u'es'
DEFAULT_BIND_HOST = 'localhost'
DEFAULT_BIND_PORT = 8090
DEFAULT_MAX_QUEUED_CONN = 1
DEFAULT_ACCEPT_TIMEOUT = 0.5
DEFAULT_RECV_TIMEOUT = 1.0


def sigint_handler(signal, frame):
    global serve_request
    serve_request = False


class TranslationHub(object):
    @staticmethod
    def serve_forever(service_username, 
                        service_password, 
                        service_base_endpoint=None, 
                        src_lang=DEFAULT_SRC_LANG, 
                        target_lang=DEFAULT_TARGET_LANG, 
                        bind_host=DEFAULT_BIND_HOST, 
                        bind_port=DEFAULT_BIND_PORT, 
                        max_queued_conn=DEFAULT_MAX_QUEUED_CONN, 
                        accept_timeout=DEFAULT_ACCEPT_TIMEOUT,
                        recv_timeout=DEFAULT_RECV_TIMEOUT):
        
        assert isinstance(service_username, unicode)
        assert isinstance(service_password, unicode)
        assert isinstance(src_lang, unicode)
        assert isinstance(target_lang, unicode)
        
        tc = translation_client.TranslationClient(
            service_username, 
            service_password, 
            *((service_base_endpoint, ) if service_base_endpoint is not None else ())
        )
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((bind_host, bind_port))
        s.listen(max_queued_conn)
        s.settimeout(accept_timeout)
        
        uuid = None
        
        global serve_request
        serve_request = True
        signal.signal(signal.SIGINT, sigint_handler)

        print 'Entering main loop...'
        
        while serve_request:
            try:
                conn, addr = s.accept()
            except socket.timeout:
                if uuid is not None:
                    result = tc.poll(uuid)
                    
                    if result is not None:
                        uuid = None
                        conn.sendall(result.encode('utf-8'))
                        
                        try:
                            conn.close()
                        except socket.error:
                            pass
            else:
                if uuid is not None:
                    tc.cancel()
                    uuid = None
                
                conn.settimeout(recv_timeout)
                
                string = ''
                
                while not string.endswith('\0'):
                    try:
                        substring = conn.recv(4096)
                    except socket.timeout:
                        break
                    
                    if not substring:
                        break
                    
                    string += substring
                else:
                    uuid = tc.translate(string[: -1].decode('utf-8'), src_lang, target_lang)
                    continue
                
                try:
                    conn.close()
                except socket.error:
                    pass
            
        print 'Finished main loop'
