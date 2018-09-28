# sftp-demo-paramiko
SFTP Demo using user key access, based on Paramiko's demo. ProFTPD 

From https://github.com/paramiko/paramiko/tree/master/demos
which didn't work, as line 126 needed "wb".

Anyway, ProFTPd didn't support GSSAPI, so my version uses the conventional SSH Keys.

ProFTPd's sftp.conf

    <IfModule mod_sftp.c>
    SFTPEngine on
    Port 2222
    SFTPLog /var/log/proftpd/sftp.log

    # Configure both the RSA and DSA host keys, using the same host key
    # files that OpenSSH uses.
    SFTPHostKey /etc/ssh/ssh_host_rsa_key
    SFTPHostKey /etc/ssh/ssh_host_dsa_key
    SFTPAuthMethods publickey
    
    #Need to be an RFC4716 formatted key, using ssh-keygen -e -f /home/<user>/.ssh/id_rsa.pub
    #Hence storing in a separate file from OpenSSH ones
    SFTPAuthorizedUserKeys file:~/.ssh/proftpd_authorized_keys

    # Enable compression
    SFTPCompression delayed
    AllowChrootSymlinks off
    </IfModule>

end
